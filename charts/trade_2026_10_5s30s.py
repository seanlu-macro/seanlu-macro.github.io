"""Charts for the Oct 2026 5s30s steepener trade idea.

Data: U.S. Treasury daily par yield curve (charts/data/treasury-par-2026.csv);
CME FedWatch via FXStreet (2 Oct 2026); Sept 2026 FOMC Summary of Economic Projections.
Run from the repo root:  python charts/trade_2026_10_5s30s.py
"""
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from style import apply, save, INK, ACCENT, MUTED, RULE, WIN, LOSS

apply()

# ── Treasury par yields, daily closes: date, 2Y, 5Y, 10Y, 30Y ─────────────────
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "treasury-par-2026.csv"
data = []
with open(DATA) as f:
    for r in csv.DictReader(f):
        data.append((datetime.strptime(r["date"], "%Y-%m-%d"),
                     float(r["2y"]), float(r["5y"]), float(r["10y"]), float(r["30y"])))
by_date = {r[0].date(): r for r in data}
dates = [r[0] for r in data]
s210 = [round((r[3] - r[1]) * 100) for r in data]
s530 = [round((r[4] - r[2]) * 100) for r in data]


# ── 1. Market-implied Fed path vs the Fed's own dots ─────────────────────────
fig, ax = plt.subplots(figsize=(7.2, 3.6))
mkt_x = [datetime(2026, 10, 5), datetime(2026, 12, 9), datetime(2027, 3, 17), datetime(2027, 6, 16)]
mkt_y = [3.875, 4.125, 4.375, 4.625]
ax.step(mkt_x + [datetime(2027, 7, 15)], mkt_y + [4.625], where="post", color=INK, label="Market pricing (fed funds midpoint)")
dot_x = [datetime(2026, 12, 31), datetime(2027, 12, 31)]
ax.plot(dot_x, [4.125, 4.125], color=ACCENT, ls="--", marker="o", markersize=6,
        markeredgecolor="white", markeredgewidth=1.5, label="Fed median dot")
ax.annotate("", xy=(datetime(2027, 6, 30), 4.625), xytext=(datetime(2027, 6, 30), 4.125),
            arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1))
ax.text(datetime(2027, 7, 8), 4.375, "≈50bp more\ntightening priced\nthan the dots", va="center", fontsize=9, color=MUTED)
ax.set_ylim(3.5, 4.9)
ax.set_yticks([3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8])
ax.tick_params(axis="x", pad=6)
ax.spines["bottom"].set_visible(False)
ax.set_xlim(datetime(2026, 9, 20), datetime(2028, 1, 31))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.2f}%"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
ax.set_title("The market prices more Fed hikes than the Fed projects")
ax.legend(loc="lower right", fontsize=9)
fig.text(0.0, -0.02, "Sources: CME FedWatch (2 Oct 2026, via FXStreet); Federal Reserve, Sept 2026.",
         fontsize=8, color=MUTED)
save(fig, "2026-10-fed-path-vs-dots")


# ── 2. Yield change since the Hormuz closure, by maturity ────────────────────
pre, now = by_date[datetime(2026, 2, 27).date()], data[-1]   # 27 Feb vs latest close
labels = ["2Y", "5Y", "10Y", "30Y"]
chg = [round((now[i] - pre[i]) * 100) for i in range(1, 5)]
fig, ax = plt.subplots(figsize=(7.2, 3.4))
colors = [MUTED, ACCENT, MUTED, ACCENT]
ax.set_axisbelow(True)
bars = ax.bar(labels, chg, color=colors, width=0.55)
for b, v in zip(bars, chg):
    ax.text(b.get_x() + b.get_width() / 2, v + 3, f"+{v}bp", ha="center", fontsize=10, color=INK)
ax.set_ylim(0, 180)
ax.set_ylabel("Change in yield (bp)")
ax.set_title("Since 27 Feb, the 5Y has sold off 53bp more than the 30Y")
fig.text(0.0, -0.02, "Change in Treasury par yields, 27 Feb to 5 Oct 2026. Source: U.S. Treasury.",
         fontsize=8, color=MUTED)
save(fig, "2026-10-yield-change-by-maturity")


