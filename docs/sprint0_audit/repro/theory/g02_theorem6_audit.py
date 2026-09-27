"""G02 audit: independent symbolic + numeric re-derivation of Theorem 6 / Theorem S15
("When Priors Push Geometry", main p.4-5 sec 3.4; supp p.7-8 sec G).

Audit-only script (scratchpad). No server artifact validates these series; this is
the auditor's own check. Symbolic part: sympy. Numeric part: mpmath quadrature at
fixed t, direct KL minimisation (no Fisher shortcut) for A(t), K(t), B(t).
"""
import json
import sympy as sp
import mpmath as mp

out = {}
t, x, a, eta, dlt, z = sp.symbols('t x a eta delta z', real=True)

# ---------- A. scores from the model density (symbolic differentiation) ----------
phi = lambda u: sp.exp(-u**2 / 2) / sp.sqrt(2 * sp.pi)
pi_eta = 1 / (1 + sp.exp(-eta))
m = pi_eta * phi(x + a - t) + (1 - pi_eta) * phi(x + a + t)
s_a = sp.diff(sp.log(m), a).subs({a: 0, eta: 0})
s_eta = sp.diff(sp.log(m), eta).subs({a: 0, eta: 0})
chk_sa = sp.simplify((s_a - (-x + t * sp.tanh(t * x))).rewrite(sp.exp))
chk_se = sp.simplify((s_eta - sp.tanh(t * x) / 2).rewrite(sp.exp))
out['score_s_a_equals_-z+tH'] = bool(chk_sa == 0)
out['score_s_eta_equals_H/2'] = bool(chk_se == 0)

# ---------- B. sech^2 series and Gaussian moments of W = t^2 + t*eps ----------
sech2 = sp.series(sp.sech(x)**2, x, 0, 13).removeO()
out['sech2_coeffs_x0_x2_x4_x6_x8_x10_x12'] = [str(sech2.coeff(x, k)) for k in (0, 2, 4, 6, 8, 10, 12)]
gm = {0: 1, 1: 0, 2: 1, 3: 0, 4: 3, 5: 0, 6: 15, 7: 0, 8: 105, 9: 0, 10: 945, 11: 0, 12: 10395}
def EW(k):
    return sp.expand(sum(sp.binomial(k, j) * (t**2)**(k - j) * t**j * gm[j] for j in range(k + 1)))
out['EW2'] = str(EW(2)); out['EW4'] = str(EW(4)); out['EW6'] = str(EW(6)); out['EW8'] = str(EW(8))

# S(t) = E sech^2(W): termwise (asymptotic) expansion; keep through t^10
S_ser = sp.expand(sum(sech2.coeff(x, k) * EW(k) for k in range(0, 13, 2)))
S_ser = sum(S_ser.coeff(t, k) * t**k for k in range(0, 11))
out['S_series_to_t10'] = str(S_ser)
S = S_ser  # use as truncated series symbol

def ser(expr, n):
    return sp.series(expr, t, 0, n).removeO()

Iaa = 1 - t**2 * S
Iae = -t * S / 2
Iee = (1 - S) / 4
Ia_given_e = ser(Iaa - Iae**2 / Iee, 9)
Ia_given_e_closed = ser(1 - t**2 * S / (1 - S), 9)
out['Iaa_series'] = str(ser(Iaa, 5))
out['Ia|eta_series_to_t8'] = str(Ia_given_e)
out['Ia|eta_closed_form_equals_schur'] = bool(sp.expand(Ia_given_e - Ia_given_e_closed) == 0)
Ie_given_a = ser(Iee - Iae**2 / Iaa, 11)
Ie_given_a_closed = ser((1 - (1 + t**2) * S) / (4 * (1 - t**2 * S)), 11)
out['Ieta|a_series'] = str(Ie_given_a)
out['Ieta|a_closed_form_equals_schur'] = bool(sp.expand(Ie_given_a - Ie_given_a_closed) == 0)

eta_d = sp.log((1 + 2 * dlt) / (1 - 2 * dlt))
out['eta_delta_series'] = str(sp.series(eta_d, dlt, 0, 5))

