"""Figures 1-5 of the paper (needs exp1.json from exp1.py)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from model import *

BLUE, ORANGE, TEAL, RED = "#2563A8", "#D97A1F", "#2E9E8F", "#B23A48"
INK, MUTED, GRID = "#1A1A1A", "#4D4D4D", "#E6E6E6"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"], "mathtext.fontset": "stix", "font.size": 9, "axes.titlesize": 9,
    "axes.titleweight": "normal", "axes.titlelocation": "center", "axes.labelsize": 9,
    "axes.edgecolor": "#000000", "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 7.5, "lines.linewidth": 1.4, "savefig.dpi": 300,
})


def zero(ax):
    ax.axhline(0, color="#999999", lw=0.6, ls=":", zorder=1)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(f"fig/{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


two_cf, two_p = np.array([STRONG, WEAK]), np.array([.5, .5])

# ---------------- Figure 1: base results (two-state cliff, smooth hill, P(default))
Ds = np.linspace(0, 60, 601)
g2 = [gain_fixed(D, two_cf, two_p)[0] for D in Ds]
ln = lognormal_draws(n=200_000)
lp = np.full(ln.size, 1 / ln.size)
Dl = np.arange(0, 61, 1.0)
gl, pdl = zip(*[(gain_fixed(D, ln, lp)[0], gain_fixed(D, ln, lp)[2]) for D in Dl])
gl, pdl = np.array(gl), np.array(pdl)
k = int(np.argmax(gl))

# Figure 1: two-state model only
fig, a = plt.subplots(1, 1, figsize=(4.4, 2.05))
zero(a)
a.plot(Ds, g2, color=BLUE)
a.axvline(d_star_two_state(), color=MUTED, ls=":", lw=1)
a.annotate(r"$D^*=44.4$", (46, -1.6), fontsize=7.5, color=MUTED)
a.annotate(r"+0.73 at $D$ = 40", (40, 0.73), (8, 1.4), fontsize=7.5, color=INK,
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
a.annotate(r"$-3.63$ at $D$ = 45", (45, -3.63), (12, -3.3), fontsize=7.5, color=INK,
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
a.set_ylim(-4.2, 2.0); a.set_xlabel(r"Debt principal $D$"); a.set_ylabel(r"$V_L - V_U$")
save(fig, "fig1_two_state")

# Figure 3 (Section 4.2): continuous cash flows, sd 25 and sd 30
ln30 = lognormal_draws(sd=30, n=200_000)
g30, pd30 = zip(*[(gain_fixed(D, ln30, lp)[0], gain_fixed(D, ln30, lp)[2]) for D in Dl])
g30, pd30 = np.array(g30), np.array(pd30)
k30 = int(np.argmax(g30))
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.4))
a = ax[0]; zero(a)
a.plot(Ds, g2, color="#B0B0B0", lw=1.0, label="Two states (Figure 1)")
a.plot(Dl, gl, color=BLUE, label="Lognormal, s.d. 25")
a.plot(Dl, g30, color=RED, ls="--", label="Lognormal, s.d. 30")
a.plot(Dl[k], gl[k], "o", color=BLUE, ms=4); a.plot(Dl[k30], g30[k30], "o", color=RED, ms=4)
a.annotate(f"optimum $D$ = {Dl[k]:.0f}, gain {gl[k]:.2f}", (Dl[k], gl[k]), (2, 1.35), fontsize=7,
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
a.annotate(f"optimum $D$ = {Dl[k30]:.0f}, gain {g30[k30]:.2f}", (Dl[k30], g30[k30]), (2, -1.3), fontsize=7,
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
a.set_ylim(-4.2, 2.0); a.set_title("(a) Value gain"); a.set_xlabel(r"Debt principal $D$"); a.set_ylabel(r"$V_L - V_U$")
a.legend(loc="lower left", fontsize=6.8)
a = ax[1]
a.plot(Dl, 100 * pdl, color=BLUE, label="s.d. 25")
a.plot(Dl, 100 * pd30, color=RED, ls="--", label="s.d. 30")
a.plot(Dl[k], 100 * pdl[k], "o", color=BLUE, ms=4); a.plot(Dl[k30], 100 * pd30[k30], "o", color=RED, ms=4)
a.annotate(f"{100*pdl[k]:.1f}% at the optimum", (Dl[k], 100 * pdl[k]), (3, 22), fontsize=7,
           arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
a.set_title("(b) Annual default probability"); a.set_xlabel(r"Debt principal $D$"); a.set_ylabel("%"); a.legend(loc="upper left", fontsize=6.8)
save(fig, "fig3_continuous")
base = dict(opt_D=float(Dl[k]), opt_gain=float(gl[k]), opt_pd=float(pdl[k]),
            zero_D=float(Dl[np.where((gl < 0) & (Dl > Dl[k]))[0][0]]))

# ---------------- Figure 2: sensitivity (one change at a time, two-state)
D2 = np.linspace(0, 70, 701)
fig, ax = plt.subplots(1, 3, figsize=(6.6, 2.2), sharey=True)
panels = [(r"(a) Tax rate $\tau_c$", [("17%", dict(tau=.17)), ("20% (base)", {}), ("30%", dict(tau=.30))]),
          (r"(b) Distress cost $c$", [("5%", dict(c=.05)), ("20% (base)", {}), ("40%", dict(c=.40))]),
          ("(c) Weak / strong cash flow", [("70 / 110", dict(cf=[110, 70])), ("60 / 120 (base)", {}), ("50 / 130", dict(cf=[130, 50]))])]
cols = [TEAL, BLUE, RED]
for a, (title, cases) in zip(ax, panels):
    zero(a)
    for (lab, kw), col in zip(cases, cols):
        kw = dict(kw); cf = np.array(kw.pop("cf", [STRONG, WEAK]), float)
        y = [gain_fixed(D, cf, two_p, **kw)[0] for D in D2]
        a.plot(D2, y, color=col, label=lab, lw=2.2 if "base" in lab else 1.5,
               ls="-" if "base" in lab else ("--" if col == TEAL else "-."))
    a.set_title(title); a.set_xlabel(r"Debt principal $D$"); a.legend(loc="lower left")
ax[0].set_ylabel(r"$V_L - V_U$")
save(fig, "fig2_sensitivity")

# ---------------- Figure 3: Extension 1, market-priced debt (lognormal)
e1 = json.load(open("exp1.json"))
D1 = np.array(e1["D"]); fx = np.array(e1["fixed"]); mk = np.array(e1["market"], float)
loss = np.array(e1["lender_loss"]); rate = np.array(e1["rate"], float)
m = (D1 >= 1) & (D1 <= 60)
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.4))
a = ax[0]; zero(a)
a.plot(D1[m], fx[m], color=BLUE, label=r"$V_L - V_U$, fixed 10% rate")
a.plot(D1[m], mk[m], color=ORANGE, ls="--", label=r"$V_L - V_U$, market-priced debt")
a.plot(D1[m], (fx + loss)[m], color=RED, ls="-.", label="Shareholders' gain, fixed rate")
a.set_title("(a) Value gain under two pricing rules"); a.set_xlabel(r"Debt raised $D$"); a.set_ylabel("Gain relative to all-equity firm")
a.legend(loc="lower left"); a.set_ylim(-3.5, 5.5)
a = ax[1]
a.plot(D1[m], 100 * rate[m], color=ORANGE)
for D in (35, 45, 50, 55):
    a.plot(D, 100 * rate[D], "o", color=ORANGE, ms=3.5)
    a.annotate(f"{100*rate[D]:.1f}%", (D, 100 * rate[D]), (D - 13, 100 * rate[D] + 5), fontsize=7,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
a.set_title("(b) Break-even borrowing rate"); a.set_xlabel(r"Debt raised $D$"); a.set_ylabel("Rate, %"); a.set_ylim(0, 90)
save(fig, "fig4_market_debt")

# ---------------- Figure 4: Extensions 2 and 4
cov = np.array([1, 1.25, 1.5, 2, 2.5, 3, 3.33, 4, 5, 6, 8, 10])
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.9))
a = ax[0]
for cv, col, lab in [(0.28, BLUE, "Volatility 0.28 (our firm)"), (1.0, RED, "Volatility 1.0 (cyclical firm)")]:
    a.plot(cov, [100 * usable_share(x, cv, n=150_000) for x in cov], color=col, ls="--", lw=1.4, label=f"{lab}, loss years only")
    a.plot(cov, [100 * usable_share(x, cv, cap=.30, n=150_000) for x in cov], color=col, label=f"{lab}, + 30% EBIT cap")
a.axvline(1 / 0.3, color=MUTED, ls=":", lw=1)
a.annotate("cap binds below\n3.3× coverage", (3.5, 30), fontsize=7, color=MUTED)
a.set_xscale("log"); a.set_xticks([1, 2, 3, 5, 10]); a.set_xticklabels(["1×", "2×", "3×", "5×", "10×"])
a.set_ylim(25, 102); a.set_title("(a) Usable share of the tax shield")
a.set_xlabel("Interest coverage  E[EBIT] / interest"); a.set_ylabel(r"% of $\tau_c \times$ interest")
from matplotlib.lines import Line2D
a.legend(handles=[Line2D([],[],color=BLUE,label="EBIT volatility 0.28"),Line2D([],[],color=RED,label="EBIT volatility 1.0"),
 Line2D([],[],color=MUTED,ls="--",lw=1.4,label="losses only (no carry-forward)"),Line2D([],[],color=MUTED,label="+ 30%-of-EBIT interest cap")],
 loc="upper center", bbox_to_anchor=(0.5,-0.25), ncol=2, fontsize=7)
a = ax[1]; zero(a)
for sd, col, ls in [(25, BLUE, "-"), (50, RED, "--")]:
    Dm = np.arange(1, 700, 1.0)
    g = np.array([multi_period_gain(D, sd=sd)[0] for D in Dm]); vu = multi_period_gain(10, sd=sd)[1]
    j = int(np.argmax(g))
    a.plot(Dm / vu * 100, g / vu * 100, color=col, ls=ls, label=f"EBIT volatility {sd/90:.2f}")
    a.plot(Dm[j] / vu * 100, g[j] / vu * 100, "o", color=col, ms=4)
    a.annotate(f"{g[j]/vu*100:.1f}% at $D/V_U$ = {Dm[j]/vu*100:.0f}%", (Dm[j] / vu * 100, g[j] / vu * 100),
               ((Dm[j] / vu * 100 + 6, g[j] / vu * 100 + 1.5) if sd == 25 else (2, -5)), fontsize=7,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5))
a.set_ylim(-12, 15); a.set_title("(b) Perpetual firm, perpetual debt"); a.set_xlabel(r"Leverage $D/V_U$, %")
a.set_ylabel(r"$(V_L - V_U)/V_U$, %"); a.legend(loc="upper center", bbox_to_anchor=(0.5,-0.25), ncol=2, fontsize=7)
save(fig, "fig5_shield_multiperiod")

json.dump(base, open("base.json", "w"))
print(base)
