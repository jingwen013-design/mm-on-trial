"""Tables C1-C3 (appC.json) and Table 3 / Section 6.2 (tcja.json). Needs exp1.json."""
import json, numpy as np
from model import *
cf = np.array([STRONG, WEAK]); pr = np.array([.5, .5])
e1 = json.load(open('exp1.json'))
two = []
for D in (40, 44, 45, 50, 55, 60):
    g, vd, _ = gain_fixed(D, cf, pr); gm, rt, _ = gain_market(D, cf, pr)
    two.append([D, round(g, 2), round(D - vd, 2), round(gm, 2), round(100 * rt, 1)])
logn = [[D, round(e1['fixed'][D], 2), round(100 * e1['pd_fixed'][D], 1), round(e1['fixed'][D] + e1['lender_loss'][D], 2),
         round(e1['market'][D], 2), round(100 * e1['rate'][D], 1), round(100 * e1['pd_mkt'][D], 1)] for D in (20, 30, 34, 35, 40, 45, 50, 55)]
cov = [1, 1.5, 2, 3, 3.33, 5, 10]
grid = []
for cv in (0.28, 0.6, 1.0):
    grid.append(['%.2f' % cv] + [round(100 * usable_share(k, cv, n=300000)) for k in cov])
    grid.append(['%.2f + cap' % cv] + [round(100 * usable_share(k, cv, cap=.3, n=300000)) for k in cov])
json.dump(dict(two=two, logn=logn, grid=grid, cov=cov), open('appC.json', 'w'))

out = {}
for sd in (25, 50):
    e = lognormal_draws(sd=sd, n=400_000, seed=3)
    rows = []
    for lab, t, cap in [('Before TCJA: 35%, no cap', .35, None), ('Rate cut only: 21%', .21, None),
                        ('Interest cap only: 35% + 30% cap', .35, .30), ('After TCJA: 21% + 30% cap', .21, .30),
                        ('Singapore: 17%, no cap', .17, None)]:
        D, g, vu, p = max(((D,) + multi_period_sim(D, e, tau=t, cap=cap) for D in range(5, 800, 1)), key=lambda x: x[1])
        rows.append(dict(label=lab, D=D, cov=90 / (0.1 * D), gain=100 * g / vu, p=100 * p))
    for r in rows: r['D_idx'] = 100 * r['D'] / rows[0]['D']
    out[sd] = rows
json.dump(out, open('tcja.json', 'w'), indent=1)

# Section 5.4 headline numbers (analytic lognormal, fine grid)
for sd in (25, 50):
    Ds = np.arange(1, 800, 1.0)
    g = np.array([multi_period_gain(D, sd=sd)[0] for D in Ds]); j = int(np.argmax(g))
    gg, vu, p = multi_period_gain(Ds[j], sd=sd)
    gross = (1 - p) * TAU * 0.1 * Ds[j] / (R + p)
    print(f"sd {sd}: D*={Ds[j]:.0f}  D/VU={Ds[j]/vu:.3f}  cov={90/(0.1*Ds[j]):.2f}  p={p:.4f}  gain={100*gg/vu:.2f}%  gross shield={100*gross/vu:.2f}%")
print('done')
