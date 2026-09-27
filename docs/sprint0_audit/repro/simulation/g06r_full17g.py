"""FINAL independent regeneration of Table S3 (and nA=500 Table S2 cells) with seed string
SHA256('20270728|nA|t|rho|s') where t and rho are formatted '%.17g' (17 significant digits).
Generator: default_rng(seed); y=+1 if U(0,1)<rho else -1; Z=standard_normal((nA,4)); Z[:,0]+=y*t;
U=(Z-b0)/exp(l0). Fits: coord-1 L-BFGS-B (bounds l1[-4,4], b1[-8,8], eta[-10,10]; maxiter 2000,
maxls 50, ftol 1e-13, gtol 1e-7) on mean negative log-likelihood; FP starts {identity, moment-match};
Joint starts moment-match at eta in {-8,-4,-1,0,1,4,8} + FP warm start + identity; coords 2-4 closed form.
BA analytic (balanced Gaussian eval, uniform decision weights). Paired Student-t 95% intervals."""
import json, hashlib, numpy as np
import g06r_indep_resim as g, g06r_variant2 as v
from scipy.stats import t as student_t
PAPER = {(0.35,0.5):(-0.0332,-0.0378,-0.0286,0.221,0.192,0.251),(0.5,0.5):(-0.0672,-0.0780,-0.0564,0.632,0.529,0.735),
 (0.75,0.5):(-0.0719,-0.0942,-0.0496,0.945,0.651,1.239),(1.5,0.5):(-0.0012,-0.0021,-0.0002,0.011,0.002,0.020),
 (0.35,0.7):(-0.0252,-0.0335,-0.0168,0.156,0.104,0.208),(0.5,0.7):(-0.0274,-0.0429,-0.0118,0.235,0.107,0.362),
 (0.75,0.7):(0.0089,-0.0201,0.0379,-0.025,-0.331,0.280),(1.5,0.7):(0.0512,0.0467,0.0558,-0.513,-0.557,-0.468),
 (0.35,0.92):(-0.0258,-0.0431,-0.0085,0.126,0.022,0.231),(0.5,0.92):(0.0108,-0.0214,0.0430,-0.181,-0.421,0.060),
 (0.75,0.92):(0.1980,0.1261,0.2699,-1.944,-2.541,-1.346),(1.5,0.92):(1.1287,1.0784,1.1790,-7.548,-7.793,-7.303)}
def cell(t,rho,nA=500,S=200):
    rows=[]; bnd=0
    for s in range(S):
        sd=int.from_bytes(hashlib.sha256(("20270728|%d|%.17g|%.17g|%d"%(nA,t,rho,s)).encode()).digest()[:8],"little")
        rng=np.random.default_rng(sd)
        y=np.where(rng.random(nA)<rho,1.0,-1.0); Z=rng.standard_normal((nA,4)); Z[:,0]+=y*t
        U=(Z-g.B0)/np.exp(g.L0); u=U[:,0]
        fx,_=v.best_of([np.array([0.0,0.0]),np.array(g.mm_start(u,t,0.0))],g.BOUNDS_FP,(u,t,0.0),1e-6)
        st=[np.array([*g.mm_start(u,t,e),e]) for e in (-8,-4,-1,0,1,4,8)]+[np.array([fx[0],fx[1],0.0]),np.array([0.0,0.0,0.0])]
        jx,_=v.best_of(st,g.BOUNDS_J,(u,t,None),1e-6)
        bnd+=abs(jx[2])>=10-1e-7
        nm=g.nuisance_mse(U)
        rows.append(((fx[0]-g.L0[0])**2+(fx[1]-g.B0[0])**2+nm,(jx[0]-g.L0[0])**2+(jx[1]-g.B0[0])**2+nm,100*(g.ba(fx[0],fx[1],t)-g.ba(jx[0],jx[1],t))))
    a=np.array(rows); d=a[:,0]-a[:,1]; b=a[:,2]; tc=student_t.ppf(.975,S-1)
    h=lambda x: tc*x.std(ddof=1)/np.sqrt(S)
    return dict(t=t,rho=rho,mse_fp=a[:,0].mean(),mse_joint=a[:,1].mean(),d_mse=[d.mean(),d.mean()-h(d),d.mean()+h(d)],d_ba_pp=[b.mean(),b.mean()-h(b),b.mean()+h(b)],joint_eta_boundary=int(bnd))
out=[]
for rho in (0.5,0.7,0.92):
    for t in (0.35,0.5,0.75,1.5):
        r=cell(t,rho); p=PAPER[(t,rho)]
        mine=(round(r['d_mse'][0],4),round(r['d_mse'][1],4),round(r['d_mse'][2],4),round(r['d_ba_pp'][0],3),round(r['d_ba_pp'][1],3),round(r['d_ba_pp'][2],3))
        r['paper']=p; r['exact_match_at_paper_precision']=all(abs(x-y)<1.5e-4 if i<3 else abs(x-y)<1.5e-3 for i,(x,y) in enumerate(zip(mine,p)))
        out.append(r)
        print("t=%.2f rho=%.2f FP=%.5f J=%.5f dMSE=%+.4f [%+.4f,%+.4f] dBA=%+.3f [%+.3f,%+.3f] bnd=%d | paper dMSE=%+.4f [%+.4f,%+.4f] dBA=%+.3f [%+.3f,%+.3f] | match=%s"%(t,rho,r['mse_fp'],r['mse_joint'],*r['d_mse'],*r['d_ba_pp'],r['joint_eta_boundary'],*p,r['exact_match_at_paper_precision']),flush=True)
json.dump(out,open(__file__.replace('.py','_out.json'),'w'),indent=1)
