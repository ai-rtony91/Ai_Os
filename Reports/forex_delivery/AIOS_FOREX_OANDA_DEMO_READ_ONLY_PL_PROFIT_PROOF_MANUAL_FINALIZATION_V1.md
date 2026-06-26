# AIOS Forex OANDA Demo Read-Only P/L Profit Proof Manual Finalization V1

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/oanda_demo_read_only_pl_result_intake_v1.py automation/forex_engine/oanda_demo_pl_result_quality_gate_v1.py automation/forex_engine/oanda_demo_profit_proof_ledger_bridge_v1.py automation/forex_engine/oanda_demo_read_only_pl_profit_proof_epic_v1.py scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py tests/forex_engine/test_oanda_demo_read_only_pl_result_intake_v1.py tests/forex_engine/test_oanda_demo_pl_result_quality_gate_v1.py tests/forex_engine/test_oanda_demo_profit_proof_ledger_bridge_v1.py tests/forex_engine/test_oanda_demo_read_only_pl_profit_proof_epic_v1.py
python -m pytest tests/forex_engine/test_oanda_demo_read_only_pl_result_intake_v1.py tests/forex_engine/test_oanda_demo_pl_result_quality_gate_v1.py tests/forex_engine/test_oanda_demo_profit_proof_ledger_bridge_v1.py tests/forex_engine/test_oanda_demo_read_only_pl_profit_proof_epic_v1.py -q
python scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py --sample-profit
python scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py --sample-loss
python scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py --sample-breakeven
python scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py --sample-incomplete
python scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py --sample-unsafe
python scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py --sample-profit --json
python scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py --sample-loss --json
python scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py --sample-profit --json
python scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py --sample-profit --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

Do not use `git add .`.

```powershell
git checkout -b feature/forex-oanda-demo-read-only-pl-profit-proof-bridge-v1 if needed
git add automation/forex_engine/oanda_demo_read_only_pl_result_intake_v1.py
git add automation/forex_engine/oanda_demo_pl_result_quality_gate_v1.py
git add automation/forex_engine/oanda_demo_profit_proof_ledger_bridge_v1.py
git add automation/forex_engine/oanda_demo_read_only_pl_profit_proof_epic_v1.py
git add scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py
git add scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py
git add scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py
git add tests/forex_engine/test_oanda_demo_read_only_pl_result_intake_v1.py
git add tests/forex_engine/test_oanda_demo_pl_result_quality_gate_v1.py
git add tests/forex_engine/test_oanda_demo_profit_proof_ledger_bridge_v1.py
git add tests/forex_engine/test_oanda_demo_read_only_pl_profit_proof_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_RESULT_INTAKE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_PL_RESULT_QUALITY_GATE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex OANDA demo read-only PL profit proof bridge"
git push -u origin feature/forex-oanda-demo-read-only-pl-profit-proof-bridge-v1
gh pr create --title "Add forex OANDA demo read-only PL profit proof bridge" --body "Build-only OANDA demo read-only P/L result intake and profit proof ledger bridge. No broker call. No trade placed. Broker action remains false." --base main --head feature/forex-oanda-demo-read-only-pl-profit-proof-bridge-v1 --draft
gh pr checks --watch
gh pr ready <PR_NUMBER>
gh pr merge <PR_NUMBER> --squash --delete-branch
git switch main
git pull --ff-only
git status --short --branch
git log -1 --oneline
```

## Safety Notes

No trade placed by this packet. No broker call was made by this packet. All protected permission flags remain false.
