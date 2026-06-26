# AIOS Forex OANDA Demo Expectancy To Live Evidence Bundle Manual Finalization V1

## Purpose

Provide exact manual validation and finalization commands for Anthony after shell access is available.

No trade placed by this packet.

No broker call was made by this packet.

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/oanda_demo_live_evidence_requirement_matrix_v1.py automation/forex_engine/oanda_demo_expectancy_to_live_gap_mapper_v1.py automation/forex_engine/oanda_demo_live_evidence_bundle_gap_gate_v1.py automation/forex_engine/oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py scripts/forex_delivery/run_oanda_demo_live_evidence_requirement_matrix_v1.py scripts/forex_delivery/run_oanda_demo_expectancy_to_live_gap_mapper_v1.py scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py tests/forex_engine/test_oanda_demo_live_evidence_requirement_matrix_v1.py tests/forex_engine/test_oanda_demo_expectancy_to_live_gap_mapper_v1.py tests/forex_engine/test_oanda_demo_live_evidence_bundle_gap_gate_v1.py tests/forex_engine/test_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py
python -m pytest tests/forex_engine/test_oanda_demo_live_evidence_requirement_matrix_v1.py tests/forex_engine/test_oanda_demo_expectancy_to_live_gap_mapper_v1.py tests/forex_engine/test_oanda_demo_live_evidence_bundle_gap_gate_v1.py tests/forex_engine/test_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py -q
python scripts/forex_delivery/run_oanda_demo_live_evidence_requirement_matrix_v1.py --sample-ready
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_gap_mapper_v1.py --sample-missing-live-evidence --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_gap_mapper_v1.py --sample-partial-live-evidence --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_gap_mapper_v1.py --sample-ready-gap-review --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-missing-live-evidence --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-partial-live-evidence --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-ready-gap-review --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-blocked-expectancy --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-unsafe --json
python scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py --sample-missing-live-evidence --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

These commands are manual only and require separate Anthony approval before any protected action.

```powershell
git checkout -b feature/forex-oanda-demo-expectancy-to-live-evidence-gap-v1 if needed
git add automation/forex_engine/oanda_demo_live_evidence_requirement_matrix_v1.py
git add automation/forex_engine/oanda_demo_expectancy_to_live_gap_mapper_v1.py
git add automation/forex_engine/oanda_demo_live_evidence_bundle_gap_gate_v1.py
git add automation/forex_engine/oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py
git add scripts/forex_delivery/run_oanda_demo_live_evidence_requirement_matrix_v1.py
git add scripts/forex_delivery/run_oanda_demo_expectancy_to_live_gap_mapper_v1.py
git add scripts/forex_delivery/run_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py
git add tests/forex_engine/test_oanda_demo_live_evidence_requirement_matrix_v1.py
git add tests/forex_engine/test_oanda_demo_expectancy_to_live_gap_mapper_v1.py
git add tests/forex_engine/test_oanda_demo_live_evidence_bundle_gap_gate_v1.py
git add tests/forex_engine/test_oanda_demo_expectancy_to_live_evidence_bundle_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAPPER_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex OANDA demo expectancy to live evidence gap bridge"
git push -u origin feature/forex-oanda-demo-expectancy-to-live-evidence-gap-v1
gh pr create --title "Add forex OANDA demo expectancy to live evidence gap bridge" --body "Build-only OANDA demo expectancy to live evidence bundle gap bridge. No broker call. No trade placed. Live trading remains false." --base main --head feature/forex-oanda-demo-expectancy-to-live-evidence-gap-v1 --draft
gh pr checks --watch
gh pr ready <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Permissions False

- demo_execution_allowed: false
- broker_action_allowed: false
- real_money_allowed: false
- compounding_allowed: false
- bank_movement_allowed: false
- live_trading_allowed: false
- credential_access_allowed: false
- account_id_persistence_allowed: false
- autonomous_execution_allowed: false
- scheduler_allowed: false
- daemon_allowed: false
- webhook_allowed: false
- live_micro_trade_exception_allowed: false
- live_evidence_bundle_approved: false

## Stop Condition

Stop if any command asks to call a broker, access credentials, read account identifiers, place an order, approve live trading, move money, compound, or use a broad staging command.
