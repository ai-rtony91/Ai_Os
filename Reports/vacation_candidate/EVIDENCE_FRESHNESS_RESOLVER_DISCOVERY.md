# Evidence Freshness Resolver Discovery

Packet ID: EVIDENCE_FRESHNESS_RESOLVER_DISCOVERY_001
Lane: EVIDENCE_FRESHNESS_RESOLVER
Mode: DRY_RUN
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os
Created by: Codex CLI Worker

## Executive Finding

AI_OS already has partial freshness signals, but no single resolver that lets Morning Digest, Night Supervisor, Dashboard, Relay, SOS, and telemetry classify the same evidence the same way.

The resolver should not become a new authority source. It should be a read-only classification layer that consumes existing evidence records, applies one vocabulary, and emits freshness classification for downstream display and interruption decisions.

Canonical ownership should remain with the current orchestration spine and existing source owners:

- Work packet state: `automation/orchestration/work_packets/`
- Approval state: `automation/orchestration/approval_inbox/`
- Worker state: `automation/orchestration/workers/`
- Validator state: `automation/orchestration/validators/`
- Commit package state: `automation/orchestration/commit_packages/`
- Runtime projection: `telemetry/runtime/` and `telemetry/night_supervisor/`
- Reports and bridge audits: evidence records only, not active authority

The resolver's job is to answer: "Can this evidence still be trusted for this decision?"

## Source Material Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/vacation_candidate/VACATION_KILLER_BLOCKERS.md`
- `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_PROOF.md`
- `Reports/bridge_audit/CODEX_RESULT_TO_EVIDENCE_ADAPTER_MAPPING.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`
- `automation/orchestration/reports/New-AiOsMorningBrief.ps1`
- `automation/orchestration/night_supervisor/README.md`
- `automation/orchestration/queue_health_supervisor.v1.example.json`
- `telemetry/runtime/runtime_state.json`
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `Relay/LEGACY_CLI_RELAY_README.md`
- `relay/reports/AUDIT_AUTONOMY_GAPS_20260531.md`
- Dashboard, telemetry, Relay, digest, notification, queue, approval, and runtime references by read-only search

## Existing Evidence Sources

| Source | Current role | Freshness value today | Authority status |
|---|---|---|---|
| `automation/orchestration/work_packets/` | Canonical packet state path | State files can prove current packet position when read fresh | Canonical owner |
| `automation/orchestration/approval_inbox/` | Canonical approval inbox path | Can prove pending/approved/rejected state when scoped and current | Canonical owner |
| `automation/orchestration/workers/` | Worker assignment and state | Can prove active, stale, or expired workers | Canonical owner |
| `automation/orchestration/validators/` | Validator evidence path | Can prove validator pass/fail/not-run only | Canonical owner |
| `automation/orchestration/commit_packages/` | Commit package evidence | Can prove commit package readiness, not approval | Canonical owner |
| `telemetry/runtime/runtime_state.json` | Runtime visibility projection | Already marks packet evidence stale and runtime freshness fresh | Projection only |
| `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` | Night Supervisor and bridge projection | Has `generated_at`, source paths, statuses, evidence categories | Projection only |
| `telemetry/morning_digest/*_LATEST.*` | Digest and operator-facing latest views | Uses latest pointer names but can contain stale source content | Projection only |
| `relay/` and `Relay/` | Legacy/manual bridge, reports, approvals, SOS files | Contains historical, sample, completed, and waiting artifacts | Legacy fallback |
| `Reports/bridge_audit/` | Adapter and bridge reports | Current as report output, historical for runtime decisions | Evidence only |
| `Reports/vacation_candidate/` | Vacation readiness reports | Current as report output, historical after newer state evidence exists | Evidence only |
| `automation/orchestration/adapters/chatgpt_to_orchestration/` | Preview-only packet evidence adapter | Emits executable=false packet validation evidence | Adapter output |
| `automation/orchestration/adapters/codex_result_to_evidence/` | Preview-only Codex result evidence adapter | Emits parse-time freshness fields | Adapter output |
| `apps/dashboard/` | Dashboard display and mock fixtures | Can display runtime data but includes many mock/reference-only files | Display only |
| `services/telemetry/runtimeVisibility.ts` | Runtime visibility freshness logic | Uses fresh/stale/unknown with configurable age threshold | Projection logic |
| Trading Lab paper artifacts | Paper signal and latency freshness checks | Stale signal checks exist for paper-only trading flow | Domain-specific evidence |

