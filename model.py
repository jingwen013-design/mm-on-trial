"""MM Proposition I on trial: the corporate-tax assumption.
One-period model from the deck, plus four extensions used in the report.
All monetary figures are teaching units unless stated otherwise.
"""
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

R = 0.10          # discount rate (risk-neutral, as in the lecture example)
TAU = 0.20        # corporate tax rate
C = 0.20          # distress cost: share of after-tax cash lost on default
STRONG, WEAK = 120.0, 60.0


# ---------------------------------------------------------------- core payoff
def after_tax(cf, interest, tau=TAU):
    """After-tax cash; no loss carry-forward, interest deductible, principal not."""
    return cf - tau * np.maximum(cf - interest, 0.0)


def firm_value(cf, prob, D, F, tau=TAU, c=C, r=R):
    """Value of all claims when the firm borrows D today and promises F next year.
    Interest deduction = F - D. Returns (V_L, V_debt, P_default)."""
    at = after_tax(cf, F - D, tau)
    default = at < F - 1e-12
    total = np.where(default, (1 - c) * at, at)
    debt = np.where(default, (1 - c) * at, F)
    return (prob @ total) / (1 + r), (prob @ debt) / (1 + r), prob @ default


def v_unlevered(cf, prob, tau=TAU, r=R):
    return (prob @ ((1 - tau) * cf)) / (1 + r)


# ------------------------------------------------- base case: fixed 10% rate
def gain_fixed(D, cf, prob, tau=TAU, c=C, rate=0.10):
    F = (1 + rate) * D
    vl, vd, pd = firm_value(cf, prob, D, F, tau, c)
    return vl - v_unlevered(cf, prob, tau), vd, pd


def d_star_two_state(tau=TAU, weak=WEAK, rate=0.10):
    """Largest D the weak state can repay: weak - tau*(weak - rate*D) = (1+rate)*D."""
    return (1 - tau) * weak / ((1 + rate) - tau * rate)


# ------------------------------------------ Extension 1: market-priced debt
def market_face(D, cf, prob, tau=TAU, c=C, r=R):
    """Promised repayment F such that lenders break even (V_debt = D).
    Returns np.nan when no F can raise D (beyond debt capacity)."""
    if D <= 0:
        return 0.0
    f = lambda F: firm_value(cf, prob, D, F, tau, c, r)[1] - D
    lo = (1 + r) * D
    if f(lo) >= -1e-10:
        return lo
    grid = np.linspace(lo, lo + 4 * cf.max(), 800)
    vals = np.array([f(x) for x in grid])
    ok = np.where(vals >= 0)[0]
    if len(ok) == 0:
        return np.nan
    j = ok[0]
    return brentq(f, grid[j - 1], grid[j])


def gain_market(D, cf, prob, tau=TAU, c=C):
    F = market_face(D, cf, prob, tau, c)
    if np.isnan(F):
        return np.nan, np.nan, np.nan
    vl, vd, pd = firm_value(cf, prob, D, F, tau, c)
    return vl - v_unlevered(cf, prob, tau), F / D - 1 if D > 0 else 0.0, pd


# ------------------------------------- Extension 2: can the shield be used?
def usable_share(coverage, cv, cap=None, n=400_000, seed=7):
    """Expected tax saving / (tau * interest), EBIT ~ Normal(mu, (cv*mu)^2), mu=1.
    coverage = E[EBIT] / interest. No loss carry-forward (lost if EBIT < interest).
    cap: deductible interest limited to cap * max(EBIT, 0) (US s163(j) style, 0.30)."""
    rng = np.random.default_rng(seed)
    ebit = 1 + cv * rng.standard_normal(n)
    I = 1.0 / coverage
    pos = np.maximum(ebit, 0.0)
    ded = np.minimum(I, pos)
    if cap is not None:
        ded = np.minimum(ded, cap * pos)
    return ded.mean() / I


# --------------------------------------------- Extension 3: personal taxes
def miller_tstar(tc, td, te):
    """Net tax advantage of $1 of interest (Miller 1977)."""
    return 1 - (1 - tc) * (1 - te) / (1 - td)


# ----------------------------------------- Extension 4: multi-period debt
def shield_pv_maturity(D, T, tau=TAU, r=R):
    """PV of shield on riskless debt D outstanding T years (interest r*D per year)."""
    return tau * D * (1 - (1 + r) ** (-np.asarray(T, float)))


def multi_period_gain(D, mean=90.0, sd=25.0, tau=TAU, c=C, r=R, coupon=0.10, dist="lognormal"):
    """Perpetual firm, EBIT iid each year. Perpetual debt D, coupon*D a year.
    Default in the first year EBIT < coupon (after-tax cash cannot cover interest);
    at default the firm loses c of its unlevered value and becomes all-equity.
    Returns (V_L - V_U, V_U, annual default prob p)."""
    I = coupon * D
    if dist == "lognormal":
        s2 = np.log(1 + (sd / mean) ** 2)
        mu = np.log(mean) - s2 / 2
        p = norm.cdf((np.log(I) - mu) / np.sqrt(s2)) if I > 0 else 0.0
    else:
        p = norm.cdf((I - mean) / sd)
    vu = (1 - tau) * mean / r
    gain = ((1 - p) * tau * I - p * c * vu) / (r + p)
    return gain, vu, p


def lognormal_draws(mean=90.0, sd=25.0, n=200_000, seed=0):
    s2 = np.log(1 + (sd / mean) ** 2)
    rng = np.random.default_rng(seed)
    return rng.lognormal(np.log(mean) - s2 / 2, np.sqrt(s2), n)


def multi_period_sim(D, ebit, tau=TAU, c=C, r=R, coupon=0.10, cap=None):
    """Simulation version of multi_period_gain with an optional interest cap
    (deductible interest <= cap * EBIT). ebit: draws of one year's EBIT."""
    I = coupon * D
    pos = np.maximum(ebit, 0.0)
    ded = np.minimum(I, pos) if cap is None else np.minimum(np.minimum(I, pos), cap * pos)
    at = ebit - tau * np.maximum(ebit - ded, 0.0)
    ok = at >= I
    p = 1 - ok.mean()
    shield = tau * (ded * ok).mean()
    vu = (1 - tau) * ebit.mean() / r
    return (shield - p * c * vu) / (r + p), vu, p
