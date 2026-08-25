"""Build the paired-difference figure for the LLM question-answering evaluation."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# model, family, acc_no_ctx, acc_tut, auroc_no_ctx, auroc_tut
ROWS = [
    ("Qwen2.5-0.5B",    "Qwen2.5",   0.38, 0.39, 0.593, 0.635),
    ("Qwen2.5-1.5B",    "Qwen2.5",   0.55, 0.63, 0.685, 0.787),
    ("Qwen2.5-3B",      "Qwen2.5",   0.80, 0.84, 0.699, 0.800),
    ("Qwen2.5-7B",      "Qwen2.5",   0.88, 0.87, 0.856, 0.878),
    ("Qwen2.5-14B",     "Qwen2.5",   0.93, 0.92, 0.667, 0.840),
    ("Falcon3-1B",      "Falcon3",   0.35, 0.45, 0.616, 0.710),
    ("Falcon3-3B",      "Falcon3",   0.64, 0.67, 0.742, 0.752),
    ("Falcon3-7B",      "Falcon3",   0.84, 0.89, 0.763, 0.820),
    ("Falcon3-10B",     "Falcon3",   0.86, 0.89, 0.859, 0.848),
    ("Phi-3-mini",      "Phi",       0.69, 0.79, 0.783, 0.866),
    ("Phi-3.5-mini",    "Phi",       0.70, 0.82, 0.752, 0.782),
    ("Phi-4-mini",      "Phi",       0.76, 0.83, 0.828, 0.734),
    ("Phi-3-medium",    "Phi",       0.81, 0.89, 0.832, 0.859),
    ("Mistral-7B-v0.3", "Mistral",   0.64, 0.75, 0.784, 0.813),
    ("Ministral-8B",    "Mistral",   0.74, 0.84, 0.766, 0.855),
    ("Mistral-Nemo",    "Mistral",   0.76, 0.78, 0.705, 0.854),
    ("Granite-3.1-2B",  "Granite",   0.56, 0.68, 0.724, 0.820),
    ("Granite-3.1-8B",  "Granite",   0.79, 0.86, 0.699, 0.737),
    ("gemma-3-1b",      "Gemma 3",   0.31, 0.34, 0.548, 0.629),
    ("gemma-3-4b",      "Gemma 3",   0.60, 0.70, 0.608, 0.744),
]

FAMILIES = ["Qwen2.5", "Falcon3", "Phi", "Mistral", "Granite", "Gemma 3"]
COLORS = {
    "Qwen2.5": "#3B6FB6",
    "Falcon3": "#C2703D",
    "Phi":     "#4C9A72",
    "Mistral": "#A45FA0",
    "Granite": "#B5883C",
    "Gemma 3": "#7A7F86",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "axes.edgecolor": "#666666",
    "axes.linewidth": 0.8,
})

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))

panels = [
    ("Accuracy", 2, 3, 0.680, 0.742, axes[0]),
    ("AUROC",    4, 5, 0.725, 0.788, axes[1]),
]

for label, i_a, i_b, mean_a, mean_b, ax in panels:
    for row in ROWS:
        fam = row[1]
        a, b = row[i_a], row[i_b]
        ax.plot([0, 1], [a, b], color=COLORS[fam], alpha=0.55, lw=1.3,
                marker="o", ms=3.6, zorder=2)

    # mean line
    ax.plot([0, 1], [mean_a, mean_b], color="#1A1A1A", lw=2.6,
            marker="o", ms=6, zorder=3)
    ax.annotate(f"mean {mean_a:.3f}", (0, mean_a), textcoords="offset points",
                xytext=(-8, -14), ha="right", fontsize=9, fontweight="bold")
    ax.annotate(f"mean {mean_b:.3f}", (1, mean_b), textcoords="offset points",
                xytext=(8, 6), ha="left", fontsize=9, fontweight="bold")

    ax.set_xlim(-0.42, 1.42)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["No context", "Tutorial"])
    ax.set_ylabel(label)
    ax.set_title(label, fontsize=11, fontweight="bold", pad=9)
    ax.grid(axis="y", color="#DDDDDD", lw=0.7, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

axes[0].axhline(0.25, color="#B03A2E", ls=":", lw=1.1, zorder=1)
axes[0].annotate("chance = 0.25", (1.42, 0.25), textcoords="offset points",
                 xytext=(-2, 4), ha="right", fontsize=8, color="#B03A2E")
axes[1].axhline(0.50, color="#B03A2E", ls=":", lw=1.1, zorder=1)
axes[1].annotate("uninformative = 0.50", (1.42, 0.50), textcoords="offset points",
                 xytext=(-2, 4), ha="right", fontsize=8, color="#B03A2E")

handles = [Line2D([], [], color=COLORS[f], lw=2, marker="o", ms=4, label=f)
           for f in FAMILIES]
fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False,
           bbox_to_anchor=(0.5, -0.015), fontsize=9)

fig.tight_layout(rect=(0, 0.06, 1, 1))
path = OUT / "results_paired.png"
fig.savefig(path, dpi=220, facecolor="white")
print(f"wrote {path}  ({path.stat().st_size/1024:.1f} KB)")