## Existing Freshness Indicators

AI_OS already emits or stores these freshness hints:

- `created_at_utc`, `generated_at`, `generatedAt`, `lastUpdatedAt`, `lastTickAt`, `lastEventAt`
- File `LastWriteTimeUtc` used by `New-AiOsMorningBrief.ps1` when structured timestamps are absent
- `age_hours` and `MaxAgeHours` in Morning Brief freshness checks
- `freshness`, `status`, `packet_state`, `visibility_state`, `stale_after_minutes`
- `display_alert`, `sos_wake_required`, `wake_class`
- `approval_required`, `approval_status`, approval path, approval age, and approval scope fields
- `validator_status`, `validator_results`, `validator_chain`
- `source_paths`, `provenance`, `input_hashes`, `source_party`, and `event_id`
- `git status --short --branch`, branch, worktree, and dirty-state classifications
- Relay categories such as `HISTORICAL_EVIDENCE`, `COMPLETED_RECORD`, `SAMPLE_OR_EXAMPLE`, and `NOISE`

The problem is not absence of freshness data. The problem is inconsistent interpretation.

## Existing Stale-State Problems

1. `telemetry/runtime/runtime_state.json` already reports stale packet evidence while also reporting runtime freshness as fresh. This is technically valid but can confuse displays unless evidence freshness and runtime heartbeat freshness are separated.
2. `telemetry/morning_digest/*_LATEST.*` names imply current state, but source contents can be older than the current branch, current packet, or current runtime cycle.
3. `relay/reports/ALERT_LATEST.md` and historical SOS files can look active unless classified as historical or superseded.
4. `Relay/` and `relay/` both exist in references, creating casing-based duplicate evidence risk on Windows.
5. Relay approval files contain waiting, historical, sample, and completed records in adjacent paths; stale approval evidence can look actionable.
6. Dashboard mock-data fixtures include stale, SOS, approval, runtime, and queue examples that must not be mixed with active state.
7. The Night Supervisor README defines `execution_result` as evidence only, but downstream consumers still need a freshness resolver before treating it as current vacation proof.
8. Codex and ChatGPT adapter outputs include freshness-like parse timestamps, but parse-time freshness does not prove the underlying source remains current.
9. Git branch and dirty worktree evidence expires as soon as the worktree mutates; reports that capture old Git state become historical for repo decisions.
10. Paper Trading Lab has domain-specific stale-signal checks that should remain separate from orchestration evidence freshness.

## Digest Mismatches

Morning Brief already checks:

- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`

It marks missing or empty evidence as `BLOCKED`, evidence older than 18 hours as `WARN`, and current evidence as `PASS`.

Mismatch risks:

- Morning Digest freshness is currently file-level or `generated_at` based, not source-owner based.
- A digest can be freshly generated from stale Relay or telemetry inputs.
- A digest can show `PASS` for file age while still containing historical approvals, sample records, or superseded alerts.
- A digest is a consumer-facing projection, not the owner of queue, approval, validator, worker, or runtime truth.

## Night Supervisor Mismatches

Night Supervisor defines an `execution_result` object with `PASS`, `FAIL`, `BLOCKED`, `NEEDS_APPROVAL`, or `NOOP`. It also says the result is evidence only and never grants APPLY, commit, push, merge, worker launch, scheduler, broker, secret, or live-trading authority.

Mismatch risks:

- A Night Supervisor report can be current for the night cycle but historical for current-day operator decisions.
- `runtime_state_proposal` is intentionally proposed state, not active state.
- Resume records are sandboxed under telemetry until a separate approved promotion.
- Validator `PASS` remains evidence only; freshness cannot convert it into permission.
- Approval classification inside Night Supervisor is not approval execution.

## Dashboard Freshness Risks

Dashboard and service references show both runtime visibility logic and extensive mock data:

- `apps/dashboard/server.js` can point to `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`.
- `apps/dashboard/src/runtimeVisibilityClient.js` has a mock-data source label.
- `apps/dashboard/src/runtimeVisibilityAdapter.js` warns not to treat stale telemetry as proof of no night activity.
- `services/telemetry/runtimeVisibility.ts` defines `fresh`, `stale`, and `unknown` runtime visibility.
- Dashboard mock fixtures include stale workers, SOS alerts, approval queues, runtime visibility, and paper-trading examples.

Dashboard should display resolver output, not infer authority from filenames or mock fixtures.

## Relay Freshness Risks

Relay is explicitly legacy fallback:

- `Relay/LEGACY_CLI_RELAY_README.md` states relay approval evidence is historical unless a current approved packet promotes it.
- Relay reports include old night summaries, alert files, SOS outbox records, and close-loop reports.
- Relay approval files include active-looking historical records, examples, and waiting records.
- The casing split between `Relay/` and `relay/` can duplicate apparent source paths.

Resolver rule: Relay evidence is `HISTORICAL` by default unless a current packet, current source owner, and current timestamp promote the specific item for a specific read-only decision.

## Telemetry Freshness Risks

Telemetry is a projection layer. It can be fresh as a projection while reporting stale source evidence.

Observed examples:

- `telemetry/runtime/runtime_state.json` has runtime `freshness: fresh` while packet evidence is `STALE`.
- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` aggregates many relay, digest, approval, and telemetry paths into one bridge state.
- `telemetry/morning_digest/PROTECTED_ACTION_READINESS_LATEST.json` includes display and SOS fields, but still cannot approve protected actions.
- `last_notified.json` can suppress repeated notification but cannot prove the underlying blocker was resolved.

