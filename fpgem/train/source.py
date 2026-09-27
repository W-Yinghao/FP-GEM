"""W1 unit: leave-one-subject-out source training + complete per-trial dumps.

A unit is `<dataset>-<labelset>-<backbone>-t<target>-s<seed>`, e.g. `B14-c4-tsmnet-t01-s0`.
Target data (signals or labels) never enters training or model selection; target rows are only
forwarded through the frozen, selected model when the dumps are written.
"""
from __future__ import annotations

import copy
import os
import platform
import socket
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F
import yaml

from .. import data as D
from .. import models as M
from ..paths import REPO, cache_dir, unit_dir
from ..provenance import ProvenanceError, code_sig, git_sha, require_clean_git, sha256_file, write_json
from ..vendor.spdnets import batchnorm as spdbn

BACKBONE_OF = {"tsmnet": "tsmnet", "eegnet": "eegnet", "chambon": "chambon"}


# ------------------------------------------------------------------ unit ids
@dataclass(frozen=True)
class Unit:
    ds: str
    label_set: str
    backbone: str
    target: int
    seed: int

    @property
    def uid(self) -> str:
        return f"{self.ds}-{self.label_set}-{self.backbone}-t{self.target:02d}-s{self.seed}"

    @staticmethod
    def parse(uid: str) -> "Unit":
        ds, ls, bb, t, s = uid.split("-")
        if not (t.startswith("t") and s.startswith("s")):
            raise ValueError(uid)
        return Unit(ds, ls, bb, int(t[1:]), int(s[1:]))


def load_cfg(path: Path | None = None) -> dict:
    with open(path or REPO / "configs" / "w1.yaml") as f:
        return yaml.safe_load(f)


def enumerate_units(cfg: dict) -> list[Unit]:
    units = []
    for ds, spec in cfg["datasets"].items():
        for ls in spec["label_sets"]:
            for bb, bspec in cfg["backbones"].items():
                if ds not in bspec["applies_to"]:
                    continue
                for t in D.target_subjects(ds):
                    for s in cfg["seeds"]:
                        units.append(Unit(ds, ls, bb, int(t), int(s)))
    return units


# ------------------------------------------------------------------ determinism
def set_determinism(seed: int, threads: int) -> None:
    import random
    if os.environ.get("CUBLAS_WORKSPACE_CONFIG") not in (":4096:8", ":16:8"):
        raise RuntimeError("CUBLAS_WORKSPACE_CONFIG must be set before CUDA initialises")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(threads)


# ------------------------------------------------------------------ split
def make_split(ds: str, target: int, seed: int, val_frac: float) -> dict:
    subs = D.all_subjects(ds)
    if target not in D.target_subjects(ds):
        raise ValueError(f"{target} is not a valid {ds} target")
    src = [s for s in subs if s != target]
    rng = np.random.default_rng([seed, target])
    n_val = max(1, int(round(val_frac * len(src))))
    val = sorted(int(v) for v in rng.choice(src, n_val, replace=False))
    train = [s for s in src if s not in val]
    assert target not in train and target not in val and not set(train) & set(val)
    return dict(target=target, train=train, val=val, roles=D.SESSION_ROLES[ds])


def improves(vb: float, vl: float, best: tuple) -> bool:
    """Appendum A1 selection rule: higher validation bAcc wins; ties are broken by lower validation loss."""
    return vb > best[0] or (vb == best[0] and vl < best[1])


def select_epoch(hist: list) -> int:
    best, ep = (-np.inf, np.inf), -1
    for h in hist:
        if improves(h["val_bacc"], h["val_loss"], best):
            best, ep = (h["val_bacc"], h["val_loss"]), h["epoch"]
    return ep


def balanced_accuracy(y: np.ndarray, pred: np.ndarray, n_classes: int) -> float:
    rec = [np.mean(pred[y == k] == k) for k in range(n_classes) if np.any(y == k)]
    return float(np.mean(rec))


