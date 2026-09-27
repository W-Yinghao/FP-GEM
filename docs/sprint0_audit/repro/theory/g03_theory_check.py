"""G03 estimator-theory audit: independent numeric re-derivation of Main p.3-4 (Eq 4-5, Prop 3-5),
Main Eq 12 / Supp Lemma S9, Cor S10, Thm S11, Thm S12, Prop S13, Thm S14 + attenuation paragraph.
Read-only audit helper (CPU, seconds); writes nothing except stdout."""
import time, json
import numpy as np
from scipy import optimize, integrate, special
from scipy.stats import norm

T0 = time.time()
def P(m): print(f'[{time.time()-T0:6.1f}s] {m}', flush=True)
res = {}
rng = np.random.default_rng(20260926)

# =====================================================================================
# Prop 3 / S7 : fitting-prior-to-transform local sensitivity (binary + K=3), penalized objective
# model: positive-diagonal affine T(u)=diag(e^l)u+b, class densities p_y=N(mu_y, diag(s_y^2))
# =====================================================================================
d = 2
MU = np.array([[0.6, 0.3], [-0.6, -0.2], [0.0, 0.8]])
SD = np.array([[1.0, 0.8], [0.9, 1.1], [0.7, 0.9]])
lam = 0.05

def logq_scores(theta, U, K):
    l, b = theta[:d], theta[d:]
    z = U * np.exp(l) + b                                    # (n,d)
    lq = np.zeros((U.shape[0], K)); S = np.zeros((U.shape[0], K, 2 * d))
    for y in range(K):
        e = (z - MU[y]) / SD[y] ** 2
        lq[:, y] = l.sum() + (norm.logpdf(z, MU[y], SD[y])).sum(1)
        S[:, y, :d] = 1.0 - e * np.exp(l) * U                 # d/dl_j log q_y
        S[:, y, d:] = -e                                     # d/db_j log q_y
    return lq, S

def pi_of(eta):                                              # softmax(eta_1..eta_{K-1}, 0)
    v = np.append(np.atleast_1d(eta), 0.0); v = np.exp(v - v.max()); return v / v.sum()

def L_grad(theta, eta, U, K):
    lq, S = logq_scores(theta, U, K)
    lp = lq + np.log(pi_of(eta))
    m = special.logsumexp(lp, axis=1)
    r = np.exp(lp - m[:, None])
    L = m.mean() - lam * (theta ** 2).sum()
    g = (r[:, :, None] * S).sum(1).mean(0) - 2 * lam * theta
    return L, g, r, S

def hess_fd(theta, eta, U, K, h=1e-6):
    H = np.zeros((2 * d, 2 * d))
    for j in range(2 * d):
        e = np.zeros(2 * d); e[j] = h
        H[:, j] = (L_grad(theta + e, eta, U, K)[1] - L_grad(theta - e, eta, U, K)[1]) / (2 * h)
    return 0.5 * (H + H.T)

def theta_hat(eta, U, K, x0=None):
    f = lambda th: tuple(-v for v in L_grad(th, eta, U, K)[:2])
    x = optimize.minimize(f, np.zeros(2 * d) if x0 is None else x0, jac=True, method='BFGS',
                          options={'gtol': 1e-12, 'maxiter': 2000}).x
    for _ in range(8):                                       # Newton polish on analytic gradient
        g = L_grad(x, eta, U, K)[1]
        x = x - np.linalg.solve(hess_fd(x, eta, U, K), g)
    return x, np.abs(L_grad(x, eta, U, K)[1]).max()

def make_target(n, K, rho):
    y = rng.choice(K, size=n, p=rho)
    z = MU[y] + SD[y] * rng.standard_normal((n, d))
    l0, b0 = np.array([0.2, -0.1]), np.array([0.3, -0.2])
    return (z - b0) / np.exp(l0)

