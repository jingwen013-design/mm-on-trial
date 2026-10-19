"""Section 5.1: market-priced debt in the lognormal model (writes exp1.json, about 3 minutes)."""
import numpy as np, json
from model import *
cf=lognormal_draws(n=200_000); pr=np.full(cf.size,1/cf.size)
VU=v_unlevered(cf,pr)
Ds=np.arange(0,66,1.0)
out={'D':Ds.tolist(),'fixed':[], 'market':[], 'rate':[], 'pd_fixed':[], 'pd_mkt':[], 'lender_loss':[]}
for D in Ds:
    g,vd,pd=gain_fixed(D,cf,pr); out['fixed'].append(g); out['pd_fixed'].append(pd); out['lender_loss'].append(D-vd)
    gm,rt,pdm=gain_market(D,cf,pr); out['market'].append(gm); out['rate'].append(rt); out['pd_mkt'].append(pdm)
json.dump(out,open('exp1.json','w'))
f=np.array(out['fixed']); m=np.array(out['market'],float)
i=np.nanargmax(f); j=np.nanargmax(m)
print('VU',VU,'fixed opt D',Ds[i],f[i],out['pd_fixed'][i],' market opt D',Ds[j],m[j],out['pd_mkt'][j],'rate',out['rate'][j])
for D in (20,30,34,40,45,50,55,60,65):
    k=int(D); print(D,'fixed %.3f pd %.3f lenderloss %.2f sh.gain %.2f | mkt %.3f rate %.2f%% pd %.3f'%(f[k],out['pd_fixed'][k],out['lender_loss'][k],f[k]+out['lender_loss'][k],m[k],100*out['rate'][k],out['pd_mkt'][k]))