# ------------------------------------------------------------------ TSMNet
def domain_batches(dom: np.ndarray, y: np.ndarray, per_domain: int, domains_per_batch: int,
                   rng: np.random.Generator) -> list[np.ndarray]:
    """Deterministic re-implementation of TSMNet's StratifiedDomainSampler: each batch holds
    `domains_per_batch` distinct domains × `per_domain` class-interleaved trials."""
    chunks = {}
    for d in np.unique(dom):
        idx = np.flatnonzero(dom == d)
        per_cls = [rng.permutation(idx[y[idx] == k]) for k in np.unique(y[idx])]
        order = [rng.permutation(len(per_cls))]
        inter = []
        for j in range(max(len(p) for p in per_cls)):
            for c in order[0]:
                if j < len(per_cls[c]):
                    inter.append(per_cls[c][j])
        inter = np.array(inter)
        n = len(inter) // per_domain
        chunks[d] = [inter[i * per_domain:(i + 1) * per_domain] for i in range(n)]
    batches = []
    while True:
        avail = [d for d, c in chunks.items() if c]
        if len(avail) < domains_per_batch:
            break
        pick = rng.choice(avail, domains_per_batch, replace=False)
        batches.append(np.concatenate([chunks[d].pop() for d in pick]))
    return batches


def tsmnet_val(model, X, y, dom, device, K) -> tuple[float, float]:
    model.eval()
    S = M.tsmnet_prebn(model, X, device, groups=dom // 10)
    d = torch.as_tensor(dom)
    for du in np.unique(dom):
        M.tsmnet_refit_domain(model, S[d == int(du)], int(du))
    _, logits = M.tsmnet_head(model, S, d)
    loss = F.cross_entropy(logits, torch.as_tensor(y)).item()
    return loss, balanced_accuracy(y, logits.argmax(1).numpy(), K)


def train_tsmnet(u: Unit, cfg: dict, data: dict, masks: dict, device, log) -> tuple:
    import geoopt
    bcfg = cfg["backbones"]["tsmnet"]
    tcfg = cfg["training"]
    K = len(data["classes"])
    X, y = data["X"], data["y"]
    sess = D.session_index(u.ds, data["session"])
    dom = data["subject"] * 10 + sess
    all_domains = [s * 10 + k for s in D.all_subjects(u.ds) for k in (0, 1)]
    model = M.build_tsmnet(K, X.shape[1], X.shape[2], all_domains, device, bcfg)
    nodecay = [p for n, p in model.named_parameters() if n.startswith("spdnet.") or n.endswith(".mean")]
    decay = [p for n, p in model.named_parameters() if not (n.startswith("spdnet.") or n.endswith(".mean"))]
    opt = geoopt.optim.RiemannianAdam([dict(params=decay, weight_decay=bcfg["optimizer"]["weight_decay"]),
                                       dict(params=nodecay, weight_decay=0.0)], lr=bcfg["optimizer"]["lr"])
    per, dpb = bcfg["batch"]["per_domain"], bcfg["batch"]["domains_per_batch"]
    sched = spdbn.MomentumBatchNormScheduler(epochs=tcfg["max_epochs"] - bcfg["bn_momentum_scheduler"]["epochs_offset"],
                                             bs=per, bs0=per * dpb, tau0=bcfg["bn_momentum_scheduler"]["tau0"])
    sched.initialize()
    sched.on_train_begin(SimpleNamespace(module_=model))
    tr, va = masks["train"], masks["val"]
    Xtr, ytr, dtr = X[tr], y[tr], dom[tr]
    rng = np.random.default_rng([u.seed, u.target, 17])
    hist, best, best_key, bad = [], None, (-np.inf, np.inf), 0
    for ep in range(tcfg["max_epochs"]):
        sched.on_epoch_begin(None)
        model.train()
        t0, tl, nb = time.time(), 0.0, 0
        for bidx in domain_batches(dtr, ytr, per, dpb, rng):
            xb = torch.as_tensor(Xtr[bidx], dtype=torch.float32, device=device)
            logits, _ = model(xb, torch.as_tensor(dtr[bidx]))
            loss = F.cross_entropy(logits, torch.as_tensor(ytr[bidx]))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            tl += loss.item()
            nb += 1
        vl, vb = tsmnet_val(model, X[va], y[va], dom[va], device, K)
        hist.append(dict(epoch=ep, train_loss=tl / max(nb, 1), val_loss=vl, val_bacc=vb, sec=time.time() - t0))
        log(f"ep {ep:3d} train {tl / max(nb, 1):.4f} val {vl:.4f} bacc {vb:.3f} ({time.time() - t0:.1f}s)")
        if improves(vb, vl, best_key):
            best_key, best, bad = (vb, vl), copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
        if bad >= tcfg["patience"] and ep + 1 >= tcfg["min_epochs"]:
            break
    model.load_state_dict(best)
    spec = dict(kind="tsmnet", n_classes=K, n_chans=X.shape[1], n_times=X.shape[2], domains=all_domains, cfg=bcfg)
    return model, spec, hist


def dump_tsmnet(u: Unit, model, data: dict, masks: dict, device, K: int) -> tuple[dict, dict]:
    sess = D.session_index(u.ds, data["session"])
    dom = data["subject"] * 10 + sess
    S = M.tsmnet_prebn(model, data["X"], device, groups=data["subject"])
    d = torch.as_tensor(dom)
    q = model.subspacedimes
    z = torch.zeros(len(dom), q * (q + 1) // 2, dtype=torch.float64)
    logits = torch.zeros(len(dom), K, dtype=torch.float64)
    dom_mean, dom_var = {}, {}
    in_set = torch.as_tensor(data["in_label_set"])
    for du in np.unique(dom):               # every domain re-centred on its own trials of the label set
        m = d == int(du)
        fit = m & in_set
        if int(fit.sum()) < 2:
            raise ProvenanceError(f"domain {int(du)}: {int(fit.sum())} trials to re-centre on")
        mean, var = M.tsmnet_refit_domain(model, S[fit], int(du))
        dom_mean[int(du)], dom_var[int(du)] = mean.squeeze(0).numpy(), var.reshape(-1).numpy()
        zz, ll = M.tsmnet_head(model, S[m], d[m])
        z[m], logits[m] = zz, ll
    extra = dict(S=S.numpy(), z=z.float().numpy(), logits=logits.float().numpy(), domain=dom)
    stats = dict(domain_ids=np.array(sorted(dom_mean)), domain_mean=np.stack([dom_mean[k] for k in sorted(dom_mean)]),
                 domain_var=np.concatenate([dom_var[k] for k in sorted(dom_var)]),
                 bn_std=model.spddsbnorm.std.detach().reshape(-1).numpy())
    return extra, stats


def replay_tsmnet(spec: dict, ckpt: Path, S: np.ndarray, dom: np.ndarray, stats: dict) -> tuple:
    """Recompute (z, logits) on CPU from the dumped artifacts only: checkpoint + domain statistics + S."""
    fresh = rebuild(spec, torch.device("cpu"))
    fresh.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=True))
    fresh.eval()
    for i, did in enumerate(stats["domain_ids"]):
        bnd = fresh.spddsbnorm.get_domain_obj(torch.tensor(int(did)))
        bnd.running_mean_test.data = torch.as_tensor(stats["domain_mean"][i])[None].clone()
        bnd.running_var_test = torch.as_tensor(stats["domain_var"][i]).reshape(1, 1).clone()
    z, lg = M.tsmnet_head(fresh, torch.as_tensor(S), torch.as_tensor(dom))
    return z.numpy(), lg.numpy()


