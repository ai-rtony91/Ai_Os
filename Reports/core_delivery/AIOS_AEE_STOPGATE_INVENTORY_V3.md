# AIOS AEE Stopgate Inventory V3

This inventory describes the anti-stop stopgates that keep the same lane running through long campaigns without unnecessary exits.

## Stopgate Families

### 1. State alignment stopgates
Codes: STATE-001, STATE-002, STATE-003, STATE-004, STATE-005

### 2. Branch stopgates
Codes: BRANCH-001, BRANCH-002

### 3. Dirty worktree stopgates
Codes: STATE-001, STATE-004, STATE-002

### 4. Staged file stopgates
Codes: STATE-003, PROTECTED-001

### 5. Forbidden path stopgates
Codes: STATE-004, SAFETY-001, SAFETY-002, SAFETY-003, SAFETY-004

### 6. Protected action stopgates
Codes: PROTECTED-001, PROTECTED-002, PROTECTED-003

### 7. Sandbox/process-launch stopgates
Codes: SANDBOX-001, SANDBOX-002, SANDBOX-003

### 8. Validator stopgates
Codes: VALIDATOR-001, VALIDATOR-002, VALIDATOR-003

### 9. Test failure stopgates
Codes: VALIDATOR-002, VALIDATOR-003

### 10. Report/checkpoint stopgates
Codes: REPORT-001, REPORT-002, REPORT-003

### 11. CI stopgates
Codes: CI-001, CI-002

### 12. Safety authority stopgates
Codes: SAFETY-001, SAFETY-002, SAFETY-003, SAFETY-004

### 13. Credential/secrets stopgates
Codes: CI-001, SAFETY-002

### 14. Trading/money movement stopgates
Codes: SAFETY-003, SAFETY-004

### 15. Broad scan stopgates
Codes: SANDBOX-003

### 16. Context compaction stopgates
Codes: CONTEXT-001

### 17. User accidental prompt injection stopgates
Codes: PROMPT-001

### 18. Owner handoff readiness stopgates
Codes: HANDOFF-001, HANDOFF-002

## Required major stopgate examples

