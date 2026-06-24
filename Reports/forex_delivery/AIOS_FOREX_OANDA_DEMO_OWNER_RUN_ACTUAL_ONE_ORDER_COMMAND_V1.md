# AIOS Forex OANDA Demo Owner Run Actual One Order Command V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-OWNER-RUN-ACTUAL-ONE-ORDER-COMMAND-V1

Branch: feature/forex-oanda-demo-owner-run-actual-one-order-command-v1

Mission outcome: created the owner-facing command package generator, command-only CLI wrapper, and tests for one protected OANDA demo order command path.

## Why This Is The Final Owner Command Surface

This packet sits after `AIOS_FOREX_OANDA_DEMO_BROKER_CALL_IMPLEMENTATION_ONE_ORDER_MANUAL_RUN_V1`. It consumes broker-call readiness, validates explicit owner command approval, validates demo-only command context, and emits the copy-pasteable PowerShell command template Anthony can run later after this PR lands.

The command package is final because it binds the one-order command surface to the previously built broker-call manual-run script while keeping runtime credentials external, requiring explicit owner confirmations, and documenting the pre-run and post-run evidence checklist.

## Why This PR Does Not Place A Trade

This PR does not call OANDA, does not call a broker, does not read `.env`, does not read credentials, does not read account identifiers, does not persist runtime material, and does not place a demo or live order.

The new script is a command generator only. It has no execute flag and prints JSON command package output, command template output, or checklist output.

## Broker-Call Implementation Dependency

The broker-call result must have status `BROKER_CALL_DRY_RUN_READY` or `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED`. It must also prove broker network call false, order placement false, and all execution authority fields false.

## Owner Approval Requirements

Anthony must approve or confirm:

- actual one-order command
- demo-only
- no live money
- one order only
- max one attempt
- stop loss
- take profit
- loss possible
- no profit guarantee
- no second order
- manual run only
- no autonomous execution
- post-trade evidence required
- runtime credentials external

## Command Context Requirements

The command context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo endpoint only
- live endpoint absent
- runtime token external
- runtime account ID external
- credential persistence false
- account ID persistence false
- one order only true
- max order attempts 1
- order already attempted false
- kill switch ready
- daily stop ready
- max loss gate ready
- pre-trade evidence ready
- post-trade evidence plan ready

## Exact Command Template Behavior

The generated command template is PowerShell-oriented and calls:

`scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py`

It includes `--execute-demo-order`, all required owner confirmation flags, runtime-only placeholders for `OANDA_DEMO_ACCESS_TOKEN` and `OANDA_DEMO_ACCOUNT_ID`, order placeholders for instrument, direction, units, stop loss, take profit, risk amount, and client order ID, plus one-order-only and evidence reminders.

## Dry-Run Behavior

With no flags, the wrapper prints JSON with:

- `script_status: OWNER_COMMAND_DRY_RUN_PACKAGE`
- broker network call false
- order placement false
- credential read false
- account ID read false
- decision package containing the final owner command template

## Checklist Behavior

With `--print-checklist`, the wrapper prints JSON containing only the pre-run checklist and post-run evidence checklist. It does not print or execute the broker-call command.

## One-Order Cap

The evaluator requires one-order-only true, max order attempts 1, and order already attempted false. The command template itself warns `ONE ORDER ONLY` and instructs the owner not to rerun after one attempt.

## Runtime Credential Placeholder Rule

The command template includes placeholders only. Real OANDA demo token and account ID values must be supplied externally at runtime by Anthony and must not be committed, printed into reports, or persisted in repo files.

## No Live Endpoint Rule

The command context requires demo endpoint only and live endpoint absent. Live trading remains blocked.

## No Credential Or Account Persistence

The evaluator and script read no credentials, read no account IDs, read no `.env`, and persist no credential or account identifier material.

## Execution Authority False

All execution authority fields remain false:

- execution_allowed
- demo_order_allowed
- live_order_allowed
- broker_write_allowed
- autonomous_order_allowed
- scheduler_allowed
- daemon_allowed
- webhook_allowed

The command package is an owner manual command surface only. Repo/governance execution authority remains false.

## Validation Results

Targeted validation before report creation:

- `python -m py_compile automation/forex_engine/oanda_demo_owner_run_actual_one_order_command_v1.py tests/forex_engine/test_oanda_demo_owner_run_actual_one_order_command_v1.py scripts/forex_delivery/run_oanda_demo_owner_run_actual_one_order_command_v1.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_owner_run_actual_one_order_command_v1.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-owner-run-actual-one-order-command-v1` with four scoped owner-command files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

After this PR lands, prepare:

`AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1`

Anthony may then use the generated command template manually under the approved demo-only, one-order-only, runtime-credential-only, evidence-bound constraints. Codex must not run the broker command.