A_t = -2 * t * S / (1 - t**2 * S)
K_t = 2 * (1 - (1 + t**2) * S) / (1 - t**2 * S)
out['A_from_Iae/Iaa*4'] = bool(sp.expand(ser(4 * Iae / Iaa, 10) - ser(A_t, 10)) == 0)
out['K_equals_8*Ieta|a'] = bool(sp.expand(ser(8 * Ie_given_a_closed, 10) - ser(K_t, 10)) == 0)
out['A_series'] = str(ser(A_t, 10))
out['K_series'] = str(ser(K_t, 10))
out['S/(1-t2S)_series'] = str(ser(S / (1 - t**2 * S), 9))
out['S^2/(1-t2S)^2_series'] = str(ser(S**2 / (1 - t**2 * S)**2, 9))
out['(1+t2)S_series'] = str(ser((1 + t**2) * S, 11))

# BA derivatives
Phi = lambda u: (1 + sp.erf(u / sp.sqrt(2))) / 2
BA = (Phi(t + a) + Phi(t - a)) / 2
out['BA_prime_at_0'] = str(sp.simplify(sp.diff(BA, a).subs(a, 0)))
out['-BA_second_at_0_minus_t*phi(t)'] = str(sp.simplify(-sp.diff(BA, a, 2).subs(a, 0) - t * phi(t)))
# B(t) = -(1/2) BA''(0) * A(t)^2 ; check equals 2 t^3 phi S^2/(1-t^2S)^2 symbolically in S
Ssym = sp.symbols('S', positive=True)
Asym = -2 * t * Ssym / (1 - t**2 * Ssym)
B_from_curv = sp.simplify(sp.Rational(1, 2) * t * phi(t) * Asym**2)
B_paper = 2 * t**3 * phi(t) * Ssym**2 / (1 - t**2 * Ssym)**2
out['B_from_curvature_equals_paper_B'] = bool(sp.simplify(B_from_curv - B_paper) == 0)
out['B_over_2t3phi_series'] = str(ser(S**2 / (1 - t**2 * S)**2, 10))

# ---------- C. numeric checks at fixed t (mpmath) ----------
mp.mp.dps = 40
def npdf(u):
    return mp.npdf(u)
def S_num(tt):
    tt = mp.mpf(tt)
    f = lambda e: mp.sech(tt**2 + tt * e)**2 * npdf(e)
    return mp.quad(f, [-mp.inf, -tt, 0, tt, mp.inf])
def dens(xx, aa, pp, tt):
    return pp * npdf(xx + aa - tt) + (1 - pp) * npdf(xx + aa + tt)

num = {}
S035 = S_num(0.35)
num['S(0.35)'] = mp.nstr(S035, 12)
num['(1+t2)S(0.35)'] = mp.nstr((1 + mp.mpf('0.35')**2) * S035, 12)
# Fisher blocks by direct quadrature of scores vs closed form
fis = []
for tt in ['0.1', '0.2', '0.3', '0.5', '1.0']:
    tt = mp.mpf(tt)
    p = lambda xx: dens(xx, 0, mp.mpf('0.5'), tt)
    sa = lambda xx: -xx + tt * mp.tanh(tt * xx)
    se = lambda xx: mp.tanh(tt * xx) / 2
    Iaa_n = mp.quad(lambda xx: p(xx) * sa(xx)**2, [-mp.inf, -tt, 0, tt, mp.inf])
    Iae_n = mp.quad(lambda xx: p(xx) * sa(xx) * se(xx), [-mp.inf, -tt, 0, tt, mp.inf])
    Iee_n = mp.quad(lambda xx: p(xx) * se(xx)**2, [-mp.inf, -tt, 0, tt, mp.inf])
    Sv = S_num(tt)
    Iag = Iaa_n - Iae_n**2 / Iee_n
    ser_val = sp.Rational(2, 3) * float(tt)**4 - 2 * float(tt)**6
    fis.append(dict(t=float(tt),
                    Iaa_err=float(Iaa_n - (1 - tt**2 * Sv)),
                    Iae_err=float(Iae_n - (-tt * Sv / 2)),
                    Iee_err=float(Iee_n - (1 - Sv) / 4),
                    Ia_given_eta=float(Iag),
                    series_2_3t4_minus_2t6=float(ser_val),
                    rel_err_series=float((Iag - ser_val) / Iag),
                    det_positive=bool(Iaa_n * Iee_n - Iae_n**2 > 0)))
