"""Figure E1: operating profit and interest of SIA and Sheng Siong (firms.json)."""
import json, numpy as np
import matplotlib.pyplot as plt
from style import ORANGE, RED, INK, MUTED, zero, save
F = json.load(open("firms.json"))
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.5))
for a, (name, scale, unit) in zip(ax, [("SIA", 1000, "S$ bn"), ("Sheng Siong", 1, "S$ m")]):
    f = F[name]; x = np.array(f["ebit"]) / scale; it = np.array(f["interest"]) / scale
    yrs = [y.replace("FY", "").split("/")[1] if "/" in y else y[2:] for y in f["years"]]
    cols = [RED if v < 0 else "#7FA6D6" for v in x]
    a.bar(range(len(x)), x, color=cols, width=0.72, zorder=2, label="Operating profit (EBIT)")
    a.plot(range(len(x)), it, color=ORANGE, marker="o", ms=2.8, lw=1.4, zorder=3, label="Interest / finance charges")
    zero(a)
    a.set_xticks(range(len(x))); a.set_xticklabels(yrs, fontsize=7)
    a.set_ylabel(unit)
    if name == "SIA":
        a.set_title("(a) Singapore Airlines")
        a.annotate("FY20/21: loss S\\$2.5bn vs interest\nS\\$0.27bn; S\\$8.8bn of rights\nand bonds backed by Temasek",
                   (11, -2.5), (0.2, -2.45), fontsize=7, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
        a.set_ylim(-3.0, 3.2); a.set_xlabel("Fiscal year ending March, 20xx")
    else:
        a.set_title("(b) Sheng Siong")
        a.text(-0.4, 212, "No bank debt; a S\\$30m government term loan\nin 2020–21; interest is lease interest (from 2019)", fontsize=7, color=INK, va="top")
        a.set_ylim(0, 215); a.set_xlabel("Year")
h, l = ax[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.04), fontsize=7.5)
fig.tight_layout(rect=(0, 0.06, 1, 1))
save(fig, "figE1_firms", tight=False)
