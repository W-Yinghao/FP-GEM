"""Generalized EM for a coordinatewise affine transform under a class mixture (W2 pre-reg §0).

Model: target feature z; T(z) = a ⊙ z + b; source class-conditionals N(μ_y, diag σ²_y); mixture weights π.
The M-step for (a, b) is exact per coordinate (closed form); the prior update depends on the variant:
  fixed (FP, κ = ∞), joint (κ = 0), or Dirichlet MAP with pseudo-counts κ·π_src.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import logsumexp


A_MIN, A_MAX = float(np.exp(-2.0)), float(np.exp(2.0))


@dataclass
class ClassGauss:
    mu: np.ndarray        # (K, D)
    var: np.ndarray       # (K, D)
    prior: np.ndarray     # (K,)

    @staticmethod
    def fit(z: np.ndarray, y: np.ndarray, K: int, floor_rel: float = 1e-4) -> "ClassGauss":
        mu = np.stack([z[y == k].mean(0) for k in range(K)])
        var = np.stack([z[y == k].var(0) for k in range(K)])
        var = np.maximum(var, floor_rel * var.mean())
        prior = np.bincount(y, minlength=K).astype(np.float64)
        return ClassGauss(mu.astype(np.float64), var.astype(np.float64), prior / prior.sum())

    def class_loglik(self, x: np.ndarray) -> np.ndarray:
        """log N(x; μ_y, σ²_y) for every row and class -> (N, K)."""
        d = x[:, None, :] - self.mu[None]
        return -0.5 * (np.sum(d * d / self.var[None], -1) + np.sum(np.log(2 * np.pi * self.var), -1)[None])


@dataclass
class GEMResult:
    a: np.ndarray
    b: np.ndarray
    pi: np.ndarray
    iters: int
    converged: bool
    objective: float


def _mstep_affine(z: np.ndarray, r: np.ndarray, g: ClassGauss, n_eff: float) -> tuple[np.ndarray, np.ndarray]:
    """Exact maximiser of Σ_i Σ_y r_iy log N(a z_i + b; μ_y, σ²_y) + n log a, per coordinate."""
    w = r[:, :, None] / g.var[None]                        # (N, K, D)
    W = w.sum((0, 1))                                      # (D,)
    wz = w * z[:, None, :]
    Sz = wz.sum((0, 1))
    Szz = (wz * z[:, None, :]).sum((0, 1))
    Smu = (w * g.mu[None]).sum((0, 1))
    Szmu = (wz * g.mu[None]).sum((0, 1))
    A = Szz - Sz * Sz / W
    B = Szmu - Smu * Sz / W
    A = np.maximum(A, 1e-12)
    a = (B + np.sqrt(B * B + 4 * A * n_eff)) / (2 * A)
    a = np.clip(a, A_MIN, A_MAX)       # W2 appendum A1: |log a| <= 2 (exact constrained optimum per coordinate)
    b = (Smu - a * Sz) / W
    return a, b


def gem(z: np.ndarray, g: ClassGauss, prior_mode: str = "fixed", kappa: float = 0.0,
        pi_fixed: np.ndarray | None = None, max_iter: int = 1000, tol: float = 1e-8,
        pi_box: tuple[np.ndarray, np.ndarray] | None = None) -> GEMResult:
    """prior_mode: 'fixed' (π = pi_fixed or source prior), 'joint' (κ=0), 'dirichlet' (κ·π_src pseudo-counts).
    pi_box: optional (low, high) per-class bounds (projected M-step, then renormalised)."""
    z = np.asarray(z, dtype=np.float64)
    n, D = z.shape
    a, b = np.ones(D), np.zeros(D)
    pi = (g.prior if pi_fixed is None else np.asarray(pi_fixed, np.float64)).copy()
    prev = -np.inf
    converged = False
    for it in range(1, max_iter + 1):
        x = a * z + b
        ll = g.class_loglik(x) + np.log(np.maximum(pi, 1e-300))[None]
        lse = logsumexp(ll, axis=1)
        obj = lse.sum() + n * np.log(a).sum()
        if prior_mode == "dirichlet" and kappa > 0:
            obj += np.sum(kappa * g.prior * np.log(np.maximum(pi, 1e-300)))
        r = np.exp(ll - lse[:, None])
        if np.isfinite(prev) and abs(obj - prev) <= tol * abs(prev):
            converged = True
            break
        prev = obj
        a, b = _mstep_affine(z, r, g, n)
        if prior_mode == "joint":
            pi = r.mean(0)
        elif prior_mode == "dirichlet":
            pi = (r.sum(0) + kappa * g.prior) / (n + kappa)
        if pi_box is not None and prior_mode != "fixed":
            pi = np.clip(pi, pi_box[0], pi_box[1])
            pi = pi / pi.sum()
    return GEMResult(a=a, b=b, pi=pi, iters=it, converged=converged, objective=float(obj))


def gem_multibatch(zs: list, g: ClassGauss, priors: list | None, update: str, max_iter: int = 1000,
                   tol: float = 1e-8, box: float | None = None) -> GEMResult:
    """Shared geometry across batches; per-batch priors fixed ('known'), re-estimated ('unknown'),
    or re-estimated within ±box of the given priors ('interval')."""
    zs = [np.asarray(zb, np.float64) for zb in zs]
    D = zs[0].shape[1]
    a, b = np.ones(D), np.zeros(D)
    pis = [np.asarray(p, np.float64).copy() for p in priors] if priors is not None else [g.prior.copy() for _ in zs]
    base = [p.copy() for p in pis]
    prev, converged = -np.inf, False
    n = sum(len(zb) for zb in zs)
    for it in range(1, max_iter + 1):
        rs, obj = [], n * np.log(a).sum()
        for zb, pi in zip(zs, pis):
            ll = g.class_loglik(a * zb + b) + np.log(np.maximum(pi, 1e-300))[None]
            lse = logsumexp(ll, axis=1)
            obj += lse.sum()
            rs.append(np.exp(ll - lse[:, None]))
        if np.isfinite(prev) and abs(obj - prev) <= tol * abs(prev):
            converged = True
            break
        prev = obj
        a, b = _mstep_affine(np.concatenate(zs), np.concatenate(rs), g, n)
        if update in ("unknown", "interval"):
            pis = [r.mean(0) for r in rs]
            if update == "interval":
                pis = [np.clip(p, np.maximum(q - box, 1e-6), q + box) for p, q in zip(pis, base)]
                pis = [p / p.sum() for p in pis]
    return GEMResult(a=a, b=b, pi=np.stack(pis), iters=it, converged=converged, objective=float(obj))


def pooled_affine(z: np.ndarray, src_mean: np.ndarray, src_std: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-coordinate marginal moment matching of the target batch to the source marginal."""
    m, s = z.mean(0), z.std(0)
    dead = (s < 1e-6 * max(float(np.median(s)), 1e-12)) | (src_std < 1e-6 * max(float(np.median(src_std)), 1e-12))
    a = np.clip(src_std / np.where(dead, 1.0, s), A_MIN, A_MAX)
    a[dead] = 1.0
    b = src_mean - a * m
    b[dead] = 0.0
    return a, b


