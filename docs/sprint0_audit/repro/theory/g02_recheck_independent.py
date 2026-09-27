"""Independent adversarial re-check of Theorem 6 / S15 (G02), double-precision SciPy only.

Different method from g02_theorem6_audit.py (sympy/mpmath): here all Fisher blocks are
obtained by numerically differentiating log m_{a,eta} (central differences) and integrating
with scipy.integrate.quad; the fixed-t coefficients A, K, B are obtained by direct
numerical KL minimisation (scipy.optimize.minimize_scalar) with no Fisher shortcut.
Also checks revision-doc numbers (v3 6.3 / 6.4, v4 P2/P3, v2 3.7).
"""
import json, math
import numpy as np
from scipy import integrate, optimize
from scipy.stats import norm

phi, Phi = norm.pdf, norm.cdf
LIM = 14.0


def m(x, a, eta, t):
    p = 1.0 / (1.0 + math.exp(-eta))
    return p * phi(x + a - t) + (1 - p) * phi(x + a + t)


def m0(x, t):
    return m(x, 0.0, 0.0, t)


def score_fd(x, t, h=1e-5):
    la = (math.log(m(x, h, 0, t)) - math.log(m(x, -h, 0, t))) / (2 * h)
    le = (math.log(m(x, 0, h, t)) - math.log(m(x, 0, -h, t))) / (2 * h)
    return la, le


def E(f, t):
    return integrate.quad(lambda x: f(x) * m0(x, t), -LIM - t, LIM + t, epsabs=1e-14, epsrel=1e-12, limit=400)[0]


def S(t):
    return E(lambda x: 1.0 / math.cosh(t * x) ** 2, t)


def fisher_fd(t):
    Iaa = E(lambda x: score_fd(x, t)[0] ** 2, t)
    Iae = E(lambda x: score_fd(x, t)[0] * score_fd(x, t)[1], t)
    Iee = E(lambda x: score_fd(x, t)[1] ** 2, t)
    return Iaa, Iae, Iee


def KL(eta, a, t):
    # KL(P_{0,eta} || P_{a,0})
    return integrate.quad(lambda x: m(x, 0, eta, t) * (math.log(m(x, 0, eta, t)) - math.log(m(x, a, 0, t))),
                          -LIM - t - 1, LIM + t + 1, epsabs=1e-16, epsrel=1e-13, limit=400)[0]


def BA(a, t):
    return 0.5 * (Phi(t + a) + Phi(t - a))


out = {"fisher": [], "direct": [], "doc_numbers": {}}
for t in [0.1, 0.2, 0.35, 0.5, 1.0]:
    s = S(t)
    Iaa, Iae, Iee = fisher_fd(t)
    closed = (1 - t * t * s, -0.5 * t * s, 0.25 * (1 - s))
    Ia_e = Iaa - Iae ** 2 / Iee
    Ie_a = Iee - Iae ** 2 / Iaa
    M = np.array([[Iaa, Iae], [Iae, Iee]])
    lam_raw = np.linalg.eigvalsh(M)[0]
    # rescaled eta' = eta * t/2 => score s_eta' = s_eta/(t/2); information in commensurate units
    D = np.diag([1.0, 2.0 / t])
    lam_resc = np.linalg.eigvalsh(D @ M @ D)[0]
    out["fisher"].append(dict(t=t, S=s,
                              Iaa_fd=Iaa, Iaa_closed=closed[0],
                              Iae_fd=Iae, Iae_closed=closed[1],
                              Iee_fd=Iee, Iee_closed=closed[2],
                              Ia_given_eta=Ia_e, Ia_given_eta_closed=1 - t * t * s / (1 - s),
                              series_23t4_m2t6=2 / 3 * t ** 4 - 2 * t ** 6,
                              Ieta_given_a=Ie_a, Ieta_given_a_closed=(1 - (1 + t * t) * s) / (4 * (1 - t * t * s)),
                              lam_min_raw=lam_raw, t6_over_6=t ** 6 / 6,
                              lam_min_rescaled_eta=lam_resc, t4_over_3=t ** 4 / 3,
                              VOI_factor_Iaa_over_Ia_eta=closed[0] / Ia_e,
                              label_equiv_0p25_over_Ieta_a=0.25 / Ie_a))

for t in [0.3, 0.5, 1.0]:
    s = S(t)
    A = -2 * t * s / (1 - t * t * s)
    K = 2 * (1 - (1 + t * t) * s) / (1 - t * t * s)
    B = 2 * t ** 3 * phi(t) * s ** 2 / (1 - t * t * s) ** 2
    for d in [1e-3, 3e-4]:
        eta = math.log((1 + 2 * d) / (1 - 2 * d))
        r = optimize.minimize_scalar(lambda a: KL(eta, a, t), bracket=(-5 * d, 0.0, 5 * d), tol=1e-12)
        a_star = r.x
        out["direct"].append(dict(t=t, delta=d, a_over_d=a_star / d, A=A,
                                  KL_over_d2=r.fun / d ** 2, K=K,
                                  dBER_over_d2=(BA(0, t) - BA(a_star, t)) / d ** 2, B=B))

# revision-doc numbers
t = 0.35
s = S(t)
out["doc_numbers"]["v3_6.3_S(0.35)"] = s
out["doc_numbers"]["v3_6.3_(1+t2)S(0.35)"] = (1 + t * t) * s
out["doc_numbers"]["v3_6.3_rounds_known_geometry_log0.1/logS"] = math.log(0.1) / math.log(s)
out["doc_numbers"]["v3_6.3_rounds_joint_slow"] = math.log(0.1) / math.log((1 + t * t) * s)
t = 0.5
s = S(t)
r_t = t * t * s
out["doc_numbers"]["v3_6.4_Bk_over_Gk_t0.5"] = -2 * t * s / (1 - r_t)
for k in [1, 3, 20]:
    out["doc_numbers"][f"v3_6.4_G_{k}"] = 1 - r_t ** k
    out["doc_numbers"][f"v3_6.4_B_{k}"] = -2 * t * s / (1 - r_t) * (1 - r_t ** k)
# EM Jacobian S*[[t^2, t/2],[2t,1]] eigenvalues
for t in [0.35, 0.5]:
    s = S(t)
    J = s * np.array([[t * t, t / 2], [2 * t, 1.0]])
    out["doc_numbers"][f"v3_6.2_J_EM_eigs_t{t}"] = sorted(np.linalg.eigvals(J).real.tolist())
json.dump(out, open(__file__.replace('.py', '.json'), 'w'), indent=1)
for row in out["fisher"]:
    print({k: (float(f"{v:.10g}") if isinstance(v, float) else v) for k, v in row.items()})
for row in out["direct"]:
    print({k: (float(f"{v:.10g}") if isinstance(v, float) else v) for k, v in row.items()})
for k, v in out["doc_numbers"].items():
    print(k, v)
