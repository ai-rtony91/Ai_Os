# AIOS Forex Builder OOS Repair

## Purpose

This note explains the paper-only expanded out-of-sample repair lane for
`PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1`.

OOS degradation means the local simulated result gets much weaker when a split is
held out from the training side of the deterministic fixture set. It is not a
real-money loss. It is a warning that the current simulated edge may not survive
new market conditions.

## Current Blocker

The expanded OOS gate exposed a serious WATCHLIST blocker:

- Weakest split: `holdout_by_regime:low_vol`
- Max degradation pct: `99.5594`
- Broker-paper contract ready: false
- Live ready: false
- Protected gate required: true

A 99.5594 percent degradation is severe because the model nearly loses the
training-side edge when low-volatility fixtures are held out. The honest response
is to reduce exposure and improve the low-vol edge, not lower the threshold or
delete the weak split.

## Repair Method

The repair is local and deterministic. It adds:

- low-volatility regime detection
- minimum range and momentum proxies
- spread-to-range sanity checks
- low-vol size reduction
- skipped low-vol intent audit evidence
- degradation improvement tracking
- a maximum allowed degradation floor that is not lowered

The repair can improve the degradation number while still leaving the system in
WATCHLIST. That is expected when the repaired degradation remains above policy.

## How To Read WATCHLIST

WATCHLIST means the evidence improved or remains informative, but it is not
strong enough for broker-paper promotion. It is not failure hiding. It is also
not approval to trade.

In this lane, WATCHLIST points to the next safe packet:

`PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1`

## Broker And Live Boundary

OOS repair is not live readiness.

This packet does not:

- connect to a broker
- read credentials
- read `.env`
- call market APIs
- place broker-paper orders
- place real orders
- start a scheduler
- start a daemon
- send webhooks

Even if OOS and stress repair both pass later, broker-paper still requires:

`PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1`

That pre-security gate must define secrets, network, broker, account, audit, and
kill-switch boundaries before any adapter work.