| code | name | severity | classification | continue condition | true stop condition | owner handoff required | example | anti-stop instruction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| STATE-001 | wrong branch unrelated dirty hard stop | high | HARD_STOP | branch equals lane/aios-aee-governance-validator-v1 | dirty on unrelated branch | no | branch: main + dirty: unrelated | continue only with current carryover lane |
| STATE-002 | approved carryover dirty continuation | info | APPROVED_CARRYOVER_CONTINUATION | carryover file set in allowed paths | expected artifacts missing from lane | no | dirty carryover files | classify as continuation, do not stop |
| STATE-003 | staged files present hard stop | high | HARD_STOP | no staged files | staged files exist | yes | staged validator files | stop and hand back owner |
| STATE-004 | forbidden path dirty hard stop | high | HARD_STOP | forbidden list empty | forbidden file dirty | yes | .env dirty | stop before any edit |
| STATE-005 | clean-main expectation false positive | high | WRONG_PACKET_FOR_CLEAN_MAIN | branch lane/... with carryover | main branch while this packet active | no | branch main | return wrong-packet not destructive action |
| BRANCH-001 | target branch conflict | high | HARD_STOP | branch matches expected lane | branch differs and no continuation state | no | target branch feature-x | keep lane fixed |
| BRANCH-002 | dirty branch switch attempt forbidden | high | HARD_STOP | no branch switch action | branch switch attempt with dirty approved work | yes | ask to switch main | block switch and preserve dirty |
| PROTECTED-001 | git add attempted by Codex | high | HARD_STOP | no protected action | `git add` attempt outside handoff | yes | git add -- | halt and route owner publish block |
| PROTECTED-002 | PR create attempted by Codex | high | HARD_STOP | no PR create | `gh pr create` attempt outside owner block | yes | gh pr create | route owner block1 only |
| PROTECTED-003 | merge attempted by Codex | high | HARD_STOP | no merge commands | merge attempt outside block2 | yes | gh pr merge | route owner block2 only |
| SANDBOX-001 | 1312 read-only command | medium | SANDBOX_LIMITATION | command is read-only and retry once | third-party launch blocks retries | no | Get-Content blocked by 1312 | retry once and continue |
| SANDBOX-002 | 1312 strict CLI | medium | DEFERRED_OWNER_VALIDATION | targeted tests pass | all remaining validation blocked | no | strict CLI blocked | continue local work and mark deferred |
| SANDBOX-003 | broad scan blocked | low | MINOR_SCAN_BLOCKED_RECORUABLE | explicit paths available | broad scan required | no | rg --files failed | switch to explicit paths |
| VALIDATOR-001 | targeted tests pass strict CLI blocked | medium | DEFERRED_OWNER_VALIDATION | targeted tests passed and 1312 | strict CLI blocks all checks | no | pytest pass, strict blocked | continue with report/checkpoint |
| VALIDATOR-002 | repairable test failures | medium | RECOVERABLE_LOCAL | failure is in allowed scope | no deterministic repair | no | missing fixture record | create fixture and rerun |
| VALIDATOR-003 | failing test requiring forbidden path | high | HARD_STOP | forbidden path alternative | required edit is forbidden path | yes | secret fixture needed | route hard stop |
| REPORT-001 | report exists but hardening remains | low | RECOVERABLE_LOCAL | pending_work in report exists | report final while work remains | no | report generated | continue hardening and re-run report |
| REPORT-002 | checkpoint exists report pending | low | RECOVERABLE_LOCAL | report missing / not yet created | report required for completion | no | checkpoint only | create report and continue |
| REPORT-003 | report/checkpoint contradiction | medium | EVIDENCE_GAP | files explicit alignment | contradictory completion markers | no | complete vs pending mismatch | repair files and continue |
| CI-001 | secret scanner risk | high | HARD_STOP | no ci-sensitive assignment lines | forbidden assignment found | no | secret = "demo" | rename marker in neutral names |
| CI-002 | placeholder false positive | low | FALSE_POSITIVE_REPAIR | placeholder only in fixture/test | placeholder in executable context | no | @filename in fixture comments | classify minor repair |
| SAFETY-001 | broker/API boundary | critical | HARD_STOP | no broker/API commands | boundary command present | yes | trading API call | stop and preserve control |
| SAFETY-002 | credential boundary | critical | HARD_STOP | no credential path | credential file/path touched | yes | .env dirty | remove credential scope |
| SAFETY-003 | trading execution boundary | critical | HARD_STOP | no execution logic touched | execution path observed | yes | scripts/forex_delivery | stop and request rebalance |
| SAFETY-004 | money movement boundary | critical | HARD_STOP | no payment/money movement touched | movement command present | yes | funds action | stop by policy |
| CONTEXT-001 | context compaction stopgate | low | RECOVERABLE_LOCAL | targeted context retained | context corruption | no | too much stale context | keep lane-local scope |
| PROMPT-001 | accidental "Explain this codebase" interruption | low | PROMPT_INTERRUPTION_IGNORE | prompt phrase matched in operator channel | explicit explanation-only request in active packet | no | Explain this codebase | ignore and continue current lane |
| HANDOFF-001 | owner handoff ready but local work remains | low | RECOVERABLE_LOCAL | local work remains | protected action ready while work remains | no | report absent pending | repair work and continue |
| HANDOFF-002 | owner handoff ready with local work complete | low | OWNER_HANDOFF_READY | no pending local work | all artifacts complete | yes | all required files complete | move to owner handoff block |

## Continue policy

- Clean-main preflight bypass applies only when branch and carryover artifacts match this packet.
- Staged files are treated as immediate stop for local-only execution.
- If explicit branch mismatch and dirty is not approved carryover, stop.
- After one 1312 event, retry read-only command once; never loop.
- Broad scans are downgrade-only failures; move to explicit file inventory.
- If protected publish actions appear while local work remains, status remains `RECOVERABLE_LOCAL`.
- If local work complete and protected handoff is ready, status becomes `OWNER_HANDOFF_READY`.
