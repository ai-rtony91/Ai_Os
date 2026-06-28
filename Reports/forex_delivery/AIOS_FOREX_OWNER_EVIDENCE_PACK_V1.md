# Forex Owner Evidence Pack V1
Generated: 2026-06-28T00:08:17.032371+00:00
- Strict mode: True
- Include templates: True

- Requested items: 17
## candidate evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: candidate_evidence_evidence.md
## walk-forward evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: walk-forward_evidence_evidence.md
## out-of-sample evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: out-of-sample_evidence_evidence.md
## demo trade telemetry
- classification: TRADING_EXECUTION_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: demo_trade_telemetry_evidence.md
## broker snapshot evidence
- classification: BROKER_API_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: broker_snapshot_evidence_evidence.md
## execution readiness evidence
- classification: TRADING_EXECUTION_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: execution_readiness_evidence_evidence.md
## risk control evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: risk_control_evidence_evidence.md
## expectancy/profit-factor evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: expectancy/profit-factor_evidence_evidence.md
## drawdown evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: drawdown_evidence_evidence.md
## sample sufficiency evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: sample_sufficiency_evidence_evidence.md
## owner approval evidence
- classification: OWNER_EVIDENCE_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: owner_approval_evidence_evidence.md
## live exception evidence
- classification: PROTECTED_PUBLISH_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: live_exception_evidence_evidence.md
## credential boundary evidence
- classification: CREDENTIAL_REQUIRED
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: credential_boundary_evidence_evidence.md
## kill-switch evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: kill-switch_evidence_evidence.md
## monitoring/alert evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: monitoring/alert_evidence_evidence.md
## audit log evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: audit_log_evidence_evidence.md
## final bundle evidence
- classification: LOCAL_REPAIRABLE
- instruction: Collect this evidence through local-only deterministic evidence sources.
- expected_filename: final_bundle_evidence_evidence.md

## Redaction Rules
- Remove all account identifiers.
- Remove authentication values.
- Remove credential-like fragments.
- Remove direct endpoint and host labels.
- Do not include order command text.

## Collection Checklist
- Collect requested evidence from local-only outputs.
- Apply all redaction rules before upload.
- Confirm evidence entry names.
- Mark `access_status` for each item.
- Attach only deterministic local files.

## Templates
### candidate evidence
Template for candidate evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### walk-forward evidence
Template for walk-forward evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### out-of-sample evidence
Template for out-of-sample evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### demo trade telemetry
Template for demo trade telemetry
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### broker snapshot evidence
Template for broker snapshot evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### execution readiness evidence
Template for execution readiness evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### risk control evidence
Template for risk control evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### expectancy/profit-factor evidence
Template for expectancy/profit-factor evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### drawdown evidence
Template for drawdown evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### sample sufficiency evidence
Template for sample sufficiency evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### owner approval evidence
Template for owner approval evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### live exception evidence
Template for live exception evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### credential boundary evidence
Template for credential boundary evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### kill-switch evidence
Template for kill-switch evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### monitoring/alert evidence
Template for monitoring/alert evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### audit log evidence
Template for audit log evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name
### final bundle evidence
Template for final bundle evidence
source evidence can be pasted here after redaction.
required fields:
- evidence_location
- observed_metric
- sample_count
- decision_basis
- validation_status
- evidence_file_name