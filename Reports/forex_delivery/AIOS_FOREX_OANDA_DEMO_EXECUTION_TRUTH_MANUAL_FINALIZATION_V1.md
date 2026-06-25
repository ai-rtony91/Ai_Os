# AIOS Forex OANDA Demo Execution Truth Manual Finalization V1

## Purpose

Provide exact manual validation and finalization commands for the OANDA demo execution truth audit and profit proof bridge packet.

No trade placed by this packet.
No broker call made by this packet.

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/oanda_demo_execution_truth_audit_v1.py automation/forex_engine/oanda_demo_profit_proof_gap_bridge_v1.py automation/forex_engine/oanda_demo_to_live_profit_readiness_truth_v1.py automation/forex_engine/oanda_demo_execution_truth_epic_v1.py scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py tests/forex_engine/test_oanda_demo_execution_truth_audit_v1.py tests/forex_engine/test_oanda_demo_profit_proof_gap_bridge_v1.py tests/forex_engine/test_oanda_demo_to_live_profit_readiness_truth_v1.py tests/forex_engine/test_oanda_demo_execution_truth_epic_v1.py
python -m pytest tests/forex_engine/test_oanda_demo_execution_truth_audit_v1.py tests/forex_engine/test_oanda_demo_profit_proof_gap_bridge_v1.py tests/forex_engine/test_oanda_demo_to_live_profit_readiness_truth_v1.py tests/forex_engine/test_oanda_demo_execution_truth_epic_v1.py -q
python scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py --sample-current-repo
python scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py --sample-current-repo
python scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py --sample-current-repo
python scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py --sample-current-repo --json
python scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py --sample-current-repo --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

Protected actions require Anthony approval. These commands are not executed by this packet.

Do not use `git add .`.

If a feature branch is needed, run the branch command shown below before staging exact files.

```powershell
git checkout -b feature/forex-oanda-demo-execution-truth-audit-v1
git add automation/forex_engine/oanda_demo_execution_truth_audit_v1.py
git add automation/forex_engine/oanda_demo_profit_proof_gap_bridge_v1.py
git add automation/forex_engine/oanda_demo_to_live_profit_readiness_truth_v1.py
git add automation/forex_engine/oanda_demo_execution_truth_epic_v1.py
git add scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py
git add scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py
git add scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py
git add tests/forex_engine/test_oanda_demo_execution_truth_audit_v1.py
git add tests/forex_engine/test_oanda_demo_profit_proof_gap_bridge_v1.py
git add tests/forex_engine/test_oanda_demo_to_live_profit_readiness_truth_v1.py
git add tests/forex_engine/test_oanda_demo_execution_truth_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_AUDIT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_GAP_BRIDGE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_TO_LIVE_PROFIT_READINESS_TRUTH_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex OANDA demo execution truth audit"
git push -u origin feature/forex-oanda-demo-execution-truth-audit-v1
gh pr create --title "Add forex OANDA demo execution truth audit" --body "Build-only OANDA demo execution truth audit and profit proof bridge. No broker call. No trade placed. Broker action remains false." --base main --head feature/forex-oanda-demo-execution-truth-audit-v1 --draft
gh pr checks --watch
gh pr ready <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Stop Condition

Stop if any validator fails, if static safety scan fails, if a command requests credentials or account identifiers, if a broker call would be made, if a trade would be placed, or if any protected action lacks explicit current Anthony approval.
