# Read-only: alternative aggregations of Stage-2 per-trial dumps (P12 re-fit) to search for paper Table-1 GEM cells
import numpy as np, glob, collections, re
from sklearn.metrics import balanced_accuracy_score as bas
R='/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_stage2/units/'
units=collections.defaultdict(dict)
for f in sorted(glob.glob(R+'*.npz')):
    d=np.load(f,allow_pickle=True)
    ds=str(d['dataset']); s=int(d['target_subject']); sd=int(d['source_seed'])
    units[(ds,s)][sd]=d
def sm(x): x=x-x.max(1,keepdims=True); e=np.exp(x); return e/e.sum(1,keepdims=True)
paper={'BNCI2014_001':{'fpgem':(73.2,11.5),'jointgem':(71.9,11.3)},'Lee2019_MI':{'fpgem':(67.6,9.3),'jointgem':(66.3,9.2)}}
out=collections.defaultdict(lambda: collections.defaultdict(list))
for (ds,s),seeds in units.items():
    for m in ['identity','fpgem','jointgem']:
        ev=[];ad=[];both=[];ensP=None;ensL=None;accs=[]
        for sd,d in seeds.items():
            ye=d['eval_y'];ya=d['adapt_y'];le=d['eval_logits_'+m];la=d['adapt_logits_'+m]
            ev.append(bas(ye,le.argmax(1))); ad.append(bas(ya,la.argmax(1)))
            both.append(bas(np.r_[ye,ya],np.r_[le,la].argmax(1)))
            accs.append((le.argmax(1)==ye).mean())
            ensP=sm(le) if ensP is None else ensP+sm(le)
            ensL=le if ensL is None else ensL+le
        out[ds][m+'|eval_seedmean'].append(np.mean(ev))
        out[ds][m+'|adapt_seedmean'].append(np.mean(ad))
        out[ds][m+'|adapt+eval'].append(np.mean(both))
        out[ds][m+'|eval_acc'].append(np.mean(accs))
        out[ds][m+'|eval_seedmax'].append(np.max(ev))
        out[ds][m+'|eval_ensprob'].append(bas(ye,ensP.argmax(1)))
        out[ds][m+'|eval_enslogit'].append(bas(ye,ensL.argmax(1)))
        for sd in (0,1,2): out[ds][m+f'|eval_seed{sd}'].append(ev[list(seeds).index(sd)] if sd in seeds else np.nan)
    for m in ['fp','joint']:
        rr=[bas(d['adapt_y'],d[m+'_responsibilities'].argmax(1)) for d in seeds.values()]
        out[ds][m+'|resp_adapt'].append(np.mean(rr))
for ds in out:
    print('==',ds,'n=',len(units and [k for k in units if k[0]==ds]))
    for k,v in sorted(out[ds].items()):
        v=100*np.array(v); flag=''
        for mm,(pm,psd) in paper.get(ds,{}).items():
            if abs(v.mean()-pm)<0.06: flag+=f' MEAN~{mm}'
        print(f'  {k:28s} {np.nanmean(v):7.3f} ({np.nanstd(v,ddof=1):6.3f}){flag}')