Resolver rule: projection freshness and source freshness must be separate fields.

## Freshness Vocabulary

| Term | Meaning | Allowed decision impact |
|---|---|---|
| `CURRENT` | Evidence is from the active source owner, within its decision window, branch/worktree aligned where applicable, not superseded, and source inputs are also current enough for the requested decision. | May inform current display, digest, supervisor, and operator guidance. Never grants approval. |
| `STALE` | Evidence is structurally valid but older than its allowed window, based on a previous Git/runtime state, or generated from stale inputs. | Display with warning; cannot support protected action, vacation readiness proof, or SOS suppression. |
| `HISTORICAL` | Evidence is an archived report, completed record, legacy fallback item, sample, mock fixture, prior digest, prior alert, or previous cycle output. | Detail-only. Must not drive current top-level state unless reclassified by fresh owner evidence. |
| `BLOCKED` | Evidence is missing, empty, malformed, contradictory, unsafe, secret-risk, live/broker-risk, branch/worktree mismatched, validator failed, approval missing for continuation, or freshness cannot be established for a required decision. | Must stop autonomous continuation and surface display or SOS based on severity. |
| `SUPERSEDED` | Evidence has been replaced by newer evidence for the same packet, lane, source, alert, approval, validator, digest, or runtime cycle. | Detail-only. Must not drive latest status. |

Internal note: a parser may temporarily use `UNKNOWN`, but consumer output should map unknown required evidence to `BLOCKED` for protected or operator-relief decisions and to `STALE` or `HISTORICAL` for detail-only displays.

## Freshness Ownership

Freshness ownership should follow source ownership:

- Queue and packet freshness belongs to the canonical work packet state owner.
- Approval freshness belongs to the canonical approval inbox and protected-action gate.
- Worker freshness belongs to worker lease/state ownership.
- Validator freshness belongs to validator evidence ownership.
- Runtime heartbeat freshness belongs to runtime telemetry.
- Digest freshness belongs to the digest generator only for digest artifact age, not source truth.
- Dashboard freshness belongs to display projection only.
- Relay freshness belongs to legacy fallback classification unless promoted by current source evidence.
- Adapter freshness belongs to parse/normalization time and source-input hashes, not operational authority.

The Evidence Freshness Resolver should classify evidence. It should not own queue state, approval state, worker state, validator state, digest authority, notification authority, or dashboard authority.

## Classification Rules

