"""Independent numeric re-check of G01 (Thm 1 / S4 / S5 / S6), written without reusing
g01_theory_check.py.  Replaces its hard-coded / trivial checks (int_g=1 set to True,
int_p=3-2) with real quadrature, and checks the S6 minimax with a brute-force grid over
randomized selectors.  Read-only; prints only."""
import numpy as np
from scipy import integrate, stats
from fractions import Fraction as Fr

res = {}
d = 1.1
f = lambda u: stats.t.pdf(u, df=3)                 # scipy's Student-t3, not the paper formula
fpaper = lambda u: 2 / (np.pi * np.sqrt(3)) * (1 + u * u / 3) ** -2
g = lambda u: d * f(d * u)
uu = np.linspace(-50, 50, 200001)
res['paper_f == scipy t3 pdf'] = np.max(np.abs(fpaper(uu) - f(uu))) < 1e-14
q = lambda h, k=0: integrate.quad(lambda t: t ** k * h(t), -np.inf, np.inf, limit=800, epsabs=1e-12, epsrel=1e-12)[0]
res['int_f=1 (quad)'] = abs(q(f) - 1) < 1e-9
res['int_g=1 (quad)'] = abs(q(g) - 1) < 1e-9
res['Var_f=3 (quad)'] = abs(q(f, 2) - 3) < 1e-6
res['Var_g=300/121 (quad)'] = abs(q(g, 2) - 300 / 121) < 1e-6
al, be = 0.6, 0.4
p1 = lambda u: ((1 - be) * f(u) - (1 - al) * g(u)) / (al - be)
p2 = lambda u: (al * g(u) - be * f(u)) / (al - be)
res['int_p1=1 (quad)'] = abs(q(p1) - 1) < 1e-9
res['int_p2=1 (quad)'] = abs(q(p2) - 1) < 1e-9
res['mean_p1=0 (quad)'] = abs(q(p1, 1)) < 1e-9
res['mean_p2=0 (quad)'] = abs(q(p2, 1)) < 1e-9
res['Var_p1=489/121 (quad)'] = abs(q(p1, 2) - 489 / 121) < 1e-6
res['Var_p2=174/121 (quad)'] = abs(q(p2, 2) - 174 / 121) < 1e-6
big = np.concatenate([np.linspace(-1e5, 1e5, 400001), uu])
res['p1>=0 grid'] = p1(big).min() >= -1e-18
res['p2>=0 grid'] = p2(big).min() >= -1e-18
res['p1<=3f'] = np.all(p1(big) <= 3 * f(big) + 1e-18)
res['p2<=3g'] = np.all(p2(big) <= 3 * g(big) + 1e-18)
# world P: target = beta p1 + (1-beta) p2 ; world G: U = T^{-1}(Z), Z ~ alpha p1+(1-alpha) p2
wP = lambda u: be * p1(u) + (1 - be) * p2(u)
src = lambda z: al * p1(z) + (1 - al) * p2(z)
res['source mixture == f'] = np.max(np.abs(src(big) - f(big))) < 1e-15
res['W_P == g'] = np.max(np.abs(wP(big) - g(big))) < 1e-15
# Monte-Carlo of world G: sample Z from source mixture via labelled classes -> U = Z/d
rng = np.random.default_rng(0)
N = 400000
# sample Z ~ f exactly (source mixture == f), then U = Z/d ; compare to direct sampling from g
Z = rng.standard_t(3, size=N); U_G = Z / d
# world P: sample labels ~ beta, then class-conditional via rejection from 3f (p1<=3f) / 3g (p2<=3g)
def rej(pdf, env_pdf_sampler, env_pdf, M, n):
    out = []
    while sum(len(o) for o in out) < n:
        x = env_pdf_sampler(4 * n); acc = rng.uniform(size=x.size) < pdf(x) / (M * env_pdf(x)); out.append(x[acc])
    return np.concatenate(out)[:n]
n1 = rng.binomial(N, be)
X1 = rej(p1, lambda m: rng.standard_t(3, size=m), f, 3, n1)
X2 = rej(p2, lambda m: rng.standard_t(3, size=m) / d, g, 3, N - n1)
U_P = np.concatenate([X1, X2])
ks = stats.ks_2samp(U_P, U_G)
res['MC KS W_P vs W_G (p>0.01)'] = ks.pvalue > 0.01
# exact rational checks
D = Fr(11, 10)
res['2/3 <= (10/11)^3'] = Fr(2, 3) <= (1 / D) ** 3
res['11/10 <= 3/2'] = D <= Fr(3, 2)
res['9-6/d^2 = 489/121'] = 9 - 6 / D ** 2 == Fr(489, 121)
res['9/d^2-6 = 174/121'] = 9 / D ** 2 - 6 == Fr(174, 121)
# S3: stabilizer check for T(u)=1.1u on p1: pushforward variance changes
res['T#p1 != p1 (var)'] = abs(d * d * 489 / 121 - 489 / 121) > 1e-3
# S6 brute force: selector = prob q of choosing T (same in both worlds)
for g0, g1 in [(1, 1), (2, 1), (0.3, 7)]:
    qq = np.linspace(0, 1, 1_000_001)
    v = np.maximum(qq * g0, (1 - qq) * g1)
    res[f'S6 minimax ({g0},{g1})'] = abs(v.min() - g0 * g1 / (g0 + g1)) < 1e-5 and abs(qq[v.argmin()] - g1 / (g0 + g1)) < 1e-5
# Prop 2: Bayes average under equal prior is gamma/2 for every q
gam = 0.37
res['Prop2 avg=gamma/2 all q'] = np.allclose((qq * gam + (1 - qq) * gam) / 2, gam / 2)
# Gaussian f cannot satisfy bounded ratio (scope note)
lr = lambda u: np.log(d) + stats.norm.logpdf(d * u) - stats.norm.logpdf(u)   # log r for Gaussian f
res['Gaussian ratio unbounded below (scope)'] = lr(40.0) < -150 and lr(400.0) < lr(40.0)
for k, v in res.items():
    print(('PASS ' if v else 'FAIL ') + k)
print('KS', ks.statistic, ks.pvalue)
print('ALL_PASS' if all(res.values()) else 'SOME_FAIL', sum(map(bool, res.values())), '/', len(res))
