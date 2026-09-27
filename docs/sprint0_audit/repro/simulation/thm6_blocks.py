# Independent check via the paper's own Fisher-block formulas with S(t)=E[sech^2(tZ)], Z~.5N(t,1)+.5N(-t,1) (mpmath high precision)
import mpmath as mp
mp.mp.dps=40
def S(t):
    f=lambda z: mp.sech(t*z)**2*(mp.npdf(z,t,1)+mp.npdf(z,-t,1))/2
    return mp.quad(f,[-mp.inf,-t,0,t,mp.inf])
for t in [mp.mpf('0.5'),mp.mpf('0.3'),mp.mpf('0.2'),mp.mpf('0.1'),mp.mpf('0.05')]:
    s=S(t); Iaa=1-t**2*s; Iae=-t*s/2; Iee=(1-s)/4; Ip=Iaa-Iae**2/Iee
    print(f"t={float(t):.2f} Iaa={float(Iaa):.8f} 1-t^2={float(1-t**2):.8f} (Iaa-(1-t^2))/t^4={float((Iaa-1+t**2)/t**4):.4f} | Ip/t^4={float(Ip/t**4):.6f} (Ip-(2/3)t^4+2t^6)/t^8={float((Ip-mp.mpf(2)/3*t**4+2*t**6)/t**8):.4f}")
