# AIOS Forex Builder Stress Repair

## Purpose

Stress repair is a local-only validation layer for paper-forward forex evidence. It diagnoses why stress/OOS remains WATCHLIST and applies conservative, deterministic repair policies such as stress-aware sizing, opportunity quality filtering, cost-drag safeguards, and drawdown caps.

This makes the paper-forward evidence harder to fool. It does not make the simulated PnL bigger by loosening gates.

## Current Blocker

The current WATCHLIST blocker is useful evidence:

- half-capture-rate stress is below the policy floor.
- disaster stress still exposes negative worst-case PnL.
- broker-paper sandbox contract readiness remains false.
- live readiness remains false.

WATCHLIST means the local result is promising but not robust enough for the next protected adapter-stub contract.

## Repair Rules

Stress repair may:

- rank opportunities by local simulated quality.
- retain higher-quality simulated intents.
- skip estimated lower-quality intent slices.
- reduce size in high-cost or high-drawdown stress regimes.
- cap disaster-case loss exposure.
- explain the half-capture blocker.

Stress repair must not:

- lower thresholds to force a pass.
- inflate PnL.
- hide losing or weak scenarios.
- remove disaster stress from evidence.
- connect to a broker.
- read credentials or `.env`.
- place paper or live orders.
- use network/API data.

## Half-Capture Interpretation

Half-capture stress asks whether the strategy survives when only a degraded portion of expected opportunity is captured. If local PnL remains positive but effective capture is below policy, the result can remain WATCHLIST. That is honest and preferred over pretending the gate passed.

## Tradeoff

Risk-to-reward and expectancy optimization are not the same as overtrading. The repair layer favors:

- stress survival over maximum simulated PnL.
- drawdown control over oversized exposure.
- cost/slippage resilience over optimistic fills.
- opportunity quality filtering over taking every signal.

Reducing PnL to improve survival is acceptable. Hiding blockers is not.

## Demo

```powershell
python -m automation.forex_engine.run_stress_repair_demo
```

The demo prints original stress classification, repaired stress classification, worst stress PnL before/after repair, retained/skipped intents, tradeoff summary, blocker status, and safety boundaries.

## Protected Next Steps

If stress repair remains WATCHLIST, the next safe packet is:

```text
PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1
```

If stress repair eventually reaches PAPER_FORWARD_READY and the broker-paper readiness contract is contract-ready, a future protected adapter-stub contract can be considered:

```text
PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT
```

That future adapter-stub contract is still not broker integration. Broker selection, credentials, paper account access, network/API use, order translation, kill switch, audit logging, daily loss limits, and Human Owner confirmation all require separate protected approval.

## Safety Boundary

This is local simulation only. No broker integration, broker paper orders, live orders, credentials, `.env`, webhooks, scheduler/daemon activation, network/API ingestion, queue mutation, approval mutation, or Reports writes are authorized.
