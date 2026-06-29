# AIOS Forex Broker Account Capability Checklist V1

## Scope
Offline readiness artifact for `BROKER_ACCOUNT_READINESS` evidence capture.  
No broker API access, credentials, or live/demo orders were used to produce this checklist.

## Checklist

### Demo account status
- Account environment identified: Not directly queried this cycle.
- Evidence status: `review-required` using repo-provided readiness reports.
- Required confirmation for this stage: owner must confirm demo account exists and is mapped to the correct broker sandbox/demo profile.

### Live account status
- Account environment identified: Not directly queried this cycle.
- Evidence status: `review-required` using repo-owned readiness artifacts.
- Required confirmation for this stage: owner must confirm live account identity and ownership before arming consideration.

### Instrument permissions
- Evidence status: `required` from policy documents and adapter readiness logs.
- Required confirmation for this stage: owner must verify symbols / instruments are enabled and compliant for EURUSD and policy test universe.

### Margin / leverage visibility
- Evidence status: `required` from risk governance docs.
- Required confirmation for this stage: owner confirms margin model and leverage settings are known and enforced in broker platform settings.

### Account mode
- Evidence status: `required` from risk and governance controls.
- Required confirmation for this stage: owner confirms account mode (netting/hedging) and whether it matches strategy assumptions.

### Endpoint separation
- Evidence status: `required` from architecture constraints.
- Required confirmation for this stage: demo/live endpoints kept physically and operationally separated; production-only credentials are never used in this repo-safe stage.

### Max loss policy
- Evidence status: `present` (`max_loss_policy_present`)
- Required confirmation for this stage: owner confirms policy values are active in the broker-side risk controls where applicable.

### Daily stop policy
- Evidence status: `present` (`daily_stop_policy_present`)
- Required confirmation for this stage: owner confirms broker-side daily stop limits are at or above repo hard-stop expectations.

### Position sizing policy
- Evidence status: `present` (`position_size_policy_present`)
- Required confirmation for this stage: owner confirms position sizing caps are aligned with documented policy and account constraints.

### Kill switch
- Evidence status: `present` via offline governance and arming checklists.
- Required confirmation for this stage: owner confirms immediate disable path exists and is tested in operational playbook.

### Audit logging
- Evidence status: `review-required`
- Required confirmation for this stage: owner confirms audit records are available for readiness checks (decision logs, limit checks, and account config snapshots).

## Rollback / disable plan
- Pre-arming condition: all checks in this artifact must be explicitly accepted by owner.
- Disable path:
  1. Mark environment as `HOLD` in promotion tracker.
  2. Revoke manual readiness consent.
  3. Remove/ignore any live arming artifacts until owner re-approves.
- Triggered rollback events:
  - incorrect account mapping
  - mismatched broker endpoint or credentials policy
  - margin/leverage or instrument mismatch
  - incomplete audit evidence
- Recovery action:
  - retain all offline artifacts.
  - rerun readiness review after correction.

## Signoff fields
- checklist completeness: `pending manual owner review`
- broker API used: `no`
- credentials used: `no`
- orders placed: `no`