1. Evidence must identify source path, source owner, creation or generation timestamp, and classification basis.
2. Evidence with no timestamp and no safe file timestamp fallback is `BLOCKED` for current decisions.
3. Evidence from reports is `HISTORICAL` for runtime decisions unless it is the output of the current packet being reviewed.
4. Evidence from mock-data, examples, samples, or fixture paths is `HISTORICAL` or `BLOCKED` depending on whether a current decision tries to use it as active state.
5. Evidence from telemetry is a projection and must include both projection freshness and source freshness.
6. Evidence from Relay is `HISTORICAL` by default unless a current approved path and current source owner prove it active.
7. Evidence from `*_LATEST.*` files is not automatically `CURRENT`; latest pointer files must still pass source freshness checks.
8. Evidence with branch/worktree mismatch is `BLOCKED` for repo tasks.
9. Evidence with dirty state captured before later file mutation is `STALE` for repo-state decisions.
10. Evidence with validator status `NOT_RUN`, `FAILED`, `PARTIAL`, or unknown is `BLOCKED` for decisions that require validation.
11. Evidence with approval status `APPROVED` is current only for its exact action, exact scope, exact files, exact branch, exact protected action, and active session or explicit expiry window.
12. Evidence with secret, broker/API, real webhook, real order, or live trading risk is `BLOCKED`.

## Stale Detection Rules

Stale detection should use both time and state transitions.

| Evidence type | Stale trigger |
|---|---|
| Git state | Any later file mutation, branch switch, commit, merge, stage, reset, clean, or elapsed decision window over 15 minutes |
| Work packet state | Newer state file or packet event exists, packet assigned to stale worker, packet updated after evidence timestamp, or state older than queue lease window |
| Worker state | Lease age exceeds worker stale threshold or worker heartbeat absent |
| Validator evidence | Changed files differ from validated files, validator timestamp predates relevant changes, or required validator was skipped/not run |
| Approval evidence | Approval expired, consumed, mismatched, superseded, outside current session, or not exact to action scope |
| Morning Digest | Artifact older than current digest window, generated from stale inputs, or source paths include historical-only records for current decisions |
| Night Supervisor | Older than active night cycle or generated before current runtime/queue/approval state changed |
| Dashboard projection | Runtime visibility source is mock data, stale telemetry, missing source, or generated before latest state transition |
| Relay evidence | Any legacy, processed, done, outbox, historical, sample, or prior alert path unless a current packet promotes it |
| SOS/alert evidence | Alert is older than latest blocker transition, already notified and no longer active, or replaced by newer alert |
| Paper Trading Lab signals | Signal age exceeds paper domain threshold or clock skew detected |

## Superseded Detection Rules

Evidence is `SUPERSEDED` when any of these are true:

- A newer record exists for the same `packet_id`, lane, source owner, and evidence type.
- A newer digest or Night Supervisor cycle exists for the same reporting purpose.
- A newer Git state check exists after a file mutation or branch state change.
- A queue item moved from inbox to running, done, blocked, archived, or error after the evidence timestamp.
- An approval was consumed, rejected, expired, replaced, or moved after the evidence timestamp.
- A validator rerun exists for the same changed file set.
- A `LATEST` pointer changed after the evidence was captured.
- A Relay item moved into `processed`, `done`, `historical`, or `outbox` after a previous active classification.
- A notification was sent for a prior blocker and a newer blocker/resolution transition exists.

## Approval Freshness Rules

Approval freshness is stricter than normal evidence freshness.

Approval evidence is current only when all conditions hold:

- Approval authority is Anthony / AI_OS Owner or the current packet's named Human Owner authority.
- Approval is for the exact protected action type.
- Approval scope matches the exact files, branch, remote, PR, or command preview.
- Approval is not expired, consumed, rejected, malformed, mismatched, or superseded.
- Approval was produced in the current approval context or has explicit replay protection.
- Validator evidence required for the action is present and current.
- No protected path, secret, broker/API, live trading, scheduler, daemon, commit, push, merge, reset, clean, or PR action exceeds the approved scope.

Fresh approval evidence still does not execute anything by itself. It only allows the protected-action gate to present a safe next step or continue under an explicitly approved packet.

## Evidence Expiration Rules

Recommended initial expiration windows:

| Evidence class | Current window |
|---|---:|
| Git branch/worktree status | 15 minutes or until any mutation |
| Dirty baseline classification | Until next Git status-changing event |
| Work packet state | 30 minutes or until state transition |
| Worker heartbeat/lease | Existing worker lease threshold, default 5 minutes if absent |
| Validator result | Until any covered file changes |
| Approval request | Until explicit expiry, consumption, rejection, or scope mismatch |
| Morning Digest | 18 hours maximum, shorter if inputs change |
| Night Supervisor cycle | One night cycle or 12 hours, whichever comes first |
| Runtime visibility telemetry | Existing runtime visibility threshold, default 5 minutes if absent |
| Dashboard mock fixture | Historical immediately for operational decisions |
| Bridge audit report | Historical immediately for runtime decisions after report creation |
| Vacation readiness report | Historical after any blocker, adapter, queue, approval, or dirty baseline change |
| Relay historical artifact | Historical immediately |
| SOS alert | Current only while underlying blocker remains active and unsuperseded |

