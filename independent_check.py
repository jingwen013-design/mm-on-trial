"""Independent check of the base results, written separately from model.py.

model.py values the lognormal case by Monte Carlo (200,000 draws). This script
does not import model.py and integrates against the lognormal density instead,
so it checks both the code and the simulation error. It reproduces:
    V_U = 65.45 and D* = 44.44 (two-state model)
    Table 1: V_L - V_U = 0.73, 0.80, -3.63, -3.55 at D = 40, 44, 45, 50
    lognormal optimum near D = 34 with a gain of about 0.56 and a default
    probability of about 1%, and the gain back to zero near D = 45.5
"""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import lognorm

r, rate, tau, c = 0.10, 0.10, 0.20, 0.20          # discount rate, borrowing rate, tax, distress cost
mean, sd = 90.0, 25.0


def after_tax(x, D):
    """Cash after corporate tax; interest rate*D is deductible, losses are not carried forward."""
    return x - tau * max(x - rate * D, 0.0)


# ---------------------------------------------------------------- two states
def gain_two_state(D, states=((120.0, 0.5), (60.0, 0.5))):
    total = 0.0
    for x, p in states:
        a = after_tax(x, D)
        total += p * (a if a >= (1 + rate) * D else (1 - c) * a)
    vu = sum(p * (1 - tau) * x for x, p in states) / (1 + r)
    return total / (1 + r) - vu, vu


vu2 = gain_two_state(0)[1]
d_star = (1 - tau) * 60 / ((1 + rate) - tau * rate)
print(f"two states: V_U = {vu2:.2f}, D* = {d_star:.2f}")
print("Table 1:", {D: round(gain_two_state(D)[0], 2) for D in (40, 44, 45, 50)})

# ------------------------------------------------- lognormal, by integration
s = np.sqrt(np.log(1 + (sd / mean) ** 2))
X = lognorm(s, scale=mean * np.exp(-s ** 2 / 2))   # E[X] = 90, sd 25
vu = (1 - tau) * mean / (1 + r)


def default_threshold(D):
    """EBIT below which after-tax cash cannot pay (1 + rate) D: 0.8x + 0.2*rate*D = 1.1D."""
    return ((1 + rate) * D - tau * rate * D) / (1 - tau)


def gain_lognormal(D):
    xd = default_threshold(D)
    f = lambda x: after_tax(x, D) * X.pdf(x)
    below = quad(f, 0, xd, points=[rate * D], limit=200)[0]        # default states
    above = quad(f, xd, np.inf, limit=200)[0]                       # creditors paid in full
    return ((1 - c) * below + above) / (1 + r) - vu, X.cdf(xd)


res = minimize_scalar(lambda D: -gain_lognormal(D)[0], bounds=(20, 45), method="bounded", options={"xatol": 1e-4})
d_opt = res.x; g_opt, p_opt = gain_lognormal(d_opt)
d_zero = brentq(lambda D: gain_lognormal(D)[0], d_opt + 1, 60)
print(f"lognormal: V_U = {vu:.2f}, optimum D = {d_opt:.1f}, gain = {g_opt:.3f} ({100 * g_opt / vu:.2f}% of V_U), "
      f"P(default) = {100 * p_opt:.2f}%, gain back to zero at D = {d_zero:.1f}")
