"""G14r: independent regeneration of the Fig. 2A local-response calibration (main p.6 L680-688; supp F.2 L846-852):
4,000 proportion-matched batches (t in {.35,.5,.75,1.5} x nA in {100,200,500,1000,2000} x 200; rho=.5),
seed SHA256('20270728|nA|%.17g t|%.17g rho|s') per supp L746-751 (same generator as g06r_full17g, which reproduced Table S3 exactly).
Derivative d theta/d eta = -H_thth^{-1} G_th,eta at the FP stationary point (eq. 5), finite differences of the analytic gradient.
Predicted displacement = (d theta/d eta) * eta_hat_Joint; observed = theta_Joint - theta_FP on (l1,b1). Local subset |eta_J|<=0.4."""
import sys, os, json, hashlib, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))+'/..')
import g06r_indep_resim as g, g06r_variant2 as v
from multiprocessing import Pool
def grad_theta(th, u, t, eta):
    return g.negll(np.array(th), u, t, eta)[1]
def deriv(th, u, t, h=1e-6):
    H=np.zeros((2,2))
    for j in range(2):
        e=np.zeros(2); e[j]=h
        H[:,j]=(grad_theta(th+e,u,t,0.0)-grad_theta(th-e,u,t,0.0))/(2*h)
    H=(H+H.T)/2
    G=(grad_theta(th,u,t,h)-grad_theta(th,u,t,-h))/(2*h)
    return -np.linalg.solve(H,G), np.linalg.eigvalsh(H)
def cell(args):
    nA,t=args; rho=0.5; out=[]
    for s in range(200):
        sd=int.from_bytes(hashlib.sha256(("20270728|%d|%.17g|%.17g|%d"%(nA,t,rho,s)).encode()).digest()[:8],"little")
        rng=np.random.default_rng(sd)
        y=np.where(rng.random(nA)<rho,1.0,-1.0); Z=rng.standard_normal((nA,4)); Z[:,0]+=y*t
        U=(Z-g.B0)/np.exp(g.L0); u=U[:,0]
        fx,_=v.best_of([np.array([0.0,0.0]),np.array(g.mm_start(u,t,0.0))],g.BOUNDS_FP,(u,t,0.0),1e-6)
        st=[np.array([*g.mm_start(u,t,e),e]) for e in (-8,-4,-1,0,1,4,8)]+[np.array([fx[0],fx[1],0.0]),np.array([0.0,0.0,0.0])]
        jx,_=v.best_of(st,g.BOUNDS_J,(u,t,None),1e-6)
        d,eig=deriv(fx,u,t)
        out.append(dict(nA=nA,t=t,s=s,eta=float(jx[2]),obs=(jx[:2]-fx).tolist(),dth=d.tolist(),hess_min_eig=float(eig.min())))
    return out
if __name__=="__main__":
    os.environ["OMP_NUM_THREADS"]="1"
    cells=[(nA,t) for t in (0.35,0.5,0.75,1.5) for nA in (100,200,500,1000,2000)]
    with Pool(4) as p: res=[r for c in p.map(cell,cells) for r in c]
    json.dump(res,open(os.path.abspath(__file__).replace('.py','_raw.json'),'w'))
    eta=np.array([r['eta'] for r in res]); obs=np.array([r['obs'] for r in res]); pred=np.array([np.array(r['dth'])*r['eta'] for r in res])
    loc=np.abs(eta)<=0.4
    print('n fits',len(res),'local |eta_J|<=0.4:',int(loc.sum()),'boundary |eta|>=10:',int((np.abs(eta)>=10-1e-7).sum()))
    print('FP Hessian (of mean NLL) positive-definite in',int(sum(r['hess_min_eig']>0 for r in res)),'of',len(res))
    O=obs[loc].ravel(); P=pred[loc].ravel()
    r2_pooled=1-np.sum((O-P)**2)/np.sum((O-O.mean())**2)
    r2_uncentered=1-np.sum((O-P)**2)/np.sum(O**2)
    r2_comp=[1-np.sum((obs[loc][:,k]-pred[loc][:,k])**2)/np.sum((obs[loc][:,k]-obs[loc][:,k].mean())**2) for k in range(2)]
    rel=np.linalg.norm(obs[loc]-pred[loc],axis=1)/np.linalg.norm(obs[loc],axis=1)
    print('R2 pooled componentwise (centered) %.5f  uncentered %.5f  per-comp l1 %.5f b1 %.5f'%(r2_pooled,r2_uncentered,*r2_comp))
    print('median vector relative error %.4f%%'%(100*np.median(rel)))
    for thr in (0.3,0.4,0.5): print(' |eta|<=',thr,'count',int((np.abs(eta)<=thr).sum()))