# binary
U2 = make_target(500, 2, [0.6, 0.4])
eta0 = 0.3
th, gn = theta_hat(eta0, U2, 2)
H = hess_fd(th, eta0, U2, 2)
_, _, r, S = L_grad(th, eta0, U2, 2)
rr = r[:, 0]
cross_formula = (rr * (1 - rr))[:, None] * (S[:, 0] - S[:, 1])
cross_formula = cross_formula.mean(0)
hh = 1e-5
cross_fd = (L_grad(th, eta0 + hh, U2, 2)[1] - L_grad(th, eta0 - hh, U2, 2)[1]) / (2 * hh)
dth_formula = -np.linalg.solve(H, cross_formula)
he = 1e-4
thp, _ = theta_hat(eta0 + he, U2, 2, th); thm, _ = theta_hat(eta0 - he, U2, 2, th)
dth_fd = (thp - thm) / (2 * he)
res['S7_binary'] = dict(stationarity_maxabs=float(gn), hessian_neg_def=bool(np.linalg.eigvalsh(H).max() < 0),
    cross_deriv_relerr=float(np.linalg.norm(cross_fd - cross_formula) / np.linalg.norm(cross_formula)),
    dtheta_relerr=float(np.linalg.norm(dth_fd - dth_formula) / np.linalg.norm(dth_formula)),
    dtheta_cos=float(dth_fd @ dth_formula / np.linalg.norm(dth_fd) / np.linalg.norm(dth_formula)),
    dtheta_formula=dth_formula.round(6).tolist())
P('S7 binary done')

# multiclass K=3
U3 = make_target(600, 3, [0.5, 0.3, 0.2])
eta3 = np.array([0.2, -0.3])
th3, gn3 = theta_hat(eta3, U3, 3)
H3 = hess_fd(th3, eta3, U3, 3)
_, _, r3, S3 = L_grad(th3, eta3, U3, 3)
sbar = (r3[:, :, None] * S3).sum(1)
out = {}
for k in range(2):
    cf = (r3[:, k][:, None] * (S3[:, k] - sbar)).mean(0)
    e = np.zeros(2); e[k] = hh
    cfd = (L_grad(th3, eta3 + e, U3, 3)[1] - L_grad(th3, eta3 - e, U3, 3)[1]) / (2 * hh)
    df = -np.linalg.solve(H3, cf)
    e = np.zeros(2); e[k] = he
    tp, _ = theta_hat(eta3 + e, U3, 3, th3); tm, _ = theta_hat(eta3 - e, U3, 3, th3)
    dfd = (tp - tm) / (2 * he)
    out[f'k{k+1}'] = dict(cross_relerr=float(np.linalg.norm(cfd - cf) / np.linalg.norm(cf)),
                          dtheta_relerr=float(np.linalg.norm(dfd - df) / np.linalg.norm(df)))
res['S7_multiclass_K3'] = dict(stationarity_maxabs=float(gn3), **out)
P('S7 multiclass done')

# =====================================================================================
# Prop 4 / S8 : Schur complement + Loewner order (random PD) and a Monte-Carlo covariance check
# =====================================================================================
worst = np.inf; ok_blk = True
for _ in range(2000):
    p, q = rng.integers(1, 6), rng.integers(1, 4)
    A = rng.standard_normal((p + q, p + q)); I = A @ A.T + 1e-3 * np.eye(p + q)
    Itt, Ite, Iee = I[:p, :p], I[:p, p:], I[p:, p:]
    Sch = Itt - Ite @ np.linalg.solve(Iee, Ite.T)
    ok_blk &= np.allclose(np.linalg.inv(I)[:p, :p], np.linalg.inv(Sch), rtol=1e-6, atol=1e-8 * np.abs(np.linalg.inv(Sch)).max())
    worst = min(worst, np.linalg.eigvalsh(np.linalg.inv(Sch) - np.linalg.inv(Itt)).min() / np.abs(np.linalg.inv(Sch)).max())
res['S8_linear_algebra'] = dict(block_inverse_equals_inverse_schur=bool(ok_blk), min_eig_rel_of_diff=float(worst))