def expected_rows(ds: str, subject: int) -> int:
    return int(sum(len(np.load(cache_dir(ds) / f, allow_pickle=False)["y"]) for f in D.cache_files(ds, subject)))


# ------------------------------------------------------------------ EEGNet / Chambon
def train_braindecode(u: Unit, cfg: dict, data: dict, masks: dict, device, log) -> tuple:
    bcfg = cfg["backbones"][u.backbone]
    tcfg = cfg["training"]
    K = len(data["classes"])
    X, y = data["X"], data["y"]
    tr, va = masks["train"], masks["val"]
    mu = X[tr].mean(axis=(0, 2), dtype=np.float64).astype(np.float32)
    sd = X[tr].std(axis=(0, 2), dtype=np.float64).astype(np.float32)
    if np.any(sd <= 0):
        raise RuntimeError("zero-variance channel in source-train data")
    Xn = (X - mu[None, :, None]) / sd[None, :, None]
    if u.backbone == "eegnet":
        model = M.build_eegnet(K, X.shape[1], X.shape[2], bcfg).to(device)
        spec = dict(kind="eegnet", n_classes=K, n_chans=X.shape[1], n_times=X.shape[2], cfg=bcfg)
    else:
        model = M.build_chambon(K, X.shape[1], data["sfreq"], X.shape[2], bcfg).to(device)
        spec = dict(kind="chambon", n_classes=K, n_chans=X.shape[1], n_times=X.shape[2], sfreq=data["sfreq"], cfg=bcfg)
    if bcfg.get("loss") == "class_weighted_ce":
        cnt = np.bincount(y[tr], minlength=K).astype(np.float64)
        w = torch.as_tensor(cnt.sum() / (K * np.maximum(cnt, 1)), dtype=torch.float32, device=device)
    else:
        w = None
    opt = torch.optim.AdamW(model.parameters(), lr=bcfg["optimizer"]["lr"], weight_decay=bcfg["optimizer"]["weight_decay"])
    Xtr = torch.as_tensor(Xn[tr], dtype=torch.float32)
    ytr = torch.as_tensor(y[tr])
    Xva = torch.as_tensor(Xn[va], dtype=torch.float32)
    yva = torch.as_tensor(y[va])
    on_gpu = (Xtr.numel() + Xva.numel()) * 4 < 8e9
    if on_gpu:
        Xtr, ytr, Xva, yva = Xtr.to(device), ytr.to(device), Xva.to(device), yva.to(device)
    rng = np.random.default_rng([u.seed, u.target, 17])
    bs = bcfg["batch_size"]
    hist, best, best_key, bad = [], None, (-np.inf, np.inf), 0
    for ep in range(tcfg["max_epochs"]):
        model.train()
        t0, tl, nb = time.time(), 0.0, 0
        perm = rng.permutation(len(ytr))
        for i in range(0, len(perm) - bs + 1, bs):          # drop the last partial batch
            idx = torch.as_tensor(perm[i:i + bs], device=Xtr.device)
            xb, yb = Xtr[idx].to(device), ytr[idx].to(device)
            loss = F.cross_entropy(model(xb), yb, weight=w)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            tl += loss.item()
            nb += 1
        model.eval()
        with torch.no_grad():
            vlog = torch.cat([model(Xva[i:i + 1024].to(device)) for i in range(0, len(yva), 1024)])
            vl = F.cross_entropy(vlog, yva.to(device), weight=w).item()
        vb = balanced_accuracy(yva.cpu().numpy(), vlog.argmax(1).cpu().numpy(), K)
        hist.append(dict(epoch=ep, train_loss=tl / max(nb, 1), val_loss=vl, val_bacc=vb, sec=time.time() - t0))
        log(f"ep {ep:3d} train {tl / max(nb, 1):.4f} val {vl:.4f} bacc {vb:.3f} ({time.time() - t0:.1f}s)")
        if improves(vb, vl, best_key):
            best_key, best, bad = (vb, vl), copy.deepcopy(model.state_dict()), 0
        else:
            bad += 1
        if bad >= tcfg["patience"] and ep + 1 >= tcfg["min_epochs"]:
            break
    model.load_state_dict(best)
    if u.backbone == "eegnet":
        M.stabilize_renorm(model, X.shape[1], X.shape[2], device)
    spec["class_weights"] = None if w is None else w.cpu().numpy().tolist()
    spec["add_log_softmax"] = bool(getattr(model, "add_log_softmax", False))
    return model, spec, hist, (mu, sd)


