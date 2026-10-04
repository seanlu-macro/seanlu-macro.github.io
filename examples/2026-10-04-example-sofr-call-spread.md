---
title: "Example: Positioning for faster Fed cuts with a SOFR call spread"
date: 2026-10-04
summary: "A dovish Fed view expressed with defined risk: a call spread on 3-month SOFR futures that pays about 3x the premium if the market reprices toward my path."
status: open
asset: Rates
expression: "Buy SR3 Dec 96.50 / 97.00 call spread"
entry: "12bp premium"
target: "35bp (spread near full value)"
stop: "Premium at risk; cut if value falls to 4bp"
risk: "1R = 12bp × 400 contracts ≈ $120k"
horizon: "Into December expiry"
conviction: Medium
---

> **This is an example post.** All levels are hypothetical and exist only to show the format: a ticket at the top, then thesis, pricing, expression, risks and a review date. Delete this file (and the other example files) before you publish your first real idea.

## Thesis

Labour-market data are softening faster than the Fed's projections assume. If the next two payroll reports confirm the trend, I expect the Committee to deliver an extra 25bp cut by December beyond what is priced.

## What the market is pricing

The December 3-month SOFR future trades at **96.40**, implying an average rate of \(100 - 96.40 = 3.60\%\) over the contract period. My path implies roughly **3.25%**, or a futures price near **96.75**. That 35bp gap between my view and the market's view is the trade.

## Choosing the expression

The view is about the *level of the policy rate by December*. That points to the front end, and there are four reasonable ways to express it:

| Expression | Max loss | Payoff if right | Why / why not |
|---|---|---|---|
| Long SR3 Dec futures | Open-ended | ~35bp | Cleanest, but a hawkish surprise hurts without limit |
| Buy 96.50 call | Premium (~20bp) | ~25bp net | Defined risk, but expensive for the move I expect |
| **Buy 96.50 / 97.00 call spread** | **Premium (12bp)** | **Up to 38bp** | **Cheap, defined risk; caps gains beyond my target, which I don't need** |
| Receive 2y SOFR swap | Open-ended | Smaller per unit | Also prices the 2027 path, which dilutes the view |

The call spread gives up upside I don't believe in (cuts well beyond 97.00) to make the trade cheaper. I don't mind that trade-off.

## Payoff

![Payoff of the 96.50/97.00 call spread at expiry, in basis points per contract](/images/example-call-spread-payoff.svg "Payoff at expiry. Breakeven is the lower strike plus the premium paid. Hypothetical levels.")

At expiry, with futures price \(F\), strikes \(K_1 < K_2\) and premium \(c\):

$$
\text{P\&L} = \max(F - K_1,\, 0) - \max(F - K_2,\, 0) - c
$$

So the breakeven is \(K_1 + c = 96.62\), the maximum gain is \(K_2 - K_1 - c = 38\text{bp}\), and the reward-to-risk ratio is about **3.2 : 1**. Each basis point on SR3 is worth $25 per contract, so 400 contracts risk about $120k.

## Risks and what would prove me wrong

- **Strong payrolls or sticky core inflation.** Two firm prints would remove the case for an extra cut. I'll cut the trade if spread value falls to 4bp.
- **The cut is delivered later than December.** If my view is right but the timing is wrong, this option expires worthless. It's the main cost of choosing an expiry.
- **A growth scare that is priced too fast.** If futures rally through 97.00 before I'm positioned, the cap means I don't benefit beyond that.

## Review date

After the next two payroll reports, or by the December FOMC at the latest.