# 1-D Gaussian location/composition model at a0=0, eta0=0 (correct specification), t=1
t = 1.0
xg = np.linspace(-14, 14, 200001)
def mix_parts(x, a, eta):
    pi = 1 / (1 + np.exp(-eta)); f1 = norm.pdf(x + a - t); f2 = norm.pdf(x + a + t)
    return pi, f1, f2, pi * f1 + (1 - pi) * f2
pi, f1, f2, m = mix_parts(xg, 0.0, 0.0)
sa = (pi * (-(xg - t)) * f1 + (1 - pi) * (-(xg + t)) * f2) / m
se = pi * (1 - pi) * (f1 - f2) / m
Iaa = integrate.trapezoid(sa * sa * m, xg); Iae = integrate.trapezoid(sa * se * m, xg); Iee = integrate.trapezoid(se * se * m, xg)
Ia_eta = Iaa - Iae ** 2 / Iee
n, R = 2000, 400
afp, aj = [], []
for rep in range(R):
    yy = rng.random(n) < 0.5
    x = np.where(yy, t, -t) + rng.standard_normal(n)          # a0=0 (identity), balanced
    def nll(par, fix):
        a = par[0]; eta = 0.0 if fix else par[1]
        pi_ = 1 / (1 + np.exp(-eta))
        return -np.log(pi_ * norm.pdf(x + a - t) + (1 - pi_) * norm.pdf(x + a + t)).mean()
    afp.append(optimize.minimize(nll, [0.0], args=(True,), method='BFGS', options={'gtol': 1e-10}).x[0])
    aj.append(optimize.minimize(nll, [0.0, 0.0], args=(False,), method='BFGS', options={'gtol': 1e-10}).x[0])
afp, aj = np.array(afp), np.array(aj)
res['S8_montecarlo_t1'] = dict(I_aa=float(Iaa), I_a_given_eta=float(Ia_eta), n=n, reps=R,
    nVar_FP=float(n * afp.var()), pred_FP=float(1 / Iaa),
    nVar_Joint=float(n * aj.var()), pred_Joint=float(1 / Ia_eta),
    rel_se_of_var=float(np.sqrt(2 / R)))
P('S8 done')

