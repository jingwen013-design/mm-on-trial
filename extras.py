"""Numbers quoted in the text that no other script prints (writes extras.json, a few seconds).

Section 3.3  the money-machine trade with taxes (buy L's debt and equity, short U)
Section 3.4  equity payoffs, CAPM beta ratio, Hamada multiplier, WACC, VaR reading of the optimum
Section 4.1  distress-cost thresholds in the two-state model
Section 5.1  shareholders' gain under a fixed rate at D = 60 (needs exp1.json)
Section 6.1  dollar value of the gain before and after the rate cut (needs tcja.json)
Section 6.2  one-period debt limit and gain at Singapore's 17% rate
Section 6.3  share of loss years for SIA; Sheng Siong under other EBIT volatilities
"""
import json
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm
from model import *
from calib2 import F as FIRMS, opt

two_cf, two_p = np.array([STRONG, WEAK]), np.array([.5, .5])
VU = v_unlevered(two_cf, two_p)
out = {}


def investors(D, X, c=C, rate=0.10):
    """What all of L's investors receive in a state with EBIT X (fixed-rate debt)."""
    at = after_tax(X, rate * D); F = (1 + rate) * D
    return at if at >= F else (1 - c) * at


# ---- 3.3 money machine: long L's debt and equity, short U
for D in (40, 45):
    pay = {s: float(investors(D, X) - (1 - TAU) * X) for s, X in (("strong", STRONG), ("weak", WEAK))}
    out[f"money_machine_D{D}"] = dict(pay, pv=(0.5 * pay["strong"] + 0.5 * pay["weak"]) / (1 + R))

# ---- 3.4 the course toolkit at D = 40
D = 40.0
VL = VU + gain_fixed(D, two_cf, two_p)[0]
eq = [float(after_tax(X, 0.1 * D) - 1.1 * D) for X in (STRONG, WEAK)]
E = 0.5 * sum(eq) / (1 + R)
wacc = (E * R + D * 0.10 * (1 - TAU)) / VL
out["toolkit_D40"] = dict(V_U=VU, V_L=VL, equity_payoffs=eq, E=E, beta_E_over_beta_U=VU / E,
                          hamada=1 + (1 - TAU) * D / E, perpetual_shield=TAU * D,
                          wacc=wacc, V_L_from_wacc=(1 - TAU) * 90 / (1 + wacc))

# VaR reading of the lognormal optimum, and the optimum under other distress costs
ln = lognormal_draws(n=200_000); lp = np.full(ln.size, 1 / ln.size)
out["var_reading_D34"] = dict(promise=1.1 * 34, q01_after_tax_cash=float(np.quantile(after_tax(ln, 0.1 * 34), 0.01)))
Dl = np.arange(0, 61, 1.0)
for c in (0.05, 0.20, 0.40):
    res = [gain_fixed(x, ln, lp, c=c) for x in Dl]; k = int(np.argmax([r[0] for r in res]))
    out[f"lognormal_optimum_c{round(100 * c)}"] = dict(D=float(Dl[k]), gain=float(res[k][0]), p_default=float(res[k][2]))

# ---- 4.1 distress-cost thresholds (two-state)
Dstar = d_star_two_state()
out["two_state"] = dict(
    D_star=Dstar, gain_at_D_star=float(gain_fixed(Dstar - 1e-9, two_cf, two_p)[0]),
    c_debt_past_limit_adds_value=brentq(lambda c: gain_fixed(Dstar + 1e-9, two_cf, two_p, c=c)[0], 1e-4, 0.2),
    D_gain_positive_again_c5=brentq(lambda x: gain_fixed(x, two_cf, two_p, c=0.05)[0], 50, 70),
    gain_at_D45={f"c{round(100 * c)}": float(gain_fixed(45, two_cf, two_p, c=c)[0]) for c in (0.05, 0.20, 0.40)})

# ---- 5.1 shareholders' gain with a fixed rate (lognormal, from exp1.json)
e1 = json.load(open("exp1.json"))
out["shareholders_gain_fixed"] = {str(d): e1["fixed"][d] + e1["lender_loss"][d] for d in (50, 60)}

# ---- 6.1 dollar value of the gain at the optimum (multi-period, EBIT volatility 0.28)
t3 = json.load(open("tcja.json"))["25"]
e = lognormal_draws(sd=25, n=400_000, seed=3)
dollars = {}
for row, tau in ((0, .35), (1, .21)):
    vu = (1 - tau) * e.mean() / R
    dollars[t3[row]["label"]] = dict(V_U=vu, gain=t3[row]["gain"] / 100 * vu)
out["tcja_dollars"] = dollars

# ---- 6.2 Singapore's 17% rate in the one-period model
ds17 = d_star_two_state(tau=0.17)
out["singapore_one_period"] = dict(D_star=ds17, max_gain_pct_of_VU=100 * gain_fixed(ds17 - 1e-9, two_cf, two_p, tau=0.17)[0]
                                   / v_unlevered(two_cf, two_p, tau=0.17))

# ---- 6.3 calibration details
sia = np.array(FIRMS["SIA"]["ebit"]); mu_s, sd_s = sia[-5:].mean(), np.diff(sia).std(ddof=1)
out["sia_share_of_loss_years"] = float(norm.cdf(-mu_s / sd_s))
ss = np.array(FIRMS["Sheng Siong"]["ebit"]); mu = ss[-5:].mean()
out["sheng_siong_by_volatility"] = {}
sd_obs = np.diff(ss).std(ddof=1)
for sd in (sd_obs / np.sqrt(2), sd_obs, 30.0):          # sqrt(2) correction, Table 4, conservative
    (k, g, p), _ = opt(mu, sd)
    out["sheng_siong_by_volatility"][f"{sd:.2f}"] = dict(opt_cov=1 / k, gain_pct=g, p_default=p)

json.dump(out, open("extras.json", "w"), indent=1)
for key, val in out.items():
    print(key, json.dumps(val, default=float)[:300])
