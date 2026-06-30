# AIOS Forex Capital Operating Program V2 Report

## Packet status
LOCAL_APPLY completed for Packet `AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2`.

## Files inspected
- `automation/forex_engine/capital_operating_program_v2.py`
- `tests/forex_engine/test_capital_operating_program_v2.py`
- `docs/trading_lab/FOREX_CAPITAL_OPERATING_PROGRAM_V2.md`

## Files created
- `automation/forex_engine/capital_operating_program_v2.py`
- `tests/forex_engine/test_capital_operating_program_v2.py`
- `docs/trading_lab/FOREX_CAPITAL_OPERATING_PROGRAM_V2.md`
- `Reports/forex_delivery/AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2_REPORT.md`

## Files changed
- `automation/forex_engine/capital_operating_program_v2.py`
- `tests/forex_engine/test_capital_operating_program_v2.py`

## Validators run
- `python -m py_compile automation/forex_engine/capital_operating_program_v2.py`
- `python -m pytest tests/forex_engine/test_capital_operating_program_v2.py -q`
- `python -m pytest tests/forex_engine/test_oanda_demo_supervised_order_execution_v1.py -q`
- `rg` phrase scan for unsafe terms
- `git diff --check -- automation/forex_engine/capital_operating_program_v2.py tests/forex_engine/test_capital_operating_program_v2.py docs/trading_lab/FOREX_CAPITAL_OPERATING_PROGRAM_V2.md Reports/forex_delivery/AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2_REPORT.md`
- `git status --short --branch`

## Validators passed
1. `python -m py_compile automation/forex_engine/capital_operating_program_v2.py`
   - Passed
2. `python -m pytest tests/forex_engine/test_capital_operating_program_v2.py -q`
   - Passed (36 passed)
3. `python -m pytest tests/forex_engine/test_oanda_demo_supervised_order_execution_v1.py -q`
   - Passed (24 passed)
4. Forbidden phrase scan for packet files
   - Passed (no matches)
5. `git diff --check -- automation/forex_engine/capital_operating_program_v2.py tests/forex_engine/test_capital_operating_program_v2.py docs/trading_lab/FOREX_CAPITAL_OPERATING_PROGRAM_V2.md Reports/forex_delivery/AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2_REPORT.md`
   - Passed (no whitespace/errors)
6. `git status --short --branch`
   - Completed

## Validators failed
None.

## Safety boundary
- read-only output
- no money movement
- no bank/broker API access
- no credential storage/read

## Remaining blockers
None from test run.

## git status
## main...origin/main
Untracked:
- automation/forex_engine/capital_operating_program_v2.py
- tests/forex_engine/test_capital_operating_program_v2.py
- docs/trading_lab/FOREX_CAPITAL_OPERATING_PROGRAM_V2.md
- Reports/forex_delivery/AIOS_FOREX_CAPITAL_OPERATING_PROGRAM_V2_REPORT.md

## commit status
No commit performed.

## push status
No push performed.

## next safe action
- Validate and fix failing tests only if any; no commit/push unless explicitly requested.
