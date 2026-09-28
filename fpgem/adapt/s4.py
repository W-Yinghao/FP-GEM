"""W2-S4: signal-level injections — class-dependence of the latent response and recovery (GPU re-inference).

prep():  per-subject, per-session mean spatial covariance of the model-window signals (µV) for EA.
run(uid): per W1 unit, inject known changes into the target's signals and re-infer features on the GPU.
"""
from __future__ import annotations

import time

import numpy as np
import torch

from .. import data as D
from .. import models as M
from ..paths import STORE
from ..train.source import rebuild
from .features import UnitView, balanced_accuracy
from .gem import ClassGauss, gem, pooled_affine
from .s1 import batch_rows

COV_DIR = STORE / "cache" / "s4_cov"
N_PERM = 1000


def _label_set(ds):
    return {"B14": "c4", "Lee": "c2", "Sleep": "c5"}[ds]


def prep(ds: str) -> None:
    COV_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for s in D.all_subjects(ds):
        d = D.load(ds, _label_set(ds), [s])
        for sess in np.unique(d["session"]):
            X = d["X"][d["session"] == sess].astype(np.float64)
            C = np.einsum("nct,ndt->cd", X, X) / (X.shape[0] * X.shape[2])
            out[f"{s}|{sess}"] = C
    np.savez(COV_DIR / f"{ds}.npz", **out)


def _sqrtm(C, p):
    """Matrix power of a PSD matrix; for p < 0 a pseudo-inverse power (eigenvalues below 1e-8·max are
    dropped), so rank-deficient (re-referenced) covariances are handled (W2 appendum A3)."""
    w, V = np.linalg.eigh(C)
    keep = w > 1e-8 * w.max()
    wp = np.zeros_like(w)
    wp[keep] = w[keep] ** p
    return (V * wp) @ V.T


def injections(C: int, rng, ds: str) -> list:
    out = []
    for draw in range(3):
        g = np.exp(rng.normal(0, 0.3, C))
        out.append(("gain", draw, np.diag(g)))
        R = np.eye(C)
        if C > 3:                          # MI: reference to the mean of 3 random channels
            chans = rng.choice(C, 3, replace=False)
            R[:, chans] -= 1.0 / 3
        else:                              # Sleep (2 bipolar channels): partial reference, appendum A3
            R[:, rng.integers(C)] -= 0.5
        out.append(("reref", draw, R))
        if ds != "Sleep":
            E = rng.normal(size=(C, C))
            E /= np.linalg.norm(E, axis=1, keepdims=True)
            out.append(("mix", draw, np.eye(C) + 0.1 * E))
    return out


def class_dependence(dz: np.ndarray, y: np.ndarray, K: int, rng) -> dict:
    def F(lbl):
        mu = dz.mean(0)
        between = sum((lbl == k).sum() * np.sum((dz[lbl == k].mean(0) - mu) ** 2) for k in range(K)) / (K - 1)
        within = sum(np.sum((dz[lbl == k] - dz[lbl == k].mean(0)) ** 2) for k in range(K)) / (len(dz) - K)
        return between / max(within, 1e-30)
    f0 = F(y)
    null = np.array([F(rng.permutation(y)) for _ in range(N_PERM)])
    cm = np.stack([dz[y == k].mean(0) for k in range(K)])
    rel = float(np.linalg.norm(cm - cm.mean(0)) / max(np.linalg.norm(cm.mean(0)), 1e-30))
    return dict(F=float(f0), p=float((1 + np.sum(null >= f0)) / (1 + N_PERM)), rel_classmean_diff=rel)


def run(uid: str) -> dict:
    t0 = time.time()
    uv = UnitView(uid)
    u, K = uv.u, uv.K
    dev = torch.device("cuda")
    gm = rebuild(uv.spec, dev)
    gm.load_state_dict(torch.load(uv.d / "ckpt.pt", map_location="cpu", weights_only=True))
    gm.to(dev).eval() if uv.kind != "tsmnet" else gm.eval()
    tgt = D.load(u.ds, u.label_set, [u.target])
    X0 = tgt["X"].astype(np.float64)
    T = uv.tgt
    assert len(T["y"]) == len(X0)
    grp = np.full(len(X0), u.target)
    norm = np.load(uv.d / "norm.npz") if uv.kind != "tsmnet" else None

    def feats(X, ref=None):
        Xf = X.astype(np.float32)
        if uv.kind == "tsmnet":
            S = M.tsmnet_prebn(gm, Xf, dev, groups=grp).numpy()
            return uv.tsm_features(S, uv.src_ref if ref is None else ref), S
        Xn = (Xf - norm["mean"][None, :, None]) / norm["std"][None, :, None]
        z, _ = M.braindecode_forward(gm, Xn, dev, groups=grp)
        return z.astype(np.float64), None

    S_ = uv.src
    tr = (S_["role"] == "train") & (S_["y"] >= 0)
    z_tr = uv.features("src", tr)
    g = ClassGauss.fit(z_tr, S_["y"][tr], K)
    src_mean, src_std = z_tr.mean(0), z_tr.std(0)
    covs = np.load(COV_DIR / f"{u.ds}.npz")
    src_keys = [k for k in covs.files if int(k.split("|")[0]) != u.target]
    R_src = np.mean([covs[k] for k in src_keys], 0)

    A = batch_rows(uv, 0)
    E = batch_rows(uv, 1) & (T["y"] >= 0)
    lab = T["y"] >= 0
    yE = T["y"][E]
    z_clean, S_clean = feats(X0)
    clean_bacc = balanced_accuracy(yE, uv.head(z_clean[E]).argmax(1), K)
    rng = np.random.default_rng([u.seed, u.target, 44])
    out = dict(unit=uid, K=K, clean_identity_bacc=clean_bacc, rows=[])
    for kind, draw, Mx in injections(X0.shape[1], rng, u.ds):
        Xi = np.einsum("cd,ndt->nct", Mx, X0)
        z_inj, S_inj = feats(Xi)
        dep = class_dependence((z_inj - z_clean)[lab], T["y"][lab], K, np.random.default_rng([u.seed, u.target, draw, 9]))
        res = {}
        res["Identity"] = uv.head(z_inj[E]).argmax(1)
        a, b = pooled_affine(z_inj[A], src_mean, src_std)
        res["Pooled"] = uv.head(a * z_inj[E] + b).argmax(1)
        for nm, mode in (("FP", "fixed"), ("Joint", "joint")):
            r = gem(z_inj[A], g, mode)
            res[nm] = uv.head(r.a * z_inj[E] + r.b).argmax(1)
        if uv.kind == "tsmnet":
            ref = uv.karcher(S_inj[A])
            res["Recenter"] = uv.head(uv.tsm_features(S_inj[E], ref)).argmax(1)
        # EA at signal level: whiten by the injected adaptation-session mean covariance, re-colour to source
        XA = Xi[A]
        R_a = np.einsum("nct,ndt->cd", XA, XA) / (XA.shape[0] * XA.shape[2])
        P = _sqrtm(R_src, 0.5) @ _sqrtm(R_a, -0.5)
        z_ea, _ = feats(np.einsum("cd,ndt->nct", P, Xi))
        res["EA"] = uv.head(z_ea[E]).argmax(1)
        for nm, pred in res.items():
            out["rows"].append(dict(injection=kind, draw=draw, method=nm, bacc=balanced_accuracy(yE, pred, K),
                                    **{f"dep_{k}": v for k, v in dep.items()}))
    out["seconds"] = round(time.time() - t0, 1)
    return out
