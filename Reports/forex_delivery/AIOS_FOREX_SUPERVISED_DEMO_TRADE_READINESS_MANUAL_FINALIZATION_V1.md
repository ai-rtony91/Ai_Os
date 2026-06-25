# AIOS Forex Supervised Demo Trade Readiness Manual Finalization V1

No broker call was made. No trade placed.

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/demo_trade_candidate_context_v1.py automation/forex_engine/demo_trade_readiness_bridge_v1.py automation/forex_engine/supervised_demo_trade_review_bundle_v1.py automation/forex_engine/supervised_demo_trade_readiness_epic_v1.py scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py scripts/forex_delivery/run_supervised_demo_trade_review_bundle_v1.py scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py tests/forex_engine/test_demo_trade_candidate_context_v1.py tests/forex_engine/test_demo_trade_readiness_bridge_v1.py tests/forex_engine/test_supervised_demo_trade_review_bundle_v1.py tests/forex_engine/test_supervised_demo_trade_readiness_epic_v1.py
python -m pytest tests/forex_engine/test_demo_trade_candidate_context_v1.py tests/forex_engine/test_demo_trade_readiness_bridge_v1.py tests/forex_engine/test_supervised_demo_trade_review_bundle_v1.py tests/forex_engine/test_supervised_demo_trade_readiness_epic_v1.py -q
python scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py --sample-ready
python scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py --sample-blocked
python scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py --sample-ready --json
python scripts/forex_delivery/run_supervised_demo_trade_review_bundle_v1.py --sample-ready --json
python scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py --sample-ready --json
python scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py --sample-ready --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

Run only after Anthony explicitly approves each protected action.

No git add dot. Stage only the exact files below.

```powershell
git checkout -b feature/forex-supervised-demo-trade-readiness-bridge-v1 if needed
git add automation/forex_engine/demo_trade_candidate_context_v1.py
git add automation/forex_engine/demo_trade_readiness_bridge_v1.py
git add automation/forex_engine/supervised_demo_trade_review_bundle_v1.py
git add automation/forex_engine/supervised_demo_trade_readiness_epic_v1.py
git add scripts/forex_delivery/run_demo_trade_readiness_bridge_v1.py
git add scripts/forex_delivery/run_supervised_demo_trade_review_bundle_v1.py
git add scripts/forex_delivery/run_supervised_demo_trade_readiness_epic_v1.py
git add tests/forex_engine/test_demo_trade_candidate_context_v1.py
git add tests/forex_engine/test_demo_trade_readiness_bridge_v1.py
git add tests/forex_engine/test_supervised_demo_trade_review_bundle_v1.py
git add tests/forex_engine/test_supervised_demo_trade_readiness_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_DEMO_TRADE_READINESS_BRIDGE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex supervised demo trade readiness bridge"
git push -u origin feature/forex-supervised-demo-trade-readiness-bridge-v1
gh pr create --title "Add forex supervised demo trade readiness bridge" --body "Build-only local supervised demo trade readiness bridge V1. No broker call. No trade placed. Broker action remains false." --base main --head feature/forex-supervised-demo-trade-readiness-bridge-v1 --draft
gh pr checks --watch
gh pr ready <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Stop Conditions

Stop if validation fails, static safety fails, any unexpected file appears in the staged diff, credentials are requested, account identifiers are requested, broker action is requested, or any trade execution is requested.
