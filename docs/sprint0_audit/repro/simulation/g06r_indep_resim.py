"""G06 adversarial re-check: INDEPENDENT re-implementation of the paper's controlled
Gaussian prior-mismatch study (main Sec 5.1 eqs 13-16, Supp Table S1), written from the
paper text only. NOT the authors' code (which is not on the server). Purpose: test whether
Table S3 numbers are reproducible within Monte-Carlo error under the stated protocol.

Model: Y in {-1,+1}, Z|Y=y ~ N(y t e1, I4), pi_src=(1/2,1/2); target Pr(Y=+1)=rho;
U = T^{-1}_{theta0}(Z), T_theta(u) = diag(e^l) u + b, l0=(log1.25,log0.8,0,0), b0=(.5,-.25,0,0).
Coordinates 2..4 are class-independent -> closed-form MLE identical for FP and Joint.
Coordinate 1: FP fixes eta=0 (pi_+=1/2); Joint fits eta in [-10,10]; L-BFGS-B, analytic grads.
BA: analytic, balanced Gaussian evaluation distribution, uniform decision weights -> sign rule.
Seeds: SHA256('20270728|nA|t|rho|s') first 8 bytes little-endian (string formatting of t/rho
unknown; we use Python repr of the float, e.g. '0.5'), sampling order unknown -> only MC-level
agreement is testable.
"""
import hashlib, sys, json, time
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, log_ndtr
from scipy.stats import norm, t as student_t

L0 = np.array([np.log(1.25), np.log(0.8), 0.0, 0.0])
B0 = np.array([0.5, -0.25, 0.0, 0.0])
BOUNDS_FP = [(-4, 4), (-8, 8)]
BOUNDS_J = [(-4, 4), (-8, 8), (-10, 10)]
OPTS = dict(maxiter=2000, maxls=50, ftol=1e-13, gtol=1e-7)


def seed_of(nA, t, rho, s):
    h = hashlib.sha256(f"20270728|{nA}|{t}|{rho}|{s}".encode()).digest()
    return int.from_bytes(h[:8], "little")


def negll(params, u, t, fixed_eta=None):
    if fixed_eta is None:
        l, b, eta = params
    else:
        l, b = params; eta = fixed_eta
    n = u.size
    el = np.exp(l)
    z = el * u + b
    lp = np.log(expit(eta)) - 0.5 * (z - t) ** 2
    lm = np.log(expit(-eta)) - 0.5 * (z + t) ** 2
    m = np.maximum(lp, lm)
    lse = m + np.log(np.exp(lp - m) + np.exp(lm - m))
    obj = lse.sum() + n * l - n * 0.5 * np.log(2 * np.pi)
    r = np.exp(lp - lse)  # posterior of +1
    dz = -z + t * (2 * r - 1)
    g_l = np.sum(dz * (z - b)) + n
    g_b = np.sum(dz)
    if fixed_eta is None:
        g_eta = np.sum(r - expit(eta))
        return -obj / n, -np.array([g_l, g_b, g_eta]) / n
    return -obj / n, -np.array([g_l, g_b]) / n


def mm_start(u, t, eta):
    p = expit(eta)
    mean_m = (2 * p - 1) * t
    var_m = 1 + 4 * p * (1 - p) * t * t
    s = np.sqrt(var_m) / np.std(u)
    return np.log(s), mean_m - s * np.mean(u)


def pgnorm(x, g, bounds):
    # box-projected gradient infinity norm
    x = np.asarray(x); g = np.asarray(g)
    pg = g.copy()
    for i, (lo, hi) in enumerate(bounds):
        if x[i] <= lo + 1e-7 and g[i] > 0: pg[i] = 0
        if x[i] >= hi - 1e-7 and g[i] < 0: pg[i] = 0
    return np.max(np.abs(pg))