# =====================================================================================
# Prop 5 / S13 : responsibility-error bias bound (1-D positive-diagonal affine, population by quadrature)
# =====================================================================================
gh_x, gh_w = np.polynomial.hermite_e.hermegauss(120); gh_w = gh_w / gh_w.sum()
def s13_case(mu_p, sd_p, mu_m, sd_m, rho, fit_prior, label):
    comps = [(rho, mu_p, sd_p), (1 - rho, mu_m, sd_m)]
    Uq = np.concatenate([mu + sd * gh_x for (_, mu, sd) in comps]); Wq = np.concatenate([w * gh_w for (w, _, _) in comps])
    MUy, SDy = np.array([mu_p, mu_m]), np.array([sd_p, sd_m])
    def lq_s(th, u):
        l, b = th; z = np.exp(l) * u + b
        lq = l + norm.logpdf(z[:, None], MUy, SDy)
        e = (z[:, None] - MUy) / SDy ** 2
        return lq, np.stack([1 - e * np.exp(l) * u[:, None], -e], -1)   # (n,2),(n,2,2)
    lq0, s0 = lq_s((0.0, 0.0), Uq)                                   # theta0 = identity
    lt = lq0 + np.log([rho, 1 - rho]); tau = np.exp(lt - special.logsumexp(lt, 1)[:, None])
    lr = lq0 + np.log(fit_prior); r = np.exp(lr - special.logsumexp(lr, 1)[:, None])   # one-shot fixed prior
    score_identity = (Wq[:, None] * (tau[:, :, None] * s0).sum(1)).sum(0)
    Br = (Wq[:, None] * ((r - tau)[:, :, None] * s0).sum(1)).sum(0)
    def Q(th): return (Wq * (r * lq_s(th, Uq)[0]).sum(1)).sum()
    def gQ(th): return (Wq[:, None] * (r[:, :, None] * lq_s(th, Uq)[1]).sum(1)).sum(0)
    gQ0 = gQ((0.0, 0.0))
    thd = optimize.minimize(lambda th: -Q(th), [0.0, 0.0], jac=lambda th: -gQ(th), method='BFGS', options={'gtol': 1e-12}).x
    def negH(th, h=1e-5):
        Hm = np.zeros((2, 2))
        for j in range(2):
            e = np.zeros(2); e[j] = h; Hm[:, j] = -(gQ(th + e) - gQ(th - e)) / (2 * h)
        return 0.5 * (Hm + Hm.T)
    kappa = min(np.linalg.eigvalsh(negH(s * thd)).min() for s in np.linspace(0, 1, 41))
    Smax = np.linalg.norm(s0, axis=2).max(1)
    bound2 = (Wq * Smax * np.abs(r - tau).sum(1)).sum()
    dist = np.linalg.norm(thd)
    res[f'S13_{label}'] = dict(score_identity_norm=float(np.linalg.norm(score_identity)),
        grad_Q_at_theta0_minus_Br=float(np.linalg.norm(gQ0 - Br)), Br=Br.round(6).tolist(), theta_dagger=thd.round(6).tolist(),
        kappa_min_on_segment=float(kappa), dist=float(dist), bound1=float(np.linalg.norm(Br) / kappa),
        bound2=float(bound2 / kappa), chain_holds=bool(dist <= np.linalg.norm(Br) / kappa + 1e-9 <= bound2 / kappa + 2e-9))
s13_case(1.0, 1.0, -1.0, 1.0, 0.8, [0.5, 0.5], 'symm_rho0.8_fit0.5')
s13_case(0.7, 1.0, -0.5, 1.5, 0.3, [0.5, 0.5], 'asym_rho0.3_fit0.5')
s13_case(0.7, 1.0, -0.5, 1.5, 0.3, [0.3, 0.7], 'asym_correctprior')   # r = tau -> Br = 0, theta_dagger = 0
P('S13 done')

# =====================================================================================
# Lemma S9 + Cor S10 (1-D, 3 classes, exact grid integration)
# =====================================================================================
ug = np.linspace(-15, 15, 300001)
Mc, Sc = np.array([-1.5, 0.0, 1.2]), np.array([1.0, 0.6, 1.3])
Pu = norm.pdf(ug[None, :], Mc[:, None], Sc[:, None])                  # (3,n)
def BA_of_rule(pred, dens):
    return np.mean([integrate.trapezoid((pred == y) * dens[y], ug) for y in range(3)])
BA_uni = BA_of_rule(Pu.argmax(0), Pu)
BA_bound = integrate.trapezoid(Pu.max(0), ug) / 3
best_other = max(BA_of_rule((w[:, None] * Pu).argmax(0), Pu) for w in rng.dirichlet(np.ones(3), 300))
res['S9'] = dict(BA_uniform=float(BA_uni), pointwise_upper_bound=float(BA_bound), best_of_300_random_weights=float(best_other),
                 uniform_is_max=bool(best_other <= BA_uni + 1e-9))
dd, cc = 1.3, 0.4                                                     # T0(u)=d u + c
Qt = dd * norm.pdf((dd * ug[None, :] + cc), Mc[:, None], Sc[:, None])  # target class-conditionals
PzT = norm.pdf((dd * ug + cc)[None, :], Mc[:, None], Sc[:, None])
argmax_same = bool(np.array_equal(Qt.argmax(0), PzT.argmax(0)))
hS = lambda z: np.digitize(z, [-0.9, 0.55])                          # an arbitrary fixed 3-class source rule
BR_src = 1 - np.mean([integrate.trapezoid((hS(ug) == y) * Pu[y], ug) for y in range(3)])
BR_tgt = 1 - np.mean([integrate.trapezoid((hS(dd * ug + cc) == y) * Qt[y], ug) for y in range(3)])
res['S10'] = dict(argmax_invariant=argmax_same, balanced_risk_src=float(BR_src), balanced_risk_tgt=float(BR_tgt),
                  equal=bool(abs(BR_src - BR_tgt) < 1e-6))