def profile_info_prior(z: np.ndarray, g: ClassGauss, ridge: float = 1e-6) -> float:
    """Average per-sample profile Fisher information of the additive-logit prior parameters given the
    affine geometry, at the identity transform (W2 pre-reg: Ī_{η|θ})."""
    z = np.asarray(z, np.float64)
    ll = g.class_loglik(z) + np.log(g.prior)[None]
    r = np.exp(ll - logsumexp(ll, 1, keepdims=True))
    K = len(g.prior)
    s_eta = r[:, :K - 1] - g.prior[None, :K - 1]                          # (N, K-1)
    resid = (z[:, None, :] - g.mu[None]) / g.var[None]                   # (N, K, D)
    s_b = -(r[:, :, None] * resid).sum(1)                                # d/db
    s_la = s_b * z + 1.0                                                 # d/dlog a
    s_th = np.concatenate([s_b, s_la], 1)
    N = len(z)
    I_ee = s_eta.T @ s_eta / N
    I_et = s_eta.T @ s_th / N
    I_tt = s_th.T @ s_th / N
    I_tt += ridge * np.trace(I_tt) / I_tt.shape[0] * np.eye(I_tt.shape[0])
    prof = I_ee - I_et @ np.linalg.solve(I_tt, I_et.T)
    return float(np.trace(prof) / (K - 1))
