"""Independent QC of finished W1 units (pre-reg §6 gates 2–3), without reading target sanity values.

  python -m scripts.check_unit --wave W1 --units configs/units_W1.txt [--out results/W1/qc.csv]
  python -m scripts.check_unit --wave W1probeA1 --unit B14-c4-tsmnet-t01-s0

Checks per unit: split manifest vs data; dump row counts vs caches; roles; label ranges; finite arrays;
logits reproduced from dumped features by the saved classifier (all backbones); TSMNet SPD matrices
symmetric positive definite; DONE.json file hashes match the files on disk.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys

import numpy as np
import torch

from fpgem import data as D
from fpgem.paths import RUNS
from fpgem.provenance import sha256_file
from fpgem.train.source import Unit, rebuild


def check(wave: str, uid: str) -> dict:
    u = Unit.parse(uid)
    d = RUNS / wave / uid
    res = dict(unit=uid, ok=False, problems=[])
    P = res["problems"]
    if not (d / "DONE.json").exists():
        P.append("no DONE.json")
        return res
    done = json.load(open(d / "DONE.json"))
    for name, h in done["files"].items():
        if sha256_file(d / name) != h:
            P.append(f"hash mismatch {name}")
    split = json.load(open(d / "split.json"))
    if u.target in split["train"] or u.target in split["val"] or set(split["train"]) & set(split["val"]):
        P.append("split overlap")
    if sorted(split["train"] + split["val"] + [u.target]) != sorted(D.all_subjects(u.ds)):
        P.append("split does not cover all subjects")
    T = np.load(d / "dump_target.npz", allow_pickle=False)
    S_ = np.load(d / "dump_source.npz", allow_pickle=False)
    # row counts vs caches
    n_t = len(D.load(u.ds, u.label_set, [u.target])["y"])
    if len(T["y"]) != n_t:
        P.append(f"target rows {len(T['y'])} != cache {n_t}")
    if set(np.unique(T["subject"])) != {u.target} or set(np.unique(T["role"])) != {"target"}:
        P.append("target dump contains non-target rows")
    src_subj = set(np.unique(S_["subject"]).tolist())
    if src_subj != set(split["train"] + split["val"]):
        P.append("source dump subjects != train+val")
    for s in split["val"]:
        if not np.all(S_["role"][S_["subject"] == s] == "val"):
            P.append(f"role mismatch for val subject {s}")
    for s in split["train"]:
        if not np.all(S_["role"][S_["subject"] == s] == "train"):
            P.append(f"role mismatch for train subject {s}")
    K = len(D.LABEL_SETS[(u.ds, u.label_set)])
    for Z in (T, S_):
        if Z["y"].min() < -1 or Z["y"].max() >= K:
            P.append("label out of range")
        for k in ("z", "logits"):
            if not np.isfinite(Z[k]).all():
                P.append(f"non-finite {k}")
    # classifier replay from dumped features
    spec = json.load(open(d / "model_spec.json"))
    model = rebuild(spec, torch.device("cpu"))
    model.load_state_dict(torch.load(d / "ckpt.pt", map_location="cpu", weights_only=True))
    model.eval()
    with torch.no_grad():
        for name, Z in (("target", T), ("source", S_)):
            idx = np.arange(0, len(Z["y"]), max(1, len(Z["y"]) // 2000))       # subsample big dumps
            z = torch.as_tensor(Z["z"][idx])
            if spec["kind"] == "tsmnet":
                lg = model.classifier(z.double()).float().numpy()
            elif spec["kind"] == "eegnet":
                w = model.final_layer.conv_classifier.weight
                lg = model.final_layer(z.reshape(len(idx), w.shape[1], w.shape[2], w.shape[3])).float().numpy()
            else:
                lg = model.final_layer(z).float().numpy()
            err = float(np.max(np.abs(lg - Z["logits"][idx])))
            res[f"replay_err_{name}"] = err
            if err > 1e-4:
                P.append(f"{name} logit replay error {err:.2e}")
    if spec["kind"] == "tsmnet":
        S = T["S"]
        if not np.allclose(S, np.swapaxes(S, 1, 2), atol=1e-10):
            P.append("S not symmetric")
        if np.linalg.eigvalsh(S[:50]).min() <= 0:
            P.append("S not positive definite")
        ds_ = np.load(d / "domain_stats.npz")
        if len(ds_["domain_ids"]) != len(np.unique(np.concatenate([T["domain"], S_["domain"]]))):
            P.append("domain stats count mismatch")
    m = json.load(open(d / "metrics.json"))
    res.update(best_epoch=m["best_epoch"], epochs_run=m["epochs_run"], best_val_bacc=round(m["best_val_bacc"], 4),
               seconds=done["seconds"], gpu=done["gpu"], replay_bit_exact=done["replay_bit_exact"])
    res["ok"] = not P
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default="W1")
    ap.add_argument("--unit")
    ap.add_argument("--units")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    torch.set_num_threads(2)
    uids = [a.unit] if a.unit else [l.strip() for l in open(a.units) if l.strip() and not l.startswith("#")]
    rows = []
    for uid in uids:
        try:
            r = check(a.wave, uid)
        except Exception as e:                      # reason-coded; never silently passed
            r = dict(unit=uid, ok=False, problems=[f"exception {e!r}"])
        rows.append(r)
        print(json.dumps(r), flush=True)
    if a.out:
        keys = sorted({k for r in rows for k in r})
        with open(a.out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for r in rows:
                w.writerow({**r, "problems": "; ".join(r.get("problems", []))})
    bad = [r["unit"] for r in rows if not r["ok"]]
    print(f"checked {len(rows)}; failing {len(bad)}: {bad[:20]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