def best_of(starts, fun, bounds, jac_args):
    res = []
    seen = set()
    for x0 in starts:
        key = tuple(np.round(x0, 12))
        if key in seen: continue
        seen.add(key)
        x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
        r = minimize(fun, x0, args=jac_args, jac=True, method="L-BFGS-B", bounds=bounds, options=OPTS)
        f, g = fun(r.x, *jac_args)
        res.append((f, r.x, pgnorm(r.x, g, bounds)))
    ok = [x for x in res if np.isfinite(x[0]) and x[2] <= 1e-7 * 10]  # scaled objective -> relax
    pool = ok if ok else res
    f, x, _ = min(pool, key=lambda z: z[0])
    return x, bool(ok)


def fit_fp(u, t):
    starts = [np.array([0.0, 0.0]), np.array(mm_start(u, t, 0.0))]
    x, ok = best_of(starts, negll, BOUNDS_FP, (u, t, 0.0))
    return x, ok


def fit_joint(u, t, fp_x):
    starts = [np.array([*mm_start(u, t, e), e]) for e in (-8, -4, -1, 0, 1, 4, 8)]
    starts.append(np.array([fp_x[0], fp_x[1], 0.0]))
    starts.append(np.array([0.0, 0.0, 0.0]))
    x, ok = best_of(starts, negll, BOUNDS_J, (u, t, None))
    return x, ok


def ba(l1, b1, t):
    s = np.exp(l1 - L0[0]); c = b1 - s * B0[0]
    thr = -c / s
    return 0.5 * (norm.cdf(t - thr) + norm.cdf(t + thr))


def nuisance_mse(U):
    # closed-form MLE for coords 2..4: T_j(u)=e^l u + b ~ N(0,1)
    tot = 0.0
    for j in (1, 2, 3):
        sd = np.std(U[:, j]); l = -np.log(sd); b = -np.exp(l) * np.mean(U[:, j])
        tot += (l - L0[j]) ** 2 + (b - B0[j]) ** 2
    return tot


def run_cell(nA, t, rho, S):
    rows = []
    for s in range(S):
        rng = np.random.default_rng(seed_of(nA, t, rho, s))
        y = np.where(rng.random(nA) < rho, 1.0, -1.0)
        Z = rng.standard_normal((nA, 4)); Z[:, 0] += y * t
        U = (Z - B0) / np.exp(L0)
        fx, fok = fit_fp(U[:, 0], t)
        jx, jok = fit_joint(U[:, 0], t, fx)
        nm = nuisance_mse(U)
        mse_fp = (fx[0] - L0[0]) ** 2 + (fx[1] - B0[0]) ** 2 + nm
        mse_j = (jx[0] - L0[0]) ** 2 + (jx[1] - B0[0]) ** 2 + nm
        rows.append((mse_fp, mse_j, ba(fx[0], fx[1], t), ba(jx[0], jx[1], t), jx[2], fok, jok))
    a = np.array([r[:5] for r in rows])
    d_mse = a[:, 0] - a[:, 1]; d_ba = 100 * (a[:, 2] - a[:, 3])
    tc = student_t.ppf(0.975, S - 1)
    def ci(v):
        m = v.mean(); h = tc * v.std(ddof=1) / np.sqrt(S); return [m, m - h, m + h]
    return dict(nA=nA, t=t, rho=rho, S=S, mse_fp=a[:, 0].mean(), mse_joint=a[:, 1].mean(),
                d_mse=ci(d_mse), d_ba_pp=ci(d_ba), eta_sd=a[:, 4].std(ddof=1),
                eta_boundary=int(np.sum(np.abs(a[:, 4]) >= 10 - 1e-7)),
                fp_ok=int(sum(r[5] for r in rows)), joint_ok=int(sum(r[6] for r in rows)))


if __name__ == "__main__":
    S = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    cells = [(t, rho) for rho in (0.5, 0.7, 0.92) for t in (0.35, 0.5, 0.75, 1.5)]
    if len(sys.argv) > 2:
        cells = cells[: int(sys.argv[2])]
    out = []
    for t, rho in cells:
        t0 = time.time()
        r = run_cell(500, t, rho, S)
        r["sec"] = round(time.time() - t0, 1)
        out.append(r)
        print(json.dumps(r), flush=True)
    json.dump(out, open(__file__.replace(".py", "_out.json"), "w"), indent=1)
