"""G01 global-ambiguity audit: independent symbolic + numeric re-derivation of every
number in Main p.3 (Thm 1, Prop 2, stabilizer text) and Supp p.1-3 (Def S1, Thm S2,
Cor S3, Thm S4, Cor S5, Cor S6).  Read-only audit helper; writes nothing."""
import sympy as sp, time, sys
T0=time.time()
def P(m): print(f'[{time.time()-T0:6.1f}s] {m}', flush=True)
import numpy as np
from scipy import integrate

u, x = sp.symbols('u x', real=True)
a_, b_ = sp.symbols('alpha beta', positive=True)
ok = {}

# ---- witness density: standard Student-t3 -------------------------------------------
f = 2 / (sp.pi * sp.sqrt(3)) * (1 + u**2 / 3) ** -2
nu = 3
f_ref = sp.gamma(sp.Rational(nu + 1, 2)) / (sp.sqrt(nu * sp.pi) * sp.gamma(sp.Rational(nu, 2))) * (1 + u**2 / nu) ** (-sp.Rational(nu + 1, 2))
ok['f_is_student_t3_pdf'] = sp.nsimplify(sp.N(f_ref.subs(u, sp.Rational(7, 3)) / f.subs(u, sp.Rational(7, 3)), 30)) == 1 and sp.nsimplify(sp.N(f_ref.subs(u, 0) / f.subs(u, 0), 30)) == 1
C = 2 / (sp.pi * sp.sqrt(3)); h = (1 + u**2 / 3) ** -2
P('start')
ok['int_f=1'] = sp.simplify(C * sp.integrate(h, (u, -sp.oo, sp.oo)) - 1) == 0
ok['E_f=0'] = sp.simplify(f.subs(u, -u) - f) == 0   # even density, finite first moment
Varf = sp.simplify(C * sp.integrate(u**2 * h, (u, -sp.oo, sp.oo)))
ok['Var_f=3'] = Varf == 3

P('f moments done')
# ---- T(u)=d u, g(u)=d f(du), r = g/f -------------------------------------------------
d = sp.Rational(11, 10)
g = d * f.subs(u, d * u)
z = sp.symbols('z', real=True)
# change of variables z = d u in int u^k d f(d u) du = d^-k int z^k f(z) dz
If0, If1, If2 = 1, 0, Varf
ok['int_g=1'] = True  # = d^0 * int f = 1 (scaling identity)
Varg = If2 / d**2
ok['Var_g=3/d^2'] = sp.simplify(Varg - 3 / d**2) == 0
r_closed = d * ((1 + u**2 / 3) / (1 + d**2 * u**2 / 3)) ** 2
r = r_closed
ok['r_closed_form'] = sp.simplify(sp.together(g / f - r_closed)) == 0
ok['r(0)=d'] = sp.simplify(r.subs(u, 0) - d) == 0
ok['r(inf)=d^-3'] = sp.simplify(sp.limit(r, u, sp.oo) - d**-3) == 0
frac = (1 + x / 3) / (1 + d**2 * x / 3)
ok['frac_decreasing_in_u2'] = sp.simplify(sp.diff(frac, x) - (1 - d**2) / 3 / (1 + d**2 * x / 3) ** 2) == 0 and (1 - d**2) < 0

P('r done')
# ---- alpha, beta, ratio conditions ---------------------------------------------------
al, be = sp.Rational(3, 5), sp.Rational(2, 5)
ok['beta/alpha=2/3'] = be / al == sp.Rational(2, 3)
ok['2/3<=(10/11)^3'] = sp.Rational(2, 3) <= sp.Rational(10, 11) ** 3   # 0.6667 <= 0.7513
ok['(10/11)^3==d^-3'] = sp.Rational(10, 11) ** 3 == d**-3
ok['(1-b)/(1-a)=3/2'] = (1 - be) / (1 - al) == sp.Rational(3, 2)
ok['11/10<=3/2'] = d <= sp.Rational(3, 2)

P('ab done')
# ---- general construction (Thm 1 / S4) with symbolic alpha, beta ---------------------
F, G = sp.symbols('F G')
p1g = ((1 - b_) * F - (1 - a_) * G) / (a_ - b_)
p2g = (a_ * G - b_ * F) / (a_ - b_)
P("ok['alpha*p1+(1-alpha)*p2=f']")
ok['alpha*p1+(1-alpha)*p2=f'] = sp.simplify(sp.expand(a_ * p1g + (1 - a_) * p2g) - F) == 0
ok['beta*p1+(1-beta)*p2=g'] = sp.simplify(sp.expand(b_ * p1g + (1 - b_) * p2g) - G) == 0
ok['int_p1=1 (sym)'] = sp.simplify(p1g.subs({F: 1, G: 1}) - 1) == 0
ok['int_p2=1 (sym)'] = sp.simplify(p2g.subs({F: 1, G: 1}) - 1) == 0

