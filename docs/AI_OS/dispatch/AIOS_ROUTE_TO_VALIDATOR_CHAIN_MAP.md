# AI_OS Route to Validator Chain Map

Each dispatch route must attach a validator chain before any later execution packet can proceed.

| Route | Validator chain |
| --- | --- |
| `BLOCKED` | git status check; blocker report; stop point verifier |
| `READ_ONLY_RECON` | git status check; branch check; worktree check; no-mutation verifier |
| `DOCS_ONLY` | git status check; allowed-path scope check; schema/JSON parse check; forbidden-path dirty check |
| `FIXTURE_ONLY` | git status check; fixture schema check; JSON parse check; no-network verifier |
| `DRY_RUN_IMPLEMENTATION` | git status check; branch/worktree check; allowed-path scope check; forbidden-path dirty check; clean-state verifier |
| `APPLY_HUMAN_APPROVED` | human approval check; allowed-path scope check; validator chain presence; clean-state verifier |
| `PR_VALIDATION` | PR file-scope check; schema/JSON parse check; CI check; forbidden-content scan |
| `MERGE_HUMAN_APPROVED` | human approval check; PR status check; merge-state check; CI check; final clean-state verifier |
| `NIGHT_SUPERVISOR_PREVIEW` | Night Supervisor lock/cycle check; no runtime start check; no telemetry/control/approval inbox write check |
| `NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL` | human approval check; runtime context precheck; lock/cycle check; stop-point check |
| `OPENAI_SMOKE_TEST_PENDING_APPROVAL` | human approval check; no key printing check; timeout check; redaction check; no repo mutation check |
| `RESPONSES_PACKET_DRAFT_PENDING_APPROVAL` | structured output check; guardrail truth eval; DRAFT_ONLY check |
| `PROMPTFOO_RED_TEAM_PENDING_APPROVAL` | human approval check; no secrets check; AI_OS-owned target check; no third-party probing check |
| `COMPUTER_USE_PENDING_APPROVAL` | human approval check; click/type/submit/delete risk check; UI action confirmation plan |
| `PI_CAR_VOICE_PREVIEW` | preview-only check; no GPIO/motor command check; human approval check |
| `PI_CAR_MOTOR_BLOCKED` | Pi GPIO/motor block check; stop point verifier |
| `LIVE_TRADING_BLOCKED` | broker/OANDA/live-trading block check; profitability-priority verifier |