# ── 3. Curve slopes in 2026 ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.plot(dates, s530, color=ACCENT, label="5s30s")
ax.plot(dates, s210, color=MUTED, lw=1.6, ls="--", label="2s10s")
for x, label in [(datetime(2026, 2, 28), "Hormuz closed"), (datetime(2026, 9, 16), "Fed hikes")]:
    ax.axvline(x, color=RULE, lw=1, zorder=0)
    ax.text(x, 127, label, fontsize=8.5, color=MUTED, ha="center", va="top",
            bbox=dict(fc="white", ec="none", pad=1))
ax.annotate(f"{s530[-1]}bp", (dates[-1], s530[-1]), xytext=(6, 0), textcoords="offset points",
            va="center", fontsize=9, color=ACCENT)
ax.annotate(f"{s210[-1]}bp", (dates[-1], s210[-1]), xytext=(6, 0), textcoords="offset points",
            va="center", fontsize=9, color=MUTED)
i_low = s530.index(min(s530))
ax.plot([dates[i_low]], [s530[i_low]], "o", color=ACCENT, markeredgecolor="white", markeredgewidth=1.5)
ax.annotate(f"5s30s low: {s530[i_low]}bp ({dates[i_low]:%-d %b})", (dates[i_low], s530[i_low]), xytext=(datetime(2026, 8, 20), 8),
            textcoords="data", ha="center", fontsize=8.5, color=MUTED,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_ylim(0, 130)
ax.set_ylabel("Spread (bp)")
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.set_title("A year of bear flattening and the first turn")
ax.legend(loc="lower left", fontsize=9)
fig.text(0.0, -0.02, "30Y minus 5Y and 10Y minus 2Y, daily closes. Source: U.S. Treasury daily par yield curve.",
         fontsize=8, color=MUTED)
save(fig, "2026-10-curve-slopes")


# ── 4. Payoff in R by 5s30s level ────────────────────────────────────────────
E1, E2, STOP, TARGET = 60, 52, 39, 90           # entries, stop and target (bp)
BP_PER_R = (E1 - STOP) + (E2 - STOP)            # 34bp of total movement = 1R
CARRY_R_3M = 0.19                               # net carry, both tranches, 3 months
s = np.linspace(STOP, 95, 200)
both = ((s - E1) + (s - E2)) / BP_PER_R
only1 = (s - E1) / BP_PER_R
r_target = ((TARGET - E1) + (TARGET - E2)) / BP_PER_R
fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.axhline(0, color=MUTED, lw=0.8)
ax.plot(s, both, color=INK, label="Both tranches filled")
ax.plot(s, only1, color=ACCENT, ls="--", label="Tranche 1 only")
for x, lab in [(STOP, f"Stop {STOP}"), (E2, f"Add {E2}"), (E1, f"Entry {E1}"), (TARGET, f"Target {TARGET}")]:
    ax.axvline(x, color=RULE, lw=1, zorder=0)
    ax.text(x, 2.75, lab, ha="center", fontsize=8.5, color=MUTED, bbox=dict(fc="white", ec="none", pad=1))
ax.plot([STOP], [-1], "o", color=LOSS, markeredgecolor="white", markeredgewidth=1.5)
ax.annotate("−1.0R", (STOP, -1), xytext=(8, -4), textcoords="offset points", fontsize=9, color=LOSS)
ax.plot([TARGET], [r_target], "o", color=WIN, markeredgecolor="white", markeredgewidth=1.5)
ax.annotate(f"+{r_target:.1f}R", (TARGET, r_target), xytext=(-40, 2), textcoords="offset points", fontsize=9, color=WIN)
ax.set_xlim(STOP - 4, 97)
ax.set_ylim(-1.5, 3.0)
ax.set_xlabel("5s30s at the close (bp)")
ax.set_ylabel("P&L (R)")
ax.set_title("What the position makes or loses at each level")
ax.legend(loc="upper left", fontsize=9, bbox_to_anchor=(0, 0.88))
fig.text(0.0, -0.08, f"1R = $100,000. Excludes carry (≈ +{CARRY_R_3M:.2f}R over three months with both tranches on).",
         fontsize=8, color=MUTED)
save(fig, "2026-10-5s30s-payoff")
