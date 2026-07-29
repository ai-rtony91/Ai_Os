CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1
AI_OS BOOTSTRAP REQUIRED: YES

## Identity

- Identity marker: AI_OS governed Packet 3 APPLY
- Supervisor identity: Anthony, Human Owner
- Mission ID / Name: AIOS-FOREX-100 / Finish AIOS Forex into evidence-backed profit stages
- Program ID / Name: AIOS-FOREX-DELIVERY / Governed Forex Delivery
- Epic ID / Name: AIOS-FOREX-EVIDENCE / Paper and Statistical Evidence
- Bucket ID / Name: AIOS-FOREX-PACKET-QUEUE-V2 / 75-to-100 packet queue
- Packet ID / Name: AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1 / Paper & Statistical Evidence Accumulation
- Mode: APPLY
- Zone: Codex East
- Worker identity: EAST_OCC_03
- Lane: forex paper statistical evidence
- Worktree: `/workspace/Ai_Os`
- Branch: `work` (observed during preflight)
- Approval authority: Anthony
- Validator chain: Python compile, targeted pytest, scoped diff check, cached diff review
- Stop point: commit and PR creation; no merge, Packet 4, broker access, demo order, or live order

## Allowed paths

- `automation/forex_engine/paper_statistical_evidence_accumulator_v1.py`
- `tests/forex_engine/test_paper_statistical_evidence_accumulator_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md`
- `Reports/forex_delivery/AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1_REPORT.md`

## Forbidden paths and actions

- `AGENTS.md`, `RISK_POLICY.md`, secrets, credentials, broker and live-trading configuration
- Network calls, broker/API calls, order placement, demo/live execution, deployment, merge, and Packet 4 creation

## Mission

Implement a deterministic, paper-only accumulator that requires repeated after-cost profitability, sufficient trades, bounded drawdown, and walk-forward/out-of-sample depth before a candidate can be selected for Human Owner review. Selection must never authorize execution.

## Preflight

Run `pwd`, `git status --short --branch`, `git branch --show-current`, and `git remote -v`. Stop on overlapping dirty work or a branch mismatch.

## Validators

- `python -m py_compile automation/forex_engine/paper_statistical_evidence_accumulator_v1.py`
- `python -m pytest tests/forex_engine/test_paper_statistical_evidence_accumulator_v1.py -q`
- `git diff --check -- automation/forex_engine/paper_statistical_evidence_accumulator_v1.py tests/forex_engine/test_paper_statistical_evidence_accumulator_v1.py Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md Reports/forex_delivery/AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1_REPORT.md`

## Commit and PR

Stage only the four allowed files. Review `git diff --cached`. Commit message: `feat(forex): accumulate paper statistical evidence`. Create a PR titled `feat(forex): accumulate paper statistical evidence` and stop without merging.

## Final report

Use the AI_OS Owner View followed by successful technical details covering files, validation, remaining dirty files, commit, PR, and safe next action.