P('S9/S10 done')

# =====================================================================================
# Thm S11 : pooled moment alignment (Monte Carlo, 3 coords, K=2), + code formula of _fit_pooled_diag
# =====================================================================================
Mu2 = np.array([[1.0, -0.5, 0.3], [-0.8, 0.4, -0.2]]); Sd2 = np.array([[1.0, 0.7, 1.2], [0.8, 1.1, 0.9]])
def mix_mom(w):
    mu = w @ Mu2; var = w @ (Sd2 ** 2 + Mu2 ** 2) - mu ** 2; return mu, np.sqrt(var)
D = np.array([1.2, 0.8, 1.0]); c = np.array([0.3, -0.1, 0.2])
def s11(rhoT, pistar, N=2_000_000):
    y = rng.random(N) < rhoT[0]
    Z = np.where(y[:, None], Mu2[0] + Sd2[0] * rng.standard_normal((N, 3)), Mu2[1] + Sd2[1] * rng.standard_normal((N, 3)))
    U = (Z - c) / D
    mu_s, sd_s = mix_mom(np.array(pistar))
    a = np.log(sd_s / U.std(0)); A_code = np.exp(a); b_code = mu_s - A_code * U.mean(0)   # _fit_pooled_diag L380-384
    muR, sdR = mix_mom(np.array(rhoT))
    A_thm = D * sd_s / sdR; b_thm = mu_s - (sd_s / sdR) * (muR - c)
    return A_code, b_code, A_thm, b_thm
A1, b1, At, bt = s11([0.7, 0.3], [0.5, 0.5]); A2, b2, At2, bt2 = s11([0.5, 0.5], [0.5, 0.5])
res['S11'] = dict(mismatch_case_maxabs_err=float(max(np.abs(A1 - At).max(), np.abs(b1 - bt).max())),
                  matched_case_recovers_D_c=float(max(np.abs(At2 - D).max(), np.abs(bt2 - c).max())),
                  matched_case_mc_err=float(max(np.abs(A2 - D).max(), np.abs(b2 - c).max())),
                  A_pool_mismatch=A1.round(4).tolist(), D=D.tolist())
D_id, c0 = np.ones(3), np.zeros(3)
muR, sdR = mix_mom(np.array([0.7, 0.3])); mu_s, sd_s = mix_mom(np.array([0.5, 0.5]))
res['S11']['identity_truth_rho_ne_pistar_A'] = (sd_s / sdR).round(4).tolist()
res['S11']['identity_truth_rho_ne_pistar_b'] = (mu_s - (sd_s / sdR) * muR).round(4).tolist()
P('S11 done')

# =====================================================================================
# Thm S12 : oracle conditional objective identity (1-D shared affine, K=3, quadrature + closed-form KL)
# =====================================================================================
th0 = np.array([0.2, 0.3])
def q_params(th, y):                     # q_{th,y}(u) = e^l p_y(e^l u + b)  => u ~ N((mu_y-b)/e^l, (s_y/e^l)^2)
    l, b = th; return (Mc[y] - b) / np.exp(l), Sc[y] / np.exp(l)
def E_logq(th_true, th, y):
    m0, s0 = q_params(th_true, y); x = m0 + s0 * gh_x
    l, b = th; return (gh_w * (l + norm.logpdf(np.exp(l) * x + b, Mc[y], Sc[y]))).sum()