## What Already Exists

- Evidence vocabulary in `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`.
- Adapter output fields for `display_alert`, `sos_wake_required`, `executable=false`, and parse-time freshness.
- Morning Brief freshness checks for digest files and bridge state.
- Night Supervisor result classification and evidence-only boundary.
- Runtime visibility code with `fresh`, `stale`, and `unknown`.
- Queue health example with stale packet visibility and stale-after minutes.
- Runtime telemetry that already detects stale packet evidence.
- Relay legacy fallback statement that limits relay approval evidence.
- Dashboard mock fixtures that mark many states as reference-only.
- Paper Trading Lab stale signal checks.

## What Is Missing

- A single freshness resolver that normalizes current/stale/historical/blocked/superseded across sources.
- Source-owner aware freshness checks for `*_LATEST.*` files.
- Separate projection freshness and source freshness fields in every consumer-facing evidence object.
- A dedupe key using source owner, packet/lane, event type, source path, timestamp, and source hash.
- Standard expiration windows per evidence type.
- Approval freshness validation against exact action scope and replay protection.
- Superseded detection across queue, approval, digest, alert, validator, worker, Git, and Relay states.
- Dashboard labels that distinguish mock, historical, stale, current, blocked, and superseded.
- Night Supervisor proof that stale source evidence cannot suppress SOS or vacation blockers.
- Morning Digest proof that fresh digest generation from stale inputs is downgraded.
- Relay casing consolidation or resolver-level casing normalization.
- Vacation-trial proof that the same blocker is classified identically in Night Supervisor, Morning Digest, Dashboard, and SOS surfaces.

## What Should Become Canonical

Only these should become canonical after a separate approved promotion:

- The five freshness classes: `CURRENT`, `STALE`, `HISTORICAL`, `BLOCKED`, `SUPERSEDED`.
- Source-owner rule: freshness classification follows the canonical owner of the underlying evidence, not the consumer displaying it.
- Evidence-is-not-approval rule for all freshness outputs.
- Projection/source separation: every display, digest, dashboard, and supervisor output must distinguish projection freshness from source freshness.
- Approval freshness rules tied to exact action scope, expiry, consumption, replay protection, and protected-action gates.
- Superseded detection rule for latest pointers, packet state, approval state, validator reruns, and Git state.

This should be promoted by editing the existing appropriate authority or workflow file under a separate approved packet, not by creating a new governance head.

## What Should Remain Adapter-Only

These should stay inside future resolver adapters or source adapters:

- How to parse Codex final-response text into freshness inputs.
- How to parse ChatGPT packet evidence into freshness inputs.
- How to classify Relay legacy records and casing variants.
- How to read dashboard mock/source labels.
- How to extract `generated_at` versus file modified time.
- How to hash source evidence for dedupe.
- How to classify domain-specific paper-trading stale signal checks.
- How to format downstream evidence for Morning Digest, Dashboard, Night Supervisor, Approval Projection, and SOS.

Adapter-only logic should not define approval authority, queue ownership, worker ownership, validator ownership, or protected-action permission.

## Consumer Rules

### Morning Digest

Morning Digest should:

- Show digest artifact freshness.
- Show source freshness for each major input.
- Downgrade fresh digest output to `STALE` if source inputs are stale.
- Treat historical Relay artifacts as detail-only.
- Never suppress SOS from stale inputs.

### Night Supervisor

Night Supervisor should:

- Emit cycle freshness and source freshness separately.
- Treat stale source evidence as `BLOCKED` when deciding unattended continuation.
- Keep approval classification separate from approval execution.
- Keep proposed runtime state separate from active runtime state.

### Dashboard

Dashboard should:

- Label mock, projection, source, historical, stale, superseded, and blocked records distinctly.
- Default to display-only for mock fixtures.
- Never show `LATEST` as current unless resolver classification is current.
- Surface `BLOCKED` and SOS-worthy freshness failures clearly.

### Relay

Relay should:

- Remain legacy fallback.
- Treat old approvals, outbox records, done records, processed handoffs, prior alerts, and prior SOS files as historical.
- Require current source-owner evidence before any relay item influences active status.