num['fisher_blocks'] = fis

# positive definiteness: (1+t^2)S(t) < 1 on a grid
grid = [mp.mpf(k) / 20 for k in range(1, 121)]
num['max_(1+t2)S_on_t_0.05_to_6'] = float(max((1 + g**2) * S_num(g) for g in grid))

# Direct KL minimisation (no Fisher shortcut): P = m_{0,eta_delta}, Q = m_{a,0}
def kl_coeffs(tt, d):
    tt = mp.mpf(tt); d = mp.mpf(d)
    pp = mp.mpf('0.5') + d          # pi_{eta_delta} = 1/2 + delta
    p = lambda xx: dens(xx, 0, pp, tt)
    brk = [-mp.inf, -tt - 1, -tt, 0, tt, tt + 1, mp.inf]
    def g(aa):   # d KL / da = E_p[(x+a) - t tanh(t(x+a))]
        return mp.quad(lambda xx: p(xx) * ((xx + aa) - tt * mp.tanh(tt * (xx + aa))), brk)
    a_star = mp.findroot(g, -2 * tt * d)
    kl = mp.quad(lambda xx: p(xx) * mp.log(p(xx) / dens(xx, a_star, mp.mpf('0.5'), tt)), brk)
    BA = lambda aa: (mp.ncdf(tt + aa) + mp.ncdf(tt - aa)) / 2
    return a_star, kl, BA(0) - BA(a_star)

kl_rows = []
for tt in ['0.3', '0.5', '1.0']:
    Sv = S_num(tt); T = mp.mpf(tt)
    A_c = -2 * T * Sv / (1 - T**2 * Sv)
    K_c = 2 * (1 - (1 + T**2) * Sv) / (1 - T**2 * Sv)
    B_c = 2 * T**3 * npdf(T) * Sv**2 / (1 - T**2 * Sv)**2
    for d in ['1e-3', '5e-4']:
        a_s, kl, dBA = kl_coeffs(tt, d)
        D = mp.mpf(d)
        kl_rows.append(dict(t=float(T), delta=float(D),
                            a_over_delta=float(a_s / D), A_closed=float(A_c),
                            KL_over_delta2=float(kl / D**2), K_closed=float(K_c),
                            dBA_over_delta2=float(dBA / D**2), B_closed=float(B_c),
                            A_lead_minus2t=float(-2 * T), K_lead_4_3t6=float(mp.mpf(4) / 3 * T**6),
                            B_lead_2t3phi=float(2 * T**3 * npdf(T))))
num['kl_direct'] = kl_rows

# iterated limits at small t using closed forms with quadrature S
lim = []
for tt in ['0.2', '0.1', '0.05']:
    T = mp.mpf(tt); Sv = S_num(T)
    lim.append(dict(t=float(T),
                    A_over_t=float(-2 * Sv / (1 - T**2 * Sv)),
                    K_over_t6=float(2 * (1 - (1 + T**2) * Sv) / (1 - T**2 * Sv) / T**6),
                    B_over_t3=float(2 * npdf(T) * Sv**2 / (1 - T**2 * Sv)**2),
                    two_phi0=float(2 * npdf(0))))
num['iterated_limits'] = lim
# S series vs quadrature at small t
num['S_series_check'] = [dict(t=tt, quad=float(S_num(tt)),
                              series=float(S_ser.subs(t, sp.Rational(tt)).evalf(30)))
                         for tt in ['0.1', '0.2', '0.3']]
out['numeric'] = num

path = '/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g02_theorem6_audit.json'
with open(path, 'w') as fh:
    json.dump(out, fh, indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
