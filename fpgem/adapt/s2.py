"""W2-S2: multi-batch known proportions (pre-reg S2 + appendum A2), MI units only, CPU."""
from __future__ import annotations

import time

import numpy as np
from scipy.special import logsumexp

from .. import data as D
from .features import UnitView, balanced_accuracy
from .gem import A_MAX, A_MIN, ClassGauss, _mstep_affine, gem, gem_multibatch, pooled_affine
from .s1 import batch_rows

B = 4


def oracle_affine(z, y, g: ClassGauss):
    """Labelled coordinatewise affine fit (responsibilities = one-hot labels)."""
    r = np.eye(len(g.prior))[y]
    return _mstep_affine(z, r, g, len(z))


def designs(K: int, rng) -> dict:
    u = np.full(K, 1.0 / K)
    out = {"balanced": np.tile(u, (B, 1))}
    if K == 2:
        out["blocked"] = np.array([[0.85, 0.15], [0.15, 0.85]] * 2)
        r = rng.dirichlet(np.ones(2))
        out["random"] = np.array([r, r[::-1], r, r[::-1]])
    else:
        blk = np.full((K, K), 0.3 / (K - 1)) + np.eye(K) * (0.7 - 0.3 / (K - 1))
        out["blocked"] = blk[:B]
        r = rng.dirichlet(np.ones(K))
        out["random"] = np.stack([np.roll(r, k) for k in range(B)])
    return out


def split_batches(y: np.ndarray, Pi: np.ndarray, rng) -> list:
    """Partition all rows into B equal batches with class counts ≈ m·Π (union = all rows)."""
    K = Pi.shape[1]
    idx = {k: list(rng.permutation(np.flatnonzero(y == k))) for k in range(K)}
    n = len(y)
    m = n // B
    counts = np.floor(Pi * m).astype(int)
    tot = np.array([len(idx[k]) for k in range(K)])
    # distribute remaining per-class totals to batches by largest fractional part
    frac = Pi * m - counts
    for k in range(K):
        rem = tot[k] - counts[:, k].sum()
        order = np.argsort(-frac[:, k])
        for j in range(max(rem, 0)):
            counts[order[j % B], k] += 1
    batches = []
    for bi in range(B):
        rows = []
        for k in range(K):
            take, idx[k] = idx[k][:counts[bi, k]], idx[k][counts[bi, k]:]
            rows += take
        batches.append(np.array(rows, dtype=int))
    return batches


def run(uid: str) -> dict:
    t0 = time.time()
    uv = UnitView(uid)
    if uv.u.ds == "Sleep":
        return dict(unit=uid, skipped="Sleep excluded from S2 (appendum A2)")
    K, S, T = uv.K, uv.src, uv.tgt
    tr = (S["role"] == "train") & (S["y"] >= 0)
    z_tr, y_tr = uv.features("src", tr), S["y"][tr]
    g = ClassGauss.fit(z_tr, y_tr, K)
    src_mean, src_std = z_tr.mean(0), z_tr.std(0)
    # between-source-subject spread for the injected shift
    subj = S["subject"][tr]
    means = np.stack([z_tr[subj == s].mean(0) for s in np.unique(subj)])
    lsd = np.stack([np.log(np.maximum(z_tr[subj == s].std(0), 1e-8)) for s in np.unique(subj)])
    v_b, v_la = means.var(0), lsd.var(0)

    A = batch_rows(uv, 0)
    E = batch_rows(uv, 1) & (T["y"] >= 0)
    zA, yA = uv.features("tgt", A), T["y"][A]
    zE, yE = uv.features("tgt", E), T["y"][E]
    a_orc, b_orc = oracle_affine(zA, yA, g)
    out = dict(unit=uid, K=K, rows=[])
    for s_scale in (0.5, 1.0):
        for draw in range(5):
            rng = np.random.default_rng([uv.u.seed, uv.u.target, draw, int(s_scale * 10)])
            la0 = rng.normal(0, s_scale * np.sqrt(v_la))
            a0 = np.clip(np.exp(la0), A_MIN, A_MAX)
            b0 = rng.normal(0, s_scale * np.sqrt(v_b))
            zA_obs = (zA - b0) / a0
            zE_obs = (zE - b0) / a0
            a_star, b_star = a_orc * a0, a_orc * b0 + b_orc
            denom = np.linalg.norm(np.concatenate([np.log(a0), b0]))
            for dname, Pi in designs(K, rng).items():
                bats = split_batches(yA, Pi, np.random.default_rng([uv.u.seed, uv.u.target, draw, int(s_scale * 10), 7]))
                zs = [zA_obs[bi] for bi in bats]
                ests = {}
                a, b = pooled_affine(zA_obs, src_mean, src_std)
                ests["Pooled-union"] = (a, b, 0, True)
                r = gem(zA_obs, g, "fixed")
                ests["FP-union"] = (r.a, r.b, r.iters, r.converged)
                for nm, upd, pri, box in (("MB-known", "known", list(Pi), None), ("MB-unknown", "unknown", None, None),
                                          ("MB-interval", "interval", list(Pi), 0.1)):
                    r = gem_multibatch(zs, g, pri, upd, box=box)
                    ests[nm] = (r.a, r.b, r.iters, r.converged)
                sv = np.linalg.svd(Pi - Pi.mean(0), compute_uv=False)
                for nm, (a, b, it, conv) in ests.items():
                    err = np.linalg.norm(np.concatenate([np.log(a) - np.log(a_star), b - b_star])) / denom
                    bacc = balanced_accuracy(yE, uv.head(a * zE_obs + b).argmax(1), K)
                    out["rows"].append(dict(scale=s_scale, draw=draw, design=dname, estimator=nm, geom_err=float(err),
                                            bacc_eval=bacc, iters=int(it), converged=bool(conv),
                                            sigma_min_centered=float(sv[min(K - 1, len(sv)) - 1]) if K > 1 else 0.0))
    out["seconds"] = round(time.time() - t0, 1)
    return out
