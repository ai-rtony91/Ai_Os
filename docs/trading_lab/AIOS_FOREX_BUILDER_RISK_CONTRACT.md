# AIOS Forex Builder Risk Contract

Packet: `PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT`

## Purpose

The risk contract classifies local forex evidence as `FAIL`, `WATCHLIST`, or `PAPER_FORWARD_READY`. It wraps the existing `automation/forex_engine/edge_gate_policy.py` thresholds and adds explicit live-boundary rejection.

The contract never emits `LIVE_READY` and never treats paper-forward readiness as live readiness.

## Local API

- `classify_risk_gate(backtest_result, walk_forward_summary=None, policy=None) -> RiskGateResult`
- `risk_policy_summary() -> dict`
- `assert_risk_contract_blocks_live(result) -> bool`

## Required Blocks

The contract rejects requests for:

- live readiness
- broker permissions
- real orders or order execution
- network market automation
- credentials, secrets, or env reads/writes
- scheduler or daemon activation
- webhooks

## Relationship To Edge Gate Policy

`risk_contract.py` uses `classify_edge_gate` and `DEFAULT_POLICY` from `edge_gate_policy.py` for metrics thresholds. The risk contract is the higher-level forex-builder safety wrapper around that policy.

## Acceptance

- Only `FAIL`, `WATCHLIST`, and `PAPER_FORWARD_READY` are valid outputs.
- `live_ready` is always `false`.
- `tests/forex_engine/test_risk_contract.py` proves live readiness is blocked.
