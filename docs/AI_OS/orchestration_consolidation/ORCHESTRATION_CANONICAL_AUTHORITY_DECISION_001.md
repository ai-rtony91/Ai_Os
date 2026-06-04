# Orchestration Canonical Authority Decision 001

## Status

`ACTIVE_DECISION`

This decision marks canonical orchestration authorities for documentation alignment only. It does not move, delete, rename, archive, or modify runtime automation files.

## Canonical High-Level Spine

```text
goal intake
-> packet draft
-> dispatcher route scoring
-> worker assignment
-> validator chain
-> approval gate
-> execution worker
-> clean-state verifier
-> commit package
-> PR lane
-> human merge
-> trace/red-team/improvement loop
```

## Canonical Authority Decisions

| Authority | Canonical decision | Boundary |
|---|---|---|
| Goal intake authority | Human owner and AI_OS Manager Control own goal acceptance. | Casual text, stale transcript fragments, screenshots, and un-tokenized notes are not executable work orders. |
| Packet draft authority | OpenAI/ChatGPT may draft packets; Codex and AI_OS governance validate packet completeness. | Drafts are inert until dispatcher, validators, and human approval accept them. |
| Packet validation authority | `AGENTS.md`, identity/lane governance, and workflow standards define packet completeness. | Missing token, lane, paths, approval authority, validator chain, or stop point blocks execution. |
| Dispatcher authority | Dispatch route scoring and blocker classes route packets. | Dispatcher cannot grant runtime, repo mutation, commit, push, merge, broker, OANDA, live trading, or Pi GPIO/motor authority. |
| Worker assignment authority | Packet-scoped worker identity and worker registry determine worker ownership. | One packet maps to one bounded worker lane unless explicit reassignment is approved. |
| Validator chain authority | Validator standards and validator-chain runners produce evidence. | Validator PASS is evidence only; it is not APPLY, commit, push, merge, runtime, or trading approval. |
| Approval gate authority | Human Owner approval plus exact-scope approval gates control protected actions. | Approval is current-session, action-specific, and does not transfer between actions. |
| Execution worker authority | Codex or assigned worker executes only the approved lane and allowed paths. | Execution workers must stop at packet stop points and may not widen scope. |
| Clean-state verifier authority | Git/worktree clean-state checks and forbidden-path checks gate start and closeout. | Clean state does not approve protected actions by itself. |
| Commit package authority | Commit package docs and protected-action gates define exact staged scope. | No `git add .`; only approved files may be staged. |
| PR lane authority | Protected main PR lane is canonical for protected main changes. | Direct push to `main` remains blocked unless separate emergency approval exists. |
| Human merge authority | Human Owner is final merge authority. | CI, validator PASS, PR readiness, dashboard state, or supervisor output cannot merge by itself. |
| Trace/red-team/improvement authority | Red-team findings, trace grading, and improvement loop feed future fixes. | Findings become future packets; they do not self-apply. |
| Night Supervisor preview authority | Night Supervisor preview docs and dispatch preview route own report-only planning. | Preview cannot start runtime, write telemetry/control/approval inbox state, or resume Paper SOS. |
| Night Supervisor runtime authority | Runtime authority remains blocked until controlled-run gates pass. | No runtime start without a separate human-approved runtime packet. |
| OpenAI CLI authority | OpenAI CLI is planner/generator only. | It cannot execute, mutate repo, start runtime, bypass dispatcher/validators/human approval, or print/use keys outside approved packets. |
| Skills authority | Skills are reviewed developer-level bundles only. | Unreviewed Skill execution remains blocked. |
| Computer-use authority | Computer-use is future isolated human-in-loop capability only. | No unsafe click, submit, delete, trading, broker, Pi, or irreversible action without approval. |
| Pi car voice authority | Pi car voice can listen, speak, explain, and propose actions. | It cannot move motors, GPIO, wheels, servos, camera, or hardware without future gates. |
| Trading Lab authority | Trading Lab remains paper-only. | Broker/OANDA/live trading stays blocked until trust gates prove safety. |

## Safety Rules

- No file is deleted or moved until references are mapped, replacement authority is named, a validator confirms no active runtime dependency, and the Human Owner approves APPLY.
- Non-canonical files remain untouched until later APPLY packets explicitly mark, update, move, archive, or delete them.
- Night Supervisor remains preview/report-only until controlled-run gates pass.
- Trading Lab remains paper-only until trust gates pass.
- OpenAI CLI may draft packets but cannot execute, mutate repo, start runtime, or bypass dispatcher, validators, and human approval.

