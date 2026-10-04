"""Payoff at expiry of a SOFR futures call spread (example post)."""
import numpy as np
import matplotlib.pyplot as plt
from style import apply, save, INK, MUTED, RULE

apply()

K1, K2, PREMIUM = 96.50, 97.00, 0.12          # strikes and premium, price points
F = np.linspace(96.00, 97.50, 400)            # futures price at expiry
pnl_bp = (np.maximum(F - K1, 0) - np.maximum(F - K2, 0) - PREMIUM) * 100

fig, ax = plt.subplots()
ax.axhline(0, color=MUTED, linewidth=0.8)
ax.plot(F, pnl_bp, color=INK)
ax.set_title("Call spread payoff at expiry, bp per contract")
ax.set_xlabel("Futures price at expiry  (implied rate = 100 − price)")
ax.set_xlim(F[0], F[-1])
ax.set_ylim(-25, 50)

be = K1 + PREMIUM
ax.annotate(f"Max loss  −{PREMIUM*100:.0f}bp", (96.15, -PREMIUM*100), xytext=(0, -16),
            textcoords="offset points", color=MUTED, fontsize=9)
ax.annotate(f"Max gain  +{(K2-K1-PREMIUM)*100:.0f}bp", (97.12, (K2-K1-PREMIUM)*100),
            xytext=(0, 8), textcoords="offset points", color=MUTED, fontsize=9)
ax.plot([be], [0], "o", color=INK, markersize=6, markeredgecolor="white", markeredgewidth=1.5)
ax.annotate(f"Breakeven {be:.2f}", (be, 0), xytext=(8, -16), textcoords="offset points",
            color=MUTED, fontsize=9)
for k in (K1, K2):
    ax.axvline(k, color=RULE, linewidth=0.8, zorder=0)

save(fig, "example-call-spread-payoff")