### Telemetry

Telemetry should:

- Preserve projection freshness.
- Add or consume source freshness when available.
- Avoid using a fresh export timestamp to imply fresh packet, approval, validator, or queue state.

### SOS

SOS should:

- Wake only on current unsuperseded blockers that stop safe continuation.
- Not wake for historical reports, samples, fixtures, or superseded alerts.
- Not suppress wake because a stale `last_notified` file exists.
- Treat missing freshness for a required vacation blocker as `BLOCKED`.

## Vacation Readiness Impact

Freshness resolution is a vacation candidate blocker because stale evidence can create both false safety and false interruption.

| Duration | Freshness requirement |
|---|---|
| 4 hours | Current queue, approval, validator, dirty baseline, and SOS evidence for active blockers |
| 12 hours | Night Supervisor and Morning Digest must agree on source freshness and blocked continuation |
| Overnight | SOS must not depend on stale alert files or stale `LATEST` pointers |
| Weekend | Evidence expiration, superseded detection, approval freshness, dashboard visibility, and failover proof must be consistent across cycles |

Current blocker effect: without a resolver, AI_OS cannot prove that "no SOS" means "safe to continue" rather than "stale evidence failed to notice the blocker."

## Acceptance Tests Needed Later

Future tests should prove:

1. Fresh evidence with matching source owner, timestamp, branch/worktree, and hash classifies as `CURRENT`.
2. Fresh digest generated from stale Relay input classifies digest source state as `STALE`.
3. Historical Relay approval cannot become current approval authority.
4. Dashboard mock fixture cannot drive active state.
5. `LATEST` pointer with old `generated_at` classifies as `STALE`.
6. Newer packet state supersedes older packet evidence.
7. Consumed approval supersedes prior approved evidence.
8. Validator evidence predating a file change classifies as `STALE` or `BLOCKED`.
9. Branch/worktree mismatch classifies repo evidence as `BLOCKED`.
10. Secret or live-trading risk classifies evidence as `BLOCKED`.
11. Runtime projection can be fresh while source evidence is stale.
12. SOS wake is required for current unsuperseded blocker evidence.
13. SOS wake is not required for historical or superseded alerts.
14. Unknown required freshness for vacation mode classifies as `BLOCKED`.

## Exact Future Implementation Boundary

Future implementation should be preview-only first:

- Read evidence records.
- Normalize source owner, source path, timestamps, source hash, packet/lane, projection timestamp, source timestamp, decision purpose, and status.
- Emit freshness classification.
- Emit `display_alert`, `sos_wake_required`, `wake_class`, `next_safe_action`, and `executable=false`.
- Write no queues.
- Write no approvals.
- Launch no workers.
- Run no Codex, OpenAI, MCP, broker, webhook, or external service.
- Execute no protected actions.
- Create no new bridge.

The first implementation should likely live under an adapter path only after a separate approved APPLY packet, with tests and fixtures. It should not edit governance, telemetry producers, dashboard, Night Supervisor, or Morning Digest until the resolver proof exists.

## Exact Next APPLY Packet Recommendation

Create a report-only mapping or acceptance-test packet before code:

Packet ID: EVIDENCE_FRESHNESS_RESOLVER_ACCEPTANCE_TESTS_001
Mode: DRY_RUN or APPLY report-only
Allowed path: `Reports/vacation_candidate/`
Create only: `Reports/vacation_candidate/EVIDENCE_FRESHNESS_RESOLVER_ACCEPTANCE_TESTS.md`

The report should define pass/fail fixtures for current, stale, historical, blocked, superseded, projection-fresh/source-stale, approval-expired, approval-consumed, validator-outdated, branch-mismatch, digest-stale-input, relay-historical, dashboard-mock, and SOS wake classification.

## Final Recommendation

Recommendation: VALIDATE, then BUILD.

Do not consolidate or retire systems until resolver tests prove what evidence is current versus historical. The fastest safe path is:

1. Define resolver acceptance tests.
2. Scaffold preview-only resolver adapter.
3. Prove classifications against existing Morning Digest, Night Supervisor, Dashboard, Relay, telemetry, and adapter evidence.
4. Only then wire consumers to display resolver output.

Status: DRY_RUN discovery complete. No source code, scripts, schemas, queues, approvals, bridges, commits, or pushes were created.
