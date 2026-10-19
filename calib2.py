"""Section 6.3: calibration of the multi-period model to Singapore Airlines and Sheng Siong (Table 4)."""
import json, numpy as np
from model import multi_period_sim
F = json.load(open('firms.json'))

def curve(mu, sd, tau=.17, n=400_000, seed=11, cap=None):
    e = mu + sd * np.random.default_rng(seed).standard_normal(n)
    ks = np.linspace(0.0, 1.2, 481)
    out = []
    for k in ks:
        if k == 0: out.append((0, 0.0, 0.0)); continue
        g, vu, p = multi_period_sim(k * mu / 0.1, e, tau=tau, cap=cap)
        out.append((k, 100 * g / vu, p))
    return np.array(out)

def opt(mu, sd, **kw):
    c = curve(mu, sd, **kw); j = int(np.argmax(c[:, 1])); return c[j], c

def table4(path="calib_out.json"):
    """Numbers reported in Table 4 (centred on the last five years; full-sample centring as a check)."""
    out = {}
    for name, f in F.items():
        x = np.array(f['ebit']); it = np.array(f['interest']); sd = np.diff(x).std(ddof=1); mu = x[-5:].mean()
        (k, g, p), _ = opt(mu, sd)
        (k2, g2, p2), _ = opt(x.mean(), sd)
        cov = [e / i if i > 0 else None for e, i in zip(x, it)]
        out[name] = dict(mu=float(mu), sd=float(sd), cv=float(sd / mu), loss_years=int((x < 0).sum()),
                         worst=float(x.min()), worst_year=f['years'][int(x.argmin())], latest_cov=float(cov[-1]),
                         min_cov=float(min(v for v in cov if v is not None)), opt_k=float(k),
                         opt_cov=(float(1 / k) if k else None), opt_gain=float(g), opt_p=float(p),
                         alt_cov=(float(1 / k2) if k2 else None), alt_gain=float(g2),
                         latest_debt=f['debt'][-1], latest_cash=f['cash'][-1], latest_interest=float(it[-1]))
    json.dump(out, open(path, "w"), indent=1)
    return out


if __name__ == "__main__":
    for name, v in table4().items():
        print(name, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()})
