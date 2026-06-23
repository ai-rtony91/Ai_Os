# AIOS Money Relevance Dashboard Rule V11

## Default Visible Money Fields
- `trading_float`
- `available_risk_budget`
- `daily_pl`
- `realized_pl`
- `equity`
- `drawdown`
- `daily_loss_left`
- `capital_cap`
- `sweep_amount`
- `resupply_need`
- `compounding_progress`
- `withdrawal_request_status`
- `broker_proof_status`
- `connector_proof_status`
- `transfer_approval_status`
- `next_money_action`

## Collapsed Fields
- `raw_evidence_paths`
- `legal_governance_detail`
- `validator_logs`
- `repo_noise`
- `css_build_diagnostics`
- `stale_reports`
- `technical_detail`

## Hidden Unless Blocking Fields
- CSS/build diagnostics
- repo noise
- stale reports
- generic technical detail
- raw evidence paths

## Safety Fields That Remain Visible Because They Protect Money
- broker proof status
- connector proof status
- transfer approval status
- risk freeze status
- daily loss left
- maintenance window status

## Dashboard UX Application
The dashboard keeps hot money facts visible and pushes raw evidence, legal/governance detail, validator logs, repo noise, stale reports, and non-blocking technical detail into collapsed drawers.

## Report Application
Reports may retain full evidence detail, but summaries should lead with money, risk, connector, approval, uptime, and maintenance blockers.

## Future 80 Percent Uptime Application
An 80 percent uptime mode must keep capital, risk, connector, approval, maintenance, and incident-readiness signals visible while keeping non-money operational noise collapsed unless blocking.

## Classification Samples
| Field | Value |
|---|---|
| trading_float | `MONEY_RELEVANT_VISIBLE` |
| daily_pl | `MONEY_RELEVANT_VISIBLE` |
| broker_proof_status | `MONEY_RELEVANT_VISIBLE` |
| connector_proof_status | `MONEY_RELEVANT_VISIBLE` |
| validator_logs | `MONEY_RELEVANT_COLLAPSED` |
| raw_evidence_paths | `MONEY_RELEVANT_COLLAPSED` |
| css_build_diagnostics | `MONEY_RELEVANT_COLLAPSED` |
| repo_noise | `MONEY_RELEVANT_COLLAPSED` |
| repo_noise_blocking_money_validation | `MONEY_RELEVANT_COLLAPSED` |