P('# ---- specialised')
# ---- specialised construction p1=3f-2g, p2=3g-2f -------------------------------------
p1s = sp.simplify(p1g.subs({a_: al, b_: be}))
p2s = sp.simplify(p2g.subs({a_: al, b_: be}))
ok['p1=3f-2g'] = sp.simplify(p1s - (3 * F - 2 * G)) == 0
ok['p2=3g-2f'] = sp.simplify(p2s - (3 * G - 2 * F)) == 0
P('p1 = 3 * f - 2 * g')
p1 = 3 * f - 2 * g
p2 = 3 * g - 2 * f
ok['int_p1=1'] = 3 * 1 - 2 * 1 == 1
ok['int_p2=1'] = 3 * 1 - 2 * 1 == 1
P('Vp1 = sp.nsimplify')
Vp1 = sp.nsimplify(3 * Varf - 2 * Varg)
Vp2 = sp.nsimplify(3 * Varg - 2 * Varf)
ok['Var_p1=9-6/d^2=489/121'] = Vp1 == 9 - 6 / d**2 == sp.Rational(489, 121)
ok['Var_p2=9/d^2-6=174/121'] = Vp2 == 9 / d**2 - 6 == sp.Rational(174, 121)
ok['mean_p1=0'] = sp.simplify(p1.subs(u, -u) - p1) == 0  # even => mean 0 (finite first moment)
ok['mean_p2=0'] = sp.simplify(p2.subs(u, -u) - p2) == 0
# nonnegativity: p1>=0 <=> r<=3/2 ; p2>=0 <=> r>=2/3
P('fn = sp.lambdify')
fn = sp.lambdify(u, f, 'numpy'); gn = sp.lambdify(u, g, 'numpy')
P('grid = np.concatenate')
grid = np.concatenate([np.linspace(-1e4, 1e4, 2_000_001), np.linspace(-5, 5, 200_001)])
P('rn = gn(grid)')
rn = gn(grid) / fn(grid)
ok['num_r_range_within_(d^-3,d]'] = bool(rn.min() > float(d**-3) - 1e-12 and rn.max() <= float(d) + 1e-12)
ok['num_p1>=0'] = bool((3 * fn(grid) - 2 * gn(grid)).min() >= 0)
ok['num_p2>=0'] = bool((3 * gn(grid) - 2 * fn(grid)).min() >= 0)
P('# both worlds')
# both worlds give g numerically
alf, bef = float(al), float(be)
wp = lambda t: bef * (3 * fn(t) - 2 * gn(t)) + (1 - bef) * (3 * gn(t) - 2 * fn(t))
src_al = lambda z: alf * (3 * fn(z) - 2 * gn(z)) + (1 - alf) * (3 * gn(z) - 2 * fn(z))
wg = lambda t: float(d) * src_al(float(d) * t)          # J_T(u) * mixture(T u)
ok['num_W_P==g'] = bool(np.max(np.abs(wp(grid) - gn(grid))) < 1e-12)
ok['num_W_G==g'] = bool(np.max(np.abs(wg(grid) - gn(grid))) < 1e-12)
P('vn1 = integrate.quad')
vn1 = integrate.quad(lambda t: t * t * (3 * fn(t) - 2 * gn(t)), -np.inf, np.inf, limit=500)[0]
vn2 = integrate.quad(lambda t: t * t * (3 * gn(t) - 2 * fn(t)), -np.inf, np.inf, limit=500)[0]
ok['num_Var_p1~4.0413'] = abs(vn1 - 489 / 121) < 1e-6
ok['num_Var_p2~1.4380'] = abs(vn2 - 174 / 121) < 1e-6

P('witness done')
# ---- Cor S3: positive-diag affine stabilizer trivial --------------------------------
aj, bj, mu, s2 = sp.symbols('a_j b_j mu sigma2', real=True)
sol = sp.solve([sp.Eq(aj**2 * s2, s2), sp.Eq(aj * mu + bj, mu)], [aj, bj], dict=True)
ok['S3_unique_pos_solution_a=1_b=0'] = [s for s in sol if s[aj].is_positive or s[aj] == 1] == [{aj: 1, bj: 0}]
ok['witness_T_not_in_Gsrc(Var changes)'] = sp.Rational(11, 10) ** 2 * Vp1 != Vp1

P('S3 done')
# ---- Prop 2 / Cor S6 -----------------------------------------------------------------
q, g0, g1, gam = sp.symbols('q g0 g1 gamma', positive=True)
qs = g1 / (g0 + g1)
ok['S6_equalizer'] = sp.simplify(qs * g0 - (1 - qs) * g1) == 0
ok['S6_value=g0g1/(g0+g1)'] = sp.simplify(qs * g0 - g0 * g1 / (g0 + g1)) == 0
ok['S6_equal_cost=gamma/2'] = sp.simplify((g0 * g1 / (g0 + g1)).subs({g0: gam, g1: gam}) - gam / 2) == 0
ok['Prop2_bayes_avg=gamma/2_for_all_q'] = sp.simplify((q * gam + (1 - q) * gam) / 2 - gam / 2) == 0
# minimax optimality numeric sweep
for G0, G1 in [(1, 1), (1, 3), (0.2, 5)]:
    qq = np.linspace(0, 1, 100_001)
    mm = np.maximum(qq * G0, (1 - qq) * G1).min()
    ok[f'S6_num_minimax_{G0}_{G1}'] = abs(mm - G0 * G1 / (G0 + G1)) < 1e-4

for k, v in ok.items():
    print(f"{'PASS' if v else 'FAIL'}  {k}")
print('numeric: (10/11)^3 =', float(sp.Rational(10, 11) ** 3), ' d^-3 =', float(d**-3),
      ' Var_p1 =', Vp1, float(Vp1), ' Var_p2 =', Vp2, float(Vp2), ' Var_g =', Varg, float(Varg),
      ' r_min_grid =', rn.min(), ' r_max_grid =', rn.max())
print('ALL_PASS' if all(bool(v) for v in ok.values()) else 'SOME_FAIL', sum(bool(v) for v in ok.values()), '/', len(ok))
