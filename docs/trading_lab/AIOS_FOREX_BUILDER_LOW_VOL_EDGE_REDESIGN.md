# AIOS Forex Builder Low-Vol Edge Redesign

## Purpose

This packet handles the remaining expanded OOS blocker in `holdout_by_regime:low_vol`.
The previous OOS repair reduced max degradation from `99.5594%` to `64.5594%`, but that
is still too weak for broker-paper readiness.

Low-vol degradation means the simulated edge that works in other regimes does not carry
cleanly into quiet market conditions. In low-vol markets, spread, chop, and small ranges can
consume the expected move before the signal has enough room to work.

## Why 64.5594% Still Blocks

The repair improved degradation by `35.0%`, but the repaired max degradation is still above
the policy floor of `35.0%`. That remains a serious WATCHLIST condition because the heldout
low-vol split is still materially worse than the training evidence.

This is not a real-money loss. AIOS is using deterministic local fixtures and simulated
paper-forward ledgers only. The number is a readiness and generalization risk signal, not an
account PnL statement.

## Low-Vol Controls

The low-vol redesign adds a stricter local policy:

- no-trade gate for weak low-vol opportunities
- minimum range proxy
- minimum momentum proxy
- spread-to-range rejection
- volatility expansion confirmation
- signal quality threshold
- low-vol position size reduction or zero size
- retained audit evidence for every rejected low-vol intent

If the no-trade gate is used, AIOS must label it as `NO_TRADE_GATE`. It is acceptable to refuse
weak low-vol trades when the edge is not proven. It is not acceptable to treat that refusal as
profitable low-vol trading.

## Reading WATCHLIST Honestly

`WATCHLIST` means the evidence is useful but not clean enough to advance into broker-paper
adapter work. It is not a hidden pass, and it is not live readiness.

If low-vol remains WATCHLIST, the next safe packet is deeper low-vol research:
`PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-RESEARCH-V2`.

If low-vol passes through a no-trade gate, the operator should read that as:

- AIOS can avoid the weak regime.
- AIOS has not proven a profitable low-vol edge.
- Broker-paper is still blocked until stress/OOS are stable and the pre-security gate lands.

## Broker-Paper Boundary

OOS repair and low-vol redesign do not create broker readiness. Broker-paper still requires:

`PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1`

That gate must define secrets, network, broker SDK, adapter, account, order, logging, and stop
controls before any broker-paper adapter work. This packet does not read credentials, use
network APIs, place orders, register webhooks, or activate schedulers or daemons.
