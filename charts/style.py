"""
Shared chart style so every chart matches the site.

    from style import apply, INK, ACCENT, MUTED, save
    apply()
    fig, ax = plt.subplots()
    ...
    save(fig, "my-chart")        # -> content/images/my-chart.svg
"""
import logging
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

INK = "#1c1b19"      # main series
ACCENT = "#1f3a5f"   # second series / highlights
MUTED = "#67635b"    # labels, annotations
RULE = "#e4e0d6"     # gridlines
WIN = "#2e6b4a"
LOSS = "#a23b2e"
SERIES = [INK, ACCENT, "#b07a2a", "#6d7f8f"]   # fixed order, never cycle past 4

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # quiet font fallbacks

IMAGES = Path(__file__).resolve().parent.parent / "content" / "images"


def apply() -> None:
    mpl.rcParams.update({
        "figure.figsize": (7.2, 4.0),
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "font.family": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "axes.edgecolor": RULE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": RULE,
        "grid.linewidth": 0.8,
        "axes.titlesize": 11,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlepad": 12,
        "axes.prop_cycle": mpl.cycler(color=SERIES),
        "lines.linewidth": 2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "svg.fonttype": "none",       # keep text as text: crisp and searchable
    })


def save(fig, name: str) -> Path:
    IMAGES.mkdir(parents=True, exist_ok=True)
    path = IMAGES / f"{name}.svg"
    fig.savefig(path, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"Saved {path}")
    return path
