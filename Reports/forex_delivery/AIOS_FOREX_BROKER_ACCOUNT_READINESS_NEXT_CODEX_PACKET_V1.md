CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

## CONTRACT
AIOS_FOREX_OWNER_APPROVAL_GATE_CONTINUATION_V1

## MISSION
Run the next repo-safe stage after broker/account readiness evidence completion:
`OWNER_APPROVAL_GATE`.

## PRECHECK
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current

## REQUIRED
- branch is main
- no pending untracked files outside report artifacts
- no broker API / credentials usage in this packet
- no order execution

## OBJECTIVE
Use the newly created readiness evidence and owner decision artifacts to complete `OWNER_APPROVAL_GATE` and unblock operator routing for the next safe action.

### Target gate
- OWNER_APPROVAL_GATE

### Required files
- Reports/forex_delivery/AIOS_FOREX_BROKER_ACCOUNT_READINESS_REVIEW_V1.md
- Reports/forex_delivery/AIOS_FOREX_BROKER_ACCOUNT_CAPABILITY_CHECKLIST_V1.md
- Reports/forex_delivery/AIOS_FOREX_BROKER_GATE_OWNER_DECISION_CARD_V1.md

## STOP
STOP when OWNER_APPROVAL_GATE evidence is captured and the promotion state advances.
