# G14r: re-run only the crossover cells cited in the abstract/§5.1 with the g06r_full17g generator (seed per supp L746-751)
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))+'/..')
import importlib.util, json
spec=importlib.util.spec_from_file_location('f',os.path.dirname(os.path.abspath(__file__))+'/../g06r_full17g.py')
src=open(spec.origin).read().split('out=[]')[0]   # import definitions only, skip the full-grid loop
ns={'__file__':spec.origin}; exec(compile(src,spec.origin,'exec'),ns)
for t,rho in [(0.75,0.92),(0.5,0.5),(0.5,0.92)]:
    r=ns['cell'](t,rho); print(t,rho,'dMSE',[round(x,5) for x in r['d_mse']],'dBA_pp',[round(x,3) for x in r['d_ba_pp']],'bnd',r['joint_eta_boundary'],flush=True)
