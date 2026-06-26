# AIOS Forex OANDA Demo Repeated Expectancy Sample Manual Finalization V1

## Manual Validation Commands

```powershell
python -m py_compile automation/forex_engine/oanda_demo_expectancy_sample_intake_v1.py automation/forex_engine/oanda_demo_repeated_expectancy_accumulator_v1.py automation/forex_engine/oanda_demo_expectancy_sufficiency_gate_v1.py automation/forex_engine/oanda_demo_repeated_expectancy_sample_epic_v1.py scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py tests/forex_engine/test_oanda_demo_expectancy_sample_intake_v1.py tests/forex_engine/test_oanda_demo_repeated_expectancy_accumulator_v1.py tests/forex_engine/test_oanda_demo_expectancy_sufficiency_gate_v1.py tests/forex_engine/test_oanda_demo_repeated_expectancy_sample_epic_v1.py
python -m pytest tests/forex_engine/test_oanda_demo_expectancy_sample_intake_v1.py tests/forex_engine/test_oanda_demo_repeated_expectancy_accumulator_v1.py tests/forex_engine/test_oanda_demo_expectancy_sufficiency_gate_v1.py tests/forex_engine/test_oanda_demo_repeated_expectancy_sample_epic_v1.py -q
python scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py --sample-strong
python scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py --sample-losing
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py --sample-strong --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py --sample-losing --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-strong --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-weak --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-insufficient --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-losing --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-unsafe --json
python scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py --sample-strong --markdown
git diff --check
git status --short --branch
```

## Manual Finalization Commands

Do not use `git add .`.

```powershell
git checkout -b feature/forex-oanda-demo-repeated-expectancy-sample-v1 if needed
git add automation/forex_engine/oanda_demo_expectancy_sample_intake_v1.py
git add automation/forex_engine/oanda_demo_repeated_expectancy_accumulator_v1.py
git add automation/forex_engine/oanda_demo_expectancy_sufficiency_gate_v1.py
git add automation/forex_engine/oanda_demo_repeated_expectancy_sample_epic_v1.py
git add scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py
git add scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py
git add scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py
git add tests/forex_engine/test_oanda_demo_expectancy_sample_intake_v1.py
git add tests/forex_engine/test_oanda_demo_repeated_expectancy_accumulator_v1.py
git add tests/forex_engine/test_oanda_demo_expectancy_sufficiency_gate_v1.py
git add tests/forex_engine/test_oanda_demo_repeated_expectancy_sample_epic_v1.py
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SUFFICIENCY_GATE_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md
git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_MANUAL_FINALIZATION_V1.md
git diff --cached
git commit -m "Add forex OANDA demo repeated expectancy sample accumulator"
git push -u origin feature/forex-oanda-demo-repeated-expectancy-sample-v1
gh pr create --title "Add forex OANDA demo repeated expectancy sample accumulator" --body "Build-only OANDA demo repeated expectancy sample accumulator. No broker call. No trade placed. Broker action remains false." --base main --head feature/forex-oanda-demo-repeated-expectancy-sample-v1 --draft
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
