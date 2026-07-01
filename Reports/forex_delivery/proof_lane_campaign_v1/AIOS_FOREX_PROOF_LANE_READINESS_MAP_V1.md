# AIOS Forex Proof Lane Readiness Map V1

## 1. Status
`PARTIAL`

## 2. Current repo baseline
- Observed pre-campaign state: `main` was clean and synced with `origin/main` at `9e0c6d0fdf747fc3721eccde28cd559cbf940496`.
- Campaign branch for this report set: `feature/forex-proof-lane-parallel-campaign-v1`.
- Evidence base includes `automation/forex_engine/config.py`, `automation/forex_engine/risk.py`, `automation/forex_engine/risk_management.py`, `automation/forex_engine/paper_operator.py`, `automation/forex_engine/metrics.py`, `automation/forex_engine/backtest.py`, `tests/forex_engine/test_risk_management.py`, `tests/forex_engine/test_paper_operator.py`, `docs/dashboard/AIOS_MINIMAL_OPERATOR_DASHBOARD_CONTRACT_V1.md`, `docs/governance/source-of-truth-map.md`, `README.md`, and `RISK_POLICY.md`.
- The repo already carries strong paper-only and read-only proof surfaces, but it does not yet carry a canonical non-secret receipt schema or any broker-authorized proof record.

## 3. Proof Lane objective
- Make the Forex Proof Lane easier to advance without crossing into live trading, broker calls, or secret handling.
- Separate proof readiness, receipt evidence, drawdown limits, demo rehearsal, repeatability, and dashboard projection into distinct governed artifacts.
- Keep the campaign focused on preparation, not execution.

## 4. Demo-proof preparation requirements
- A demo-proof lane needs a sanitized receipt shape, a dry-run validator, and a fixture set that can be replayed locally without network access.
- The receipt shape must be non-secret and must not assume real broker IDs, live endpoints, or account identifiers.
- The demo rehearsal must prove only the structure of the evidence path, not an order route or profit outcome.
- Validation must stay local and deterministic.

## 5. Owner approval requirements
- Any future broker-authorized demo or live proof step needs current-session Human Owner approval with exact scope.
- Approval must name the instrument, side, order type, units, stop loss, take profit, max loss, approval window, and stop point.
- Approval must be explicit for the exact packet or execution lane and must not be inferred from prior work.
- Historical approval artifacts do not authorize this campaign.

## 6. Broker-boundary requirements
- This campaign cannot call OANDA, a demo broker, or a live broker.
- This campaign cannot read credentials, account IDs, tokens, raw broker payloads, or live order identifiers.
- Paper-only modules may be inspected for risk math, but they cannot be treated as broker proof.
- Any broker-facing evidence belongs in a separately approved lane.

## 7. Receipt evidence requirements
- Receipts must identify the run, lane, symbol, order intent, fill result, risk controls, and validation state.
- Receipts must be sanitized before storage and must keep raw identifiers redacted.
- Receipts must carry an integrity anchor such as a raw-receipt hash instead of raw payload storage.
- Receipts must link to owner approval and validator status so they can be audited without leaking private data.

## 8. Live-micro exception prerequisites
- A live-micro exception remains a separate governed exception under `RISK_POLICY.md`.
- It requires explicit current approval, runtime-only credentials, one-order-only enforcement, micro-size enforcement, stop loss, take profit, max loss gate, daily stop gate, kill-switch validation, and sanitized evidence.
- It also requires a broker-safe preflight and a hard stop after the one approved order.
- None of those live prerequisites are satisfied by this campaign.

## 9. Claims allowed
- Paper-only proof readiness mapping.
- Evidence gap mapping.
- Demo-proof preparation planning.
- Read-only dashboard/source-of-truth projection planning.
- Validation acceleration planning.

## 10. Claims blocked
- Live-ready.
- Broker-verified.
- Profit-proven.
- Demo-executed.
- Micro-trade authorized.
- Account-authoritative.
- Institutional-ready.

## 11. Readiness matrix

| Area | Classification | Notes |
|---|---|---|
| Paper-only engine and risk scaffolding | `PRESENT` | Local config, risk, backtest, metrics, and tests exist. |
| Demo-proof receipt schema | `ABSENT` | No canonical non-secret receipt envelope is present yet. |
| Owner approval capture for this campaign | `PARTIAL` | Governance exists, but no campaign-specific approval record is in scope here. |
| Broker boundary enforcement | `BLOCKED_BY_GOVERNANCE` | No broker calls, live calls, or credential reads are permitted. |
| Live-micro exception readiness | `UNSAFE_CURRENT_PHASE` | Too many separate prerequisites remain unresolved. |
| Demo rehearsal path | `PARTIAL` | A dry-run rehearsal can be mapped, but not executed as broker-authorized proof. |
| Dashboard proof projection | `PARTIAL` | Read-only projection contracts exist, but proof-lane state is not canonical yet. |
| Repeatability evidence trail | `PARTIAL` | Deterministic evidence exists, but no unified ledger contract owns it yet. |
