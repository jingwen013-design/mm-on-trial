"""Shared figure style and helpers for figs.py and fig_firms.py."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    "pdf.fonttype": 42,   # embed TrueType fonts so the PDFs print and search correctly
})


def zero(ax):
    ax.axhline(0, color="#999999", lw=0.6, ls=":", zorder=1)


def save(fig, name, tight=True):
    """Write fig/<name>.pdf (for the paper) and fig/<name>.png (for the notebook)."""
    os.makedirs("fig", exist_ok=True)
    if tight:
        fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"fig/{name}.{ext}", bbox_inches="tight", facecolor="white",
                    metadata={"CreationDate": None} if ext == "pdf" else None)
    plt.close(fig)
