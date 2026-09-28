"""W2-S1: estimator family under natural shift, per W1 unit (CPU, from dumps)."""
from __future__ import annotations

import time

import numpy as np

from .. import data as D
from .features import UnitView, balanced_accuracy
from .gem import ClassGauss, gem, pooled_affine, profile_info_prior

METHODS = ["Identity", "Pooled", "FP", "Joint", "K6", "Kstar"]


def batch_rows(uv: UnitView, sess: int) -> np.ndarray:
    """Label-free batch of a target session (A2: B14-c2 batches contain only its L/R trials)."""
    T = uv.tgt
    m = D.session_index(uv.u.ds, T["session"]) == sess
    if uv.u.ds == "B14" and uv.u.label_set == "c2":
        m &= T["in_label_set"]
    return m


def sleep_r2(uv: UnitView, K: int) -> float:
    """Between-source-night variance of additive stage logits (ref = last class), averaged over directions."""
    S = uv.src
    tr = (S["role"] == "train") & (S["y"] >= 0)
    logits = []
    for s in np.unique(S["subject"][tr]):
        for n in np.unique(S["session"][tr & (S["subject"] == s)]):
            m = tr & (S["subject"] == s) & (S["session"] == n)
            c = np.bincount(S["y"][m], minlength=K) + 0.5
            p = c / c.sum()
            logits.append(np.log(p[:-1] / p[-1]))
    return float(np.mean(np.var(np.array(logits), axis=0, ddof=1)))


def run(uid: str) -> dict:
    t0 = time.time()
    uv = UnitView(uid)
    K = uv.K
    S = uv.src
    tr = (S["role"] == "train") & (S["y"] >= 0)
    va = (S["role"] == "val") & (S["y"] >= 0)
    z_tr = uv.features("src", tr)
    y_tr = S["y"][tr]
    g = ClassGauss.fit(z_tr, y_tr, K)
    src_mean, src_std = z_tr.mean(0), z_tr.std(0)

    # kappa*
    if uv.u.ds == "Sleep":
        r2 = sleep_r2(uv, K)
        I = profile_info_prior(uv.features("src", va), g)
        kstar = 1.0 / (I * r2)
    else:
        r2, I, kstar = 0.0, float("nan"), float("inf")     # balanced cue schedule, no rejection

    T = uv.tgt
    A = batch_rows(uv, 0)
    E = batch_rows(uv, 1)
    E_scored = E & (T["y"] >= 0)
    out = dict(unit=uid, K=K, r2=r2, I_eta_theta=I, kappa_star=kstar, pi_src=g.prior.tolist(),
               n_adapt=int(A.sum()), n_eval=int(E_scored.sum()), rows=[])

    for protocol, fit_rows in (("inductive", A), ("transductive", E)):
        z_fit = uv.features("tgt", fit_rows)
        z_ev = uv.features("tgt", E_scored)
        y_ev = T["y"][E_scored]
        fits = {"Identity": (np.ones(z_fit.shape[1]), np.zeros(z_fit.shape[1]), g.prior, 0, True)}
        a, b = pooled_affine(z_fit, src_mean, src_std)
        fits["Pooled"] = (a, b, g.prior, 0, True)
        for name, kw in (("FP", dict(prior_mode="fixed")), ("Joint", dict(prior_mode="joint")),
                         ("K6", dict(prior_mode="dirichlet", kappa=6.0)),
                         ("Kstar", dict(prior_mode="fixed") if not np.isfinite(kstar) else dict(prior_mode="dirichlet", kappa=kstar))):
            r = gem(z_fit, g, **kw)
            fits[name] = (r.a, r.b, r.pi, r.iters, r.converged)
        for name, (a, b, pi, it, conv) in fits.items():
            x = a * z_ev + b
            head = balanced_accuracy(y_ev, uv.head(x).argmax(1), K)
            dens = balanced_accuracy(y_ev, g.class_loglik(x).argmax(1), K)
            out["rows"].append(dict(protocol=protocol, method=name, bacc_head=head, bacc_density=dens,
                                    prior_move_l1=float(np.abs(np.asarray(pi) - g.prior).sum()),
                                    log_a_norm=float(np.linalg.norm(np.log(a))), b_norm=float(np.linalg.norm(b)),
                                    iters=int(it), converged=bool(conv), pi_hat=np.asarray(pi).tolist()))
        if uv.kind == "tsmnet":                               # TSMNet's own SFUDA: re-centre on the fit batch
            ref = uv.karcher(T["S"][fit_rows])
            x = uv.features("tgt", E_scored, ref=ref)
            out["rows"].append(dict(protocol=protocol, method="Recenter",
                                    bacc_head=balanced_accuracy(y_ev, uv.head(x).argmax(1), K),
                                    bacc_density=float("nan"), prior_move_l1=0.0, log_a_norm=float("nan"),
                                    b_norm=float("nan"), iters=0, converged=True, pi_hat=g.prior.tolist()))
    out["seconds"] = round(time.time() - t0, 1)
    return out
