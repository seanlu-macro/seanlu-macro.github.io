---
title: "Example: Treasury 2s10s steepener on term-premium rebuild"
date: 2026-06-15
summary: "A DV01-neutral 2s10s steepener, betting that heavier supply pushes term premium higher while the front end stays anchored."
status: closed
asset: Rates
expression: "Long 2y / short 10y Treasury futures, DV01-neutral"
entry: "2s10s at +45bp"
target: "+75bp"
stop: "+30bp"
risk: "1R = 15bp × $50k DV01 = $750k"
horizon: "3 months"
conviction: Medium
closed: 2026-08-20
exit: "+30bp (stopped)"
result: "-1.0R"
---

> **This is an example post** with hypothetical levels, included so you can see how a closed idea and its post-mortem link together. Delete it before you publish real ideas.

## Thesis

Heavier coupon supply should push term premium higher at the long end. The front end should stay anchored by a Fed on hold.

## What the market is pricing

2s10s at +45bp sits near the bottom of its post-normalisation range, with little term premium priced.

## The trade

A DV01-neutral steepener: long 2-year futures and short 10-year futures, sized so that each leg carries $50k per basis point. The position profits if the curve steepens and is insensitive to parallel moves.

## Risks and what would prove me wrong

- A growth scare that rallies the long end (bull flattening).
- Supply being absorbed easily at auctions, with strong demand at the tails.

Stop at +30bp. Review after the August refunding announcement.
