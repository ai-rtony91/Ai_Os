# AIOS Forex 75-to-100 Overnight Packet Queue V2

## Packet 1

- Packet ID: `AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_LANDING_V1`
- Purpose: preserve and package landed Flow 2 evidence countdown module as the next execution package.
- Why first: this keeps existing validated Flow 2 work unmodified and owner-reviewable before higher-risk governance changes.
- Allowed Paths:
  - `automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py`
  - `tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py`
  - `Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md`
- Validators:
  - `python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py`
  - `python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q`
  - `git diff --check -- automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md`
  - `git status --short --branch`
- Stop Point: local validation + report package handoff only, no commit/push.

## Packet 2

- Packet ID: `AIOS_FOREX_LIVE_CAPABILITY_GOVERNANCE_UNBLOCK_V2`
- Purpose: rewrite `RISK_POLICY.md`, `README.md`, `WHITEPAPER.md`, and `docs/architecture/AI_OS_WHITEPAPER.md` to replace the single-exception-only model with a governed live capability gate.
- Why second: governance edits must follow a preserved Flow 2 landing state and remain policy-only.
- Allowed Paths:
  - `RISK_POLICY.md`
  - `README.md`
  - `WHITEPAPER.md`
  - `docs/architecture/AI_OS_WHITEPAPER.md`
  - `Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md`
- Validators:
  - Python text validation script from governance packet.
  - `git diff --check -- RISK_POLICY.md README.md WHITEPAPER.md docs/architecture/AI_OS_WHITEPAPER.md Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md`
  - `git status --short --branch`
- Stop Point: local APPLY + validation + no commit/push.

## Packet 3

- Packet ID: `AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1`
- Purpose: implement/repair the next-candidate profitability gate and evidence sufficiency logic, with no live execution path.
- Why third: once governance gate is defined, execution can progress to deterministic candidate acceleration.
- Allowed Paths:
  - `automation/forex_engine/`
  - `tests/forex_engine/`
  - `Reports/forex_delivery/`
- Validators:
  - module-level compile and targeted tests for selected evidence/candidate selectors.
  - repository scoped diff check on changed files.
  - `git status --short --branch`
- Stop Point: local validation package handoff, no commit/push.
