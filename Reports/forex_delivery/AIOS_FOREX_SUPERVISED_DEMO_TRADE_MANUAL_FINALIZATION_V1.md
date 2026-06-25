# AIOS Forex Supervised Demo Trade Manual Finalization V1

## Manual Validation

Run these from `C:\Dev\Ai.Os` in PowerShell:

```powershell
python -m py_compile automation/forex_engine/supervised_demo_trade_epic_v1.py automation/forex_engine/broker_read_only_snapshot_contract_v1.py automation/forex_engine/demo_account_readiness_gate_v1.py automation/forex_engine/demo_trade_risk_gate_v1.py automation/forex_engine/demo_position_sizer_v1.py automation/forex_engine/demo_order_plan_builder_v1.py automation/forex_engine/demo_operator_execution_ticket_v1.py automation/forex_engine/post_trade_evidence_capture_v1.py automation/forex_engine/demo_trade_feedback_router_v1.py scripts/forex_delivery/run_supervised_demo_trade_epic_v1.py scripts/forex_delivery/run_demo_order_plan_builder_v1.py scripts/forex_delivery/run_post_trade_evidence_capture_v1.py tests/forex_engine/test_supervised_demo_trade_epic_v1.py tests/forex_engine/test_broker_read_only_snapshot_contract_v1.py tests/forex_engine/test_demo_account_readiness_gate_v1.py tests/forex_engine/test_demo_trade_risk_gate_v1.py tests/forex_engine/test_demo_position_sizer_v1.py tests/forex_engine/test_demo_order_plan_builder_v1.py tests/forex_engine/test_demo_operator_execution_ticket_v1.py tests/forex_engine/test_post_trade_evidence_capture_v1.py tests/forex_engine/test_demo_trade_feedback_router_v1.py
python -m pytest tests/forex_engine/test_supervised_demo_trade_epic_v1.py tests/forex_engine/test_broker_read_only_snapshot_contract_v1.py tests/forex_engine/test_demo_account_readiness_gate_v1.py tests/forex_engine/test_demo_trade_risk_gate_v1.py tests/forex_engine/test_demo_position_sizer_v1.py tests/forex_engine/test_demo_order_plan_builder_v1.py tests/forex_engine/test_demo_operator_execution_ticket_v1.py tests/forex_engine/test_post_trade_evidence_capture_v1.py tests/forex_engine/test_demo_trade_feedback_router_v1.py -q
python scripts/forex_delivery/run_supervised_demo_trade_epic_v1.py --sample-ready
python scripts/forex_delivery/run_supervised_demo_trade_epic_v1.py --sample-blocked
python scripts/forex_delivery/run_supervised_demo_trade_epic_v1.py --sample-ready --json
python scripts/forex_delivery/run_demo_order_plan_builder_v1.py --sample-ready --json
python scripts/forex_delivery/run_post_trade_evidence_capture_v1.py --sample-profit --json
git diff --check
git status --short --branch
```

## Manual Finalization

No broad add-dot staging is allowed. Stage exact files only.

If a feature branch is needed, run:

```powershell
git checkout -b feature/forex-supervised-demo-trade-execution-stack-v1
```

Stage exact files:

```powershell
git add automation/forex_engine/broker_read_only_snapshot_contract_v1.py
git add automation/forex_engine/demo_account_readiness_gate_v1.py
git add automation/forex_engine/demo_trade_risk_gate_v1.py
git add automation/forex_engine/demo_position_sizer_v1.py
git add automation/forex_engine/demo_order_plan_builder_v1.py
git add automation/forex_engine/demo_operator_execution_ticket_v1.py
git add automation/forex_engine/post_trade_evidence_capture_v1.py
git add automation/forex_engine/demo_trade_feedback_router_v1.py
git add automation/forex_engine/supervised_demo_trade_epic_v1.py
git add scripts/forex_delivery/run_supervised_demo_trade_epic_v1.py
git add scripts/forex_delivery/run_demo_order_plan_builder_v1.py
git add scripts/forex_delivery/run_post_trade_evidence_capture_v1.py
git add tests/forex_engine/test_broker_read_only_snapshot_contract_v1.py
git add tests/forex_engine/test_demo_account_readiness_gate_v1.py
git add tests/forex_engine/test_demo_trade_risk_gate_v1.py
git add tests/forex_engine/test_demo_position_sizer_v1.py
git add tests/forex_engine/test_demo_order_plan_builder_v1.py
git add tests/forex_engine/test_demo_operator_execution_ticket_v1.py
git add tests/forex_engine/test_post_trade_evidence_capture_v1.py
git add tests/forex_engine/test_demo_trade_feedback_router_v1.py
git add tests/forex_engine/test_supervised_demo_trade_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_V1.md
git add Reports/forex_delivery/AIOS_FOREX_BROKER_READ_ONLY_SNAPSHOT_CONTRACT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_DEMO_ORDER_PLAN_BUILDER_V1.md
git add Reports/forex_delivery/AIOS_FOREX_POST_TRADE_EVIDENCE_CAPTURE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_MANUAL_FINALIZATION_V1.md
```

Review cached diff, commit, push, PR, checks, merge, and sync only with Anthony approval:

```powershell
git diff --cached
git commit -m "Add forex supervised demo trade execution stack"
git push -u origin feature/forex-supervised-demo-trade-execution-stack-v1
gh pr create --title "Add forex supervised demo trade execution stack" --body "Build-only local supervised demo execution stack V1. No trade placed. Broker action remains false." --base main --head feature/forex-supervised-demo-trade-execution-stack-v1 --draft
gh pr checks --watch
gh pr merge --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Stop Conditions

Stop if validation fails, cached diff includes unrelated files, any file outside the exact staged list appears, or any command requests credentials, broker access, live trading, real money, compounding, bank movement, destructive cleanup, or direct push to `main`.
