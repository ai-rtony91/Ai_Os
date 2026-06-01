# Validator Chain Contract

Date: 2026-06-01
Packet: AIOS-P24

## 1. Purpose

The validator chain gives AI_OS one DRY_RUN command that turns configured validator checks into a single JSON receipt before APPLY, commit, push, or merge decisions.

## 2. Canonical Validator Chain Config

Canonical config: `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`.

The config owns validator order, required status, severity, and any future `script_path` or `stop_on_fail` fields. The runner reads this config and must not mutate it.

## 3. Validator Runner

Canonical runner: `automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1`.

The runner resolves the repo root, reads the config, executes validators without APPLY flags, captures output, and prints one JSON receipt to stdout.

## 4. Receipt Schema

Receipts use schema `AIOS_VALIDATOR_CHAIN_RECEIPT.v1` and include `chain_id`, `generated_at`, `chain_result`, counts, and `results[]`. Each result includes `validator_id`, `script_path`, `result`, `exit_code`, `required`, `stop_on_fail`, and `output_preview`.

## 5. Chain Result Meanings

`PASS` means the runner completed and required validators did not fail. `FAIL` means a required validator failed but the chain continued. `BLOCKED` means a required stop-on-fail validator failed, timed out, or was missing.

## 6. Evidence Path

When called with `-WriteEvidence`, the runner writes `telemetry/evidence/VALIDATOR_CHAIN_<timestamp>.json`. Evidence files are generated receipts and should be reviewed before retention or commit decisions.

## 7. Rules For Adding Validators

Add validators by updating the canonical config in a separate approved packet. Prefer explicit `script_path`, `required`, and `stop_on_fail` fields. Validator scripts must be DRY_RUN-safe and must not require mutation flags.

## 8. Supervisor Future Wiring Note

`services/python_supervisor/supervisor_engine.py` currently reports validator state as `NOT_RUN`. Future wiring should consume the JSON receipt path or latest evidence file without running mutation-capable code inside the read-only supervisor layer.

## 9. Safety Boundaries

The runner must not approve APPLY, advance packets, stage, commit, push, start services, install packages, collect secrets, or touch broker/OANDA/live trading paths. Validator output is evidence only, not approval.

## 10. Packet Reference

Created by AIOS-P24 as a validator-chain enforcement layer. Human approval remains required for protected actions.