# ------------------------------------------------------------------ unit driver
def run_unit(uid: str, wave: str = "W1", cfg_path: Path | None = None) -> dict:
    t_start = time.time()
    u = Unit.parse(uid)
    if u.uid != uid:
        raise ValueError(f"non-canonical unit id {uid} (expected {u.uid})")
    cfg = load_cfg(cfg_path)
    sha = require_clean_git()
    out = unit_dir(wave, uid)
    out.mkdir(parents=True, exist_ok=True)
    done = out / "DONE.json"
    if done.exists():
        return dict(status="skip", unit=uid)
    logf = open(out / "train.log", "a")

    def log(msg):
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    threads = int(os.environ.get("SLURM_CPUS_PER_TASK", "4"))
    set_determinism(u.seed, threads)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available")
    device = torch.device("cuda")
    gpu = torch.cuda.get_device_name(0)
    log(f"unit {uid} sha {sha[:12]} gpu {gpu} host {socket.gethostname()}")

    D.validate_config(cfg)
    split = make_split(u.ds, u.target, u.seed, cfg["training"]["val_fraction_subjects"])
    subjects = split["train"] + split["val"] + [u.target]
    cache_hashes = D.verify_cache(u.ds, subjects)             # every file used == MANIFEST entry
    data = D.load(u.ds, u.label_set, subjects)
    for s in subjects:                                        # no silent row loss in the loader
        if int((data["subject"] == s).sum()) != expected_rows(u.ds, s):
            raise ProvenanceError(f"subject {s}: loaded rows != cached rows")
    subj = data["subject"]
    masks = dict(train=np.isin(subj, split["train"]), val=np.isin(subj, split["val"]), target=subj == u.target)
    masks["train"] &= data["y"] >= 0                      # label set only (B14-c2) and scored epochs only (Sleep)
    masks["val"] &= data["y"] >= 0
    # leakage invariants (fail loud)
    if np.any(masks["target"] & (masks["train"] | masks["val"])):
        raise ProvenanceError("target rows in train/val")
    if set(np.unique(subj[masks["train"]])) != set(split["train"]) or set(np.unique(subj[masks["val"]])) != set(split["val"]):
        raise ProvenanceError("split manifest does not match loaded data")
    K = len(data["classes"])
    manifest = cache_dir(u.ds) / "MANIFEST.json"
    log(f"split train={split['train']} val={split['val']} target={u.target} n_train={masks['train'].sum()} n_val={masks['val'].sum()} n_target={masks['target'].sum()}")

    if u.backbone == "tsmnet":
        model, spec, hist = train_tsmnet(u, cfg, data, masks, device, log)
        norm = None
    else:
        model, spec, hist, norm = train_braindecode(u, cfg, data, masks, device, log)
    # save the selected, pristine model before any dump-time re-centering touches BN buffers
    torch.save(model.state_dict(), out / "ckpt.pt")
    write_json(out / "model_spec.json", spec)
    write_json(out / "split.json", split)
    if norm is not None:
        np.savez(out / "norm.npz", mean=norm[0], std=norm[1])

    # ---------------- dumps
    meta_keys = D.META_KEYS + (["record_index", "truncated_night"] if u.ds == "Sleep" else [])
    role = np.where(masks["target"], "target", np.where(np.isin(subj, split["train"]), "train", "val"))
    rows_src = ~masks["target"]
    if u.backbone == "tsmnet":
        extra, stats = dump_tsmnet(u, model, data, masks, device, K)
        np.savez(out / "domain_stats.npz", **stats)
        z_r, lg_r = replay_tsmnet(spec, out / "ckpt.pt", extra["S"], extra["domain"], stats)   # gate 3, all rows
        err = max(float(np.max(np.abs(lg_r - extra["logits"]))), float(np.max(np.abs(z_r - extra["z"]))))
    else:
        Xn = (data["X"] - norm[0][None, :, None]) / norm[1][None, :, None]
        z, logits = M.braindecode_forward(model, Xn, device, groups=data["subject"])
        extra = dict(z=z, logits=logits)
        rep = M.replay_head(model, z, u.backbone, device)                                     # gate 3, all rows
        err = float(np.max(np.abs(rep - logits)))
    if not err <= 1e-5:
        raise ProvenanceError(f"classifier replay mismatch {err}")
    for name, rows in (("dump_target.npz", masks["target"]), ("dump_source.npz", rows_src)):
        arrs = {k: data[k][rows] for k in meta_keys}
        arrs.update({k: v[rows] for k, v in extra.items()})
        arrs["role"] = role[rows]
        np.savez(out / name, **arrs)

    # ---------------- self-replay from the saved checkpoint (bit-exact target features)
    fresh = rebuild(spec, device)
    fresh.load_state_dict(torch.load(out / "ckpt.pt", map_location="cpu", weights_only=True))
    if u.backbone == "tsmnet":
        S2 = M.tsmnet_prebn(fresh, data["X"][masks["target"]], device, groups=subj[masks["target"]]).numpy()
        replay_ok = bool(np.array_equal(S2, extra["S"][masks["target"]]))
    else:
        fresh.to(device)
        z2, _ = M.braindecode_forward(fresh, Xn[masks["target"]], device, groups=subj[masks["target"]])
        replay_ok = bool(np.array_equal(z2, extra["z"][masks["target"]]))
    if not replay_ok:
        raise ProvenanceError("self-replay of target features is not bit-exact")

    # ---------------- descriptive sanity (pre-reg §7): evaluation session/night of the target
    ev = masks["target"] & (D.session_index(u.ds, data["session"]) == 1) & (data["y"] >= 0)
    ad = masks["target"] & (D.session_index(u.ds, data["session"]) == 0)
    if ev.sum() == 0 or ad.sum() == 0:
        raise ProvenanceError(f"target has {int(ad.sum())} adaptation / {int(ev.sum())} evaluation rows")
    sanity = balanced_accuracy(data["y"][ev], extra["logits"][ev].argmax(1), K)
    if not np.isfinite(sanity):
        raise ProvenanceError("non-finite sanity value")
    # target-side sanity lives in its own file, read only by scripts/summarize_w1.py after the fleet
    write_json(out / "sanity_target.json", dict(
        unit=uid, sanity_eval_bacc=sanity, sanity_eval_n=int(ev.sum()),
        sanity_eval_recall={int(k): float(np.mean(extra["logits"][ev].argmax(1)[data["y"][ev] == k] == k))
                            for k in range(K) if np.any(data["y"][ev] == k)},
        sanity_eval_classes_present=int(len(np.unique(data["y"][ev]))),
        sanity_note=("TSMNet: each target session re-centred on its own label-set trials (standard TSMNet inference)"
                     if u.backbone == "tsmnet" else "eval-mode network, source normalisation")))
    best_ep = select_epoch(hist)
    metrics = dict(unit=uid, best_epoch=best_ep, best_val_loss=hist[best_ep]["val_loss"],
                   best_val_bacc=hist[best_ep]["val_bacc"], epochs_run=len(hist), replay_max_abs_err=err,
                   n_rows=dict(target=int(masks["target"].sum()), source=int((~masks["target"]).sum())),
                   history=hist)
    write_json(out / "metrics.json", metrics)
    files = {f.name: sha256_file(f) for f in sorted(out.iterdir())
             if f.suffix in (".pt", ".npz", ".json") and f.name != "DONE.json" and not f.name.startswith("FAILED_")}
    write_json(done, dict(
        status="ok", unit=uid, wave=wave, git_sha=sha, code_sig=code_sig(), cache_manifest_sha256=sha256_file(manifest),
        torch=torch.__version__, python=platform.python_version(), gpu=gpu, host=socket.gethostname(),
        slurm_job=os.environ.get("SLURM_JOB_ID"), seconds=round(time.time() - t_start, 1),
        replay_bit_exact=replay_ok, cache_files=cache_hashes, cpu=_cpu_model(), threads=torch.get_num_threads(),
        files=files))
    log(f"DONE {uid} best_epoch={best_ep} val_bacc={metrics['best_val_bacc']:.3f} ({time.time() - t_start:.0f}s)")
    logf.close()
    return dict(status="ok", unit=uid)


def _cpu_model() -> str:
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def rebuild(spec: dict, device):
    if spec["kind"] == "tsmnet":
        return M.build_tsmnet(spec["n_classes"], spec["n_chans"], spec["n_times"], spec["domains"], device, spec["cfg"])
    if spec["kind"] == "eegnet":
        return M.build_eegnet(spec["n_classes"], spec["n_chans"], spec["n_times"], spec["cfg"])
    return M.build_chambon(spec["n_classes"], spec["n_chans"], spec["sfreq"], spec["n_times"], spec["cfg"])
