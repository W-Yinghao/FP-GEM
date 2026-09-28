"""W2-S3: detecting fixed-prior mismatch (pre-reg S3 + appendum A2), CPU."""
from __future__ import annotations

import time

import numpy as np
from scipy.special import logsumexp
from scipy.stats import chi2

from .features import UnitView
from .gem import ClassGauss, gem
from .s1 import batch_rows

N_BOOT = 500


def prior_em(x: np.ndarray, g: ClassGauss, iters: int = 500, tol: float = 1e-10) -> np.ndarray:
    cl = g.class_loglik(x)
    pi = g.prior.copy()
    for _ in range(iters):
        ll = cl + np.log(np.maximum(pi, 1e-300))[None]
        r = np.exp(ll - logsumexp(ll, 1, keepdims=True))
        new = r.mean(0)
        if np.abs(new - pi).max() < tol:
            pi = new
            break
        pi = new
    return pi


def lr_stat(z: np.ndarray, g: ClassGauss) -> tuple[float, np.ndarray, tuple]:
    r = gem(z, g, "fixed")
    x = r.a * z + r.b
    cl = g.class_loglik(x)
    pi_hat = prior_em(x, g)
    l1 = logsumexp(cl + np.log(np.maximum(pi_hat, 1e-300))[None], 1).sum()
    l0 = logsumexp(cl + np.log(g.prior)[None], 1).sum()
    return float(2 * (l1 - l0)), pi_hat, (r.a, r.b)


def lr_test(z: np.ndarray, g: ClassGauss, rng) -> dict:
    stat, pi_hat, (a, b) = lr_stat(z, g)
    n, K = len(z), len(g.prior)
    null = []
    for _ in range(N_BOOT):
        y = rng.choice(K, n, p=g.prior)
        x = g.mu[y] + rng.normal(size=(n, g.mu.shape[1])) * np.sqrt(g.var[y])
        null.append(lr_stat((x - b) / a, g)[0])
    null = np.array(null)
    p = (1 + np.sum(null >= stat)) / (1 + N_BOOT)
    return dict(stat=stat, p=float(p), reject=bool(p <= 0.05), pi_hat=pi_hat.tolist())


def moment_test(z: np.ndarray, g: ClassGauss, z_src: np.ndarray, y_src: np.ndarray) -> dict:
    """Prior-invariant moment test: project out source class-mean differences; Hotelling-type T² with a
    Ledoit–Wolf pooled within-class source covariance; χ² reference (appendum A2)."""
    from sklearn.covariance import LedoitWolf
    K = len(g.prior)
    Dm = (g.mu[:K - 1] - g.mu[K - 1]).T                            # (D, K-1)
    Q, _ = np.linalg.qr(Dm)
    P = np.eye(z.shape[1]) - Q @ Q.T
    U, sv, _ = np.linalg.svd(P)
    W = U[:, sv > 0.5].T                                          # orthonormal basis of the complement
    resid = np.concatenate([z_src[y_src == k] - g.mu[k] for k in range(K)]) @ W.T
    C = LedoitWolf().fit(resid).covariance_
    d = (z.mean(0) - g.mu[K - 1]) @ W.T
    t2 = float(len(z) * d @ np.linalg.solve(C, d))
    df = W.shape[0]
    p = float(chi2.sf(t2, df))
    return dict(t2=t2, df=int(df), p=p, reject=bool(p <= 0.05))


def run(uid: str) -> dict:
    t0 = time.time()
    uv = UnitView(uid)
    K, S, T = uv.K, uv.src, uv.tgt
    tr = (S["role"] == "train") & (S["y"] >= 0)
    z_tr, y_tr = uv.features("src", tr), S["y"][tr]
    g = ClassGauss.fit(z_tr, y_tr, K)
    A = batch_rows(uv, 0)
    zA, yA = uv.features("tgt", A), T["y"][A]
    out = dict(unit=uid, K=K, rows=[])
    rng = np.random.default_rng([uv.u.seed, uv.u.target, 3])
    true_p = np.bincount(yA[yA >= 0], minlength=K) / max((yA >= 0).sum(), 1)
    cells = [("natural", None, zA, true_p)]
    if uv.u.ds != "Sleep":
        for q in (0.3, 0.2):
            for draw in range(5):
                r2 = np.random.default_rng([uv.u.seed, uv.u.target, draw, int(q * 100)])
                c0 = np.flatnonzero(yA == 0)
                keep_n = int(round(len(c0) * q / (1 - q)))
                keep = np.concatenate([r2.choice(c0, keep_n, replace=False), np.flatnonzero(yA != 0)])
                p = np.bincount(yA[keep], minlength=K) / len(keep)
                cells.append((f"q{q}", draw, zA[keep], p))
    for name, draw, z, p in cells:
        lr = lr_test(z, g, rng)
        mt = moment_test(z, g, z_tr, y_tr)
        out["rows"].append(dict(cell=name, draw=draw, n=len(z), true_prop=np.asarray(p).tolist(),
                                tv_true_vs_src=float(0.5 * np.abs(np.asarray(p) - g.prior).sum()),
                                lr=lr, moment=mt))
    out["seconds"] = round(time.time() - t0, 1)
    return out