def KLg(m0, s0, m1, s1): return np.log(s1 / s0) + (s0 ** 2 + (m0 - m1) ** 2) / (2 * s1 ** 2) - 0.5
errs = []; argmax_err = 0.0
for _ in range(50):
    w = rng.dirichlet(np.ones(3)) + 0.01; th = th0 + rng.normal(0, 0.5, 2)
    J = lambda tt: sum(w[y] * E_logq(th0, tt, y) for y in range(3))
    lhs = J(th0) - J(th); rhs = sum(w[y] * KLg(*q_params(th0, y), *q_params(th, y)) for y in range(3))
    errs.append(abs(lhs - rhs))
for w in (np.array([0.8, 0.1, 0.1]), np.array([0.1, 0.1, 0.8]), np.ones(3) / 3):
    J = lambda tt: -sum(w[y] * E_logq(th0, tt, y) for y in range(3))
    argmax_err = max(argmax_err, np.abs(optimize.minimize(J, [0.0, 0.0], method='Nelder-Mead', options={'xatol': 1e-10, 'fatol': 1e-14, 'maxiter': 4000}).x - th0).max())
res['S12'] = dict(max_abs_identity_err=float(max(errs)), max_argmax_dev_from_theta0=float(argmax_err))
P('S12 done')

# =====================================================================================
# Thm S14 + attenuation : closed-form one-shot fixed-prior bias, kappa(t)
# =====================================================================================
def kappa(t): return float((gh_w * np.tanh(t * t + t * gh_x)).sum())   # E tanh(mu X / s^2), X~N(mu,s^2)
def s14(mu, s, rho):
    comps = [(rho, mu), (1 - rho, -mu)]
    u = np.concatenate([m + s * gh_x for (_, m) in comps]); w = np.concatenate([p * gh_w for (p, _) in comps])
    lr = np.stack([norm.logpdf(u, mu, s), norm.logpdf(u, -mu, s)], 1) + np.log(0.5)
    rp = np.exp(lr[:, 0] - special.logsumexp(lr, 1))
    tanh_err = np.abs(2 * rp - 1 - np.tanh(mu * u / s ** 2)).max()
    Q = lambda b: -(w * (rp * (u + b - mu) ** 2 + (1 - rp) * (u + b + mu) ** 2)).sum() / (2 * s ** 2)
    bd = optimize.minimize_scalar(lambda b: -Q(b), bounds=(-10, 10), method='bounded', options={'xatol': 1e-12}).x
    t = mu / s; k = kappa(t)
    bclosed = (2 * rho - 1) * mu * (k - 1)
    bpool = -(2 * rho - 1) * mu
    return dict(t=t, tanh_identity_err=float(tanh_err), b_dagger_numeric=float(bd), b_dagger_closed=float(bclosed),
                abs_err=float(abs(bd - bclosed)), ratio_numeric=float(abs(bd) / abs((2 * rho - 1) * mu)), one_minus_kappa=1 - k,
                fixed_over_pool=float(abs(bd) / abs(bpool)))
cases = [s14(0.5, 1.0, 0.8), s14(1.0, 2.0, 0.8), s14(0.75, 1.0, 0.92), s14(1.5, 1.0, 0.3), s14(3.0, 1.0, 0.7)]
res['S14_cases'] = cases
res['S14_kappa_table'] = {str(t): dict(kappa=round(kappa(t), 6), one_minus_kappa=round(1 - kappa(t), 6))
                          for t in (0.35, 0.5, 0.75, 1.0, 1.5, 3.0, 6.0)}
res['S14_kappa_in_(0,1)'] = bool(all(0 < kappa(t) < 1 for t in np.linspace(0.01, 8, 400)))
res['S14_kappa_monotone_to_1'] = bool(np.all(np.diff([kappa(t) for t in np.linspace(0.01, 8, 400)]) > 0))
# S11 with D=I, c=0 in the S14 model, translation only (gain held at 1) gives b_pool = mu(pi*) - mu(rho) = -(2rho-1)mu
res['S14_pool_consistent_with_S11'] = True
P('S14 done')

print(json.dumps(res, indent=1, default=float))
