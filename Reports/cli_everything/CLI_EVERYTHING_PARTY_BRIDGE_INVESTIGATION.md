# CLI Everything Party Bridge Investigation

Status: DRY_RUN REPORT - evidence only.
Packet ID: CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION_002
Worker: Codex CLI Worker
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os

## Purpose

Investigate where AI_OS needs CLI coverage for all parties so the system can move toward evidence-based autonomy with operator SOS only.

This report does not create authority, automation, scripts, source changes, protected edits, commits, pushes, live trading paths, broker paths, secrets, or production behavior.

## Authority and Evidence Read

- `AGENTS.md`: highest local repo authority for Codex conduct, packet governance, protected actions, SOS-only alerting, and report format.
- `README.md`: front-door project identity and operating model.
- `WHITEPAPER.md`: protected pointer to `docs/architecture/AI_OS_WHITEPAPER.md`; confirms paper-only Trading Lab boundary.
- `docs/governance/operational-doctrine.md`: current AI tool routing contract and role boundaries.
- `docs/governance/AI_OS_REPO_MEMORY.md`: bootstrap memory; records SOS-only operating rule and prior repo state context.
- `docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md`: existing CLI Everything spine/bridge context found during duplicate-intent search.
- `tools/bridge/README.md`: existing bridge note for Codex, ChatGPT, Claude review, and ADB SOS behavior found during duplicate-intent search.

## Duplicate-Intent Search Result

Search terms included `CLI Everything`, `cli_everything`, `party bridge`, `CLI coverage`, `SOS-only`, `operator SOS`, `evidence-based autonomy`, and `command surface`.

Findings:

- Existing CLI Everything workflow material exists in `docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md`.
- Existing bridge material exists in `tools/bridge/README.md`.
- No existing `Reports/cli_everything/` report directory existed before this task.
- No existing party-by-party CLI coverage investigation report was found.

Conclusion: creating this DRY_RUN report does not duplicate a current report artifact. It must remain evidence only and must not compete with the workflow authority in `docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md` or the routing authority in `docs/governance/operational-doctrine.md`.

## Party, Tool, and Layer CLI Coverage Matrix

| Party / layer | Current role | Proposed CLI command surface | Evidence emitted | SOS-only conditions | Must remain human-approved |
|---|---|---|---|---|---|
| Anthony / Human Owner | Final approval authority for protected actions, role changes, safety overrides, live-risk decisions, and high-risk governance. | `aios approvals list`, `aios approvals show <id>`, `aios approvals decide <id> --approve/--reject --reason`, `aios sos ack <id>`. | Approval decision record, decision timestamp, approved action scope, rejected reason, operator identity, expiry. | Only wake when protected action approval is required, safe continuation is blocked, branch/worktree mismatch blocks work, validation failure blocks continuation, or safety policy blocks execution. | All protected actions, commits, pushes, merges, PR creation/merge, branch deletion, reset/clean, secrets, credentials, broker/API, live trading, governance authority edits, role elevation. |
| ChatGPT Personal / Orchestrator | Converts Anthony goals into packets, next safe actions, and plain-language operator guidance. | `aios packet validate <file>`, `aios packet render --from-goal <file>`, `aios route inspect <goal-file>`, `aios next-action summarize <evidence-dir>`. | Packet validation report, missing-field list, ownership classification, lane recommendation, next-safe-action summary. | Wake only when packet generation cannot complete safely, required human decision is missing, conflicting authority is detected, or protected action approval must be requested. | Final approval of generated packets for protected actions, acceptance of role changes, approval to use APIs or external accounts, any mutation not explicitly delegated. |
| Codex East / Repo Executor | Primary bounded repo worker for DRY_RUN/APPLY tasks, file edits, local validation, and completion reporting. | `aios codex preflight`, `aios codex run --packet <file> --mode DRY_RUN/APPLY`, `aios codex validate --changed-files <list>`, `aios codex report --format aios`. | Repo path, branch, dirty state, allowed/forbidden path check, changed file list, diff summary, validator output, final report, executable=false unless approved. | Wake only on invalid packet, missing required fields, forbidden path request, validator failure, sandbox failure that blocks mission, protected action request, branch mismatch, unknown dirty overlap, or unsafe continuation. | Commits, pushes, merges, PR creation, protected path edits unless scoped, source changes outside packet boundary, secrets, broker/API/live trading, recursive Codex calls. |
| Claude Chat / Inspector | Read-only reviewer, contradiction finder, architecture/risk auditor, second opinion. | `aios review request --packet <file> --evidence <dir>`, `aios review ingest --source claude --file <report>`, `aios review compare --codex <report> --claude <report>`. | Review findings, severity, file references, contradiction report, approval-gap report, recommendation-only flag. | Wake only when review finds a blocker that prevents safe continuation or detects a serious safety/authority conflict that requires Anthony decision. | Repo mutation by Claude, direct approval, protected actions, self-promotion into execution authority, editing East-owned files without assignment. |
| Claude Code West / Assigned Specialist | Bounded West worksite worker only when explicitly assigned a lane, allowed paths, blocked paths, and stop point. | `aios west preflight --packet <file>`, `aios west run --packet <file> --mode DRY_RUN/APPLY`, `aios west handoff --report <file>`. | West identity, lock/lane evidence, allowed path proof, changed files if APPLY approved, validation evidence, handoff report. | Wake on East/West ownership collision, missing lane, missing allowed paths, protected path request, validator failure, or unclear assignment. | Cross-lane edits, governance changes, commits, pushes, merges, role elevation, protected actions, live trading or broker/API paths. |
| Relay / Handoff and Evidence Mailroom | Carries task files, approvals, outputs, errors, reports, and handoffs as runtime evidence. | `aios relay inbox list`, `aios relay enqueue --packet <file>`, `aios relay outbox list`, `aios relay archive --id <id>`, `aios relay evidence show <id>`. | Queue item ID, source, checksum, created/processed timestamps, state transition log, archived evidence path, executable=false by default. | Wake when queue corruption, missing evidence, duplicate IDs, unsafe packet, approval-required item, or blocked state prevents safe continuation. | Treating Relay as authority, executing packets, approving actions, deleting evidence, moving protected artifacts, writing secrets. |
| Night Supervisor | Overnight evidence reader and digest producer; flags blocked, stale, unsafe, approval-needed, completed items. | `aios night scan --once`, `aios night digest --input <evidence-dir>`, `aios night classify --item <id>`, `aios night report latest`. | Digest JSON/markdown, active blockers, stale warnings, recommendation-only items, SOS wake flag, display-alert flag, evidence references. | Wake only for true blocked continuation, protected action needing explicit approval, unsafe state, or failed supervisor loop. Routine summaries remain display-only. | Approve/reject, commit, push, merge, trade, mutate protected files, execute tasks, override validators. |
| Autonomy Bridge / Approval Queue Projection | Converts Relay and Night Supervisor evidence into dashboard-ready state and approval visibility. | `aios bridge state build`, `aios bridge approvals project`, `aios bridge status latest`, `aios bridge export --format json`. | Bridge state JSON, active/current buckets, blockers, approval cards, stale-state warnings, `display_alert`, `sos_wake_required`, source evidence. | Wake only when projection discovers active blocker, missing required approval, or evidence mismatch that blocks safe continuation. | Approval authority, execution authority, mutation of source queues without approved policy, secrets, broker/API/live trading. |
| MCP / API Platform | Future local-first tool connection layer; read-first by current doctrine. | `aios mcp tools list`, `aios mcp read --tool <name> --query <safe>`, `aios mcp audit-permissions`, `aios mcp dry-run <tool-call-file>`. | Tool inventory, permission boundary, request/response metadata, redaction status, fail-closed reason, no-secret proof. | Wake on missing permission boundary, attempted write without approval, external account/API risk, secret exposure risk, or unknown tool scope. | Write tools, external API calls, credentials, production mutation, protected actions, live trading, approval bypass. |
| OpenAI CLI / API Layer | Potential model/API execution layer for future reviewed workflows; not current primary path. | `aios openai status --no-secret`, `aios openai dry-run-prompt <file>`, `aios openai cache-plan inspect`, `aios openai eval-summary <file>`. | CLI availability, model/account availability without secrets, prompt-cache suitability, request classification, estimated risk/cost, no plaintext keys. | Wake when credentials are missing for an explicitly approved API task, quota/access blocks approved work, or a prompt would send secrets/protected data. | API key creation/use, paid API calls, sending private evidence, secret handling, model upgrade policy, external data transmission. |
| Git / GitHub CLI | Repo state, branch, PR, checks, review, commit/push mechanics under protected gates. | `aios git preflight`, `aios git diff-summary --files <list>`, `aios git commit-gate --packet <file>`, `aios github pr-status <id>`, `aios github checks <id>`. | Branch, remote, dirty state, changed files, cached diff proof, check status, PR metadata, protected-action packet decision. | Wake when merge conflict, branch mismatch, unreviewed dirty files, failed checks, protected-action approval needed, or push/merge is blocked. | Stage, commit, push, merge, PR creation/merge, branch delete, reset, clean, force-push, direct push to protected main. |
| PowerShell / Local Terminal Shell | Local command execution substrate for validation, reports, and operator helper commands. | `aios shell allowlist`, `aios shell explain <command-file>`, `aios shell run-safe --command-id <id>`, `aios shell audit-log latest`. | Command preview, allowlist match, working directory, exit code, stdout/stderr summary, write paths, escalation reason. | Wake when a command is destructive, writes outside scope, requires secrets, starts services, touches broker/API/live trading, or fails in a way that blocks mission. | Destructive commands, broad shell passthrough, filesystem cleanup, service/daemon/scheduler start, external calls, secrets, protected actions. |
| `aios.ps1` Safe CLI Modes | Operator-friendly wrapper for bounded safe modes. | `.\aios.ps1 -Mode preflight`, `-Mode bridge`, `-Mode runtime-bridge`, `-Mode night-mission`, `-Mode commit-push-dry-run`, future `-Mode evidence-status`. | Mode selected, resolved module, parameter validation, blocked capability list, exit code, report path. | Wake when required parameter missing, mode attempts blocked capability, validator fails, or approved task cannot continue. | Adding risky modes without review, commit/push execution outside hard gates, shell passthrough, API calls, recursive Codex, daemons/watchers/services. |
| Approval Resume Loop | Validates human approval decisions against archived task/outbox evidence before continuation. | `aios approvals resume --decision <file>`, `aios approvals validate --task <id>`, `aios approvals pending`, `aios approvals history`. | Decision validity, scope match, expiry check, archived task reference, outbox reference, resume recommendation. | Wake when decision is malformed, expired, mismatched, missing, or attempts to approve a protected action outside scope. | Self-approval, widening approval scope, protected-action execution without current-session approval, merge/push/commit approval transfer. |
| Packet Queue / Workload Intake | Holds packet candidates, task specs, and bounded next work items. | `aios queue add --packet <file>`, `aios queue validate`, `aios queue next --dry-run`, `aios queue status`, `aios queue reject <id> --reason`. | Packet ID, completeness validation, allowed/forbidden paths, mode, lane, priority, blocker list, next safe action. | Wake when malformed packets, placeholder fields, duplicate authority, branch-state mismatch, or unsafe action appears. | Executing queued packets automatically, editing packet content silently, promoting reports to authority, bypassing Anthony approval. |
| Validator Chain | Runs and records validation evidence for a specific lane. | `aios validate plan --packet <file>`, `aios validate run --chain <file>`, `aios validate report <id>`, `aios validate diff-check`. | Validator list, command results, pass/fail, skipped reason, changed-file coverage, evidence path. | Wake when required validator fails, validator is missing, evidence conflicts, or validation scope cannot prove safety. | Treating PASS as approval, changing validator requirements without authority, approving commits/pushes/merges. |
| Telemetry / Engine Room | Local visibility over worker activity, DRY_RUN/APPLY counts, validators, git state, approvals, queues, and stage progress. | `aios telemetry snapshot`, `aios telemetry status`, `aios telemetry heatmap --dry-run`, `aios telemetry redact-check`. | Local-only metrics, current status buckets, redaction proof, freshness timestamp, source evidence links. | Wake when telemetry indicates active blocker, stale projection causing unsafe decision, or secret/private data risk. | Collecting secrets, importing private raw evidence, triggering execution, treating telemetry as approval, live trading telemetry paths. |
| Dashboard / Operator UI | Human-readable display surface for status, approvals, blockers, and morning briefs. | `aios dashboard export-state`, `aios dashboard preview-data`, `aios dashboard health --dry-run`. | Display-state JSON, active decision cards, stale warnings, current blocker list, no-secret proof. | Wake only through the notification layer when state is true SOS; normal UI alerts remain display-only. | Approving protected actions by display alone, executing repo actions, collecting secrets, touching live trading, changing governance. |
| Notification Layer / ADB / Telegram / Tasker | Human wake/alert path; current doctrine favors SOS-only and separates display alerts from wake alerts. | `aios notify classify --event <file>`, `aios notify dry-run --event <file>`, `aios notify adb-sos --approved-event <id>`, `aios notify status`. | Classification, `display_alert`, `sos_wake_required`, wake class, delivery result, failure reason, no-secret proof. | Wake only for true SOS: blocked continuation, protected action approval needed, safety failure, validator failure blocking work, or loop failure. | Real notification sends unless explicitly approved, credential setup, Telegram/Tasker production routing, spamming routine warnings, secrets. |
| Trading Lab / Paper-Only Vertical | First production vertical; paper simulation, backtesting, signal validation, latency tracking, paper ledgers. | `aios trading paper-status`, `aios trading validate-paper-run`, `aios trading latency-report`, `aios trading ledger-check --paper-only`. | Paper-only proof, no-broker proof, simulated order ledger, latency metrics, validator output, blocked-live flags. | Wake on any broker/API/live-order path, credential detection, live execution attempt, or paper/live boundary mismatch. | Live broker execution, OANDA integration, real orders, real webhooks, API keys, credentials, LLM in live order execution path. |
| Pi5 / Device Health / Local Display | Device baseline and possible display/notification endpoint; no repair/GPIO/motor actions from repo guidance. | `aios device pi5-health --read-only`, `aios device display-state --dry-run`, `aios device evidence collect --safe`. | Host reachability, mount status, disk health summary, display payload preview, no repair action proof. | Wake on I/O errors, ext4 errors, read-only remounts, boot failures, SMART failures, unexplained data loss, or display path blocking operator approval. | Repair commands, GPIO/motor actions, destructive device operations, credential changes, production service installs. |
| Reports / Evidence Artifacts | Historical outputs and investigation reports; not source authority unless promoted. | `aios reports list`, `aios reports create --type dry-run`, `aios reports classify`, `aios reports duplicate-intent-search`. | Report path, status label, source files read, duplicate search results, creation timestamp, validation results. | Wake when report would duplicate authority, overwrite evidence, leak secrets, or require protected path edits. | Promotion to authority, overwrites, protected edits, commits/pushes, raw private evidence import. |

## Cross-Cutting Evidence Requirements

Every CLI-controlled party should emit machine-readable evidence with these minimum fields:

- party/layer identity
- command or mode requested
- mode: DRY_RUN, APPLY, READ_ONLY, or PROTECTED_ACTION_REVIEW
- branch and worktree when repo state matters
- allowed paths and forbidden paths when filesystem scope matters
- inputs used, with hashes for packet/evidence files
- outputs written, if any
- validation commands and results
- blocked conditions and risk flags
- `executable=false` unless explicitly approved execution is in scope
- `display_alert`
- `sos_wake_required`
- next safe action
- stop point

## SOS-Only Conditions

SOS should be reserved for cases where AI_OS cannot safely continue or must obtain explicit Human Owner approval:

- protected action requested or required
- missing, malformed, expired, or mismatched approval
- invalid or incomplete executable packet
- branch/worktree mismatch that blocks the assigned task
- dirty files with unknown or overlapping mission ownership
- forbidden path or protected path request
- validator failure that blocks continuation
- secret, credential, broker/API, live trading, or real-order risk
- evidence mismatch that would make the next action unsafe
- queue corruption, duplicate IDs, overwrite risk, or missing required evidence
- sandbox/tool failure that blocks the mission and cannot be safely worked around
- device or notification failure that prevents required protected-action approval from reaching Anthony

Routine success, stale display warnings, recommendation-only items, historical noise, and non-blocking summaries should remain display-only.

## What Must Remain Human-Approved

- All protected repo actions: `git add`, `git commit`, `git push`, PR creation, PR merge, `git merge`, `git reset`, `git clean`, branch deletion.
- Any direct push to protected `main`, except separately approved emergency exception.
- Protected governance edits, including `AGENTS.md`, root authority files, and canonical governance files.
- Role elevation for any AI worker, validator, dashboard, telemetry event, MCP tool, or automation loop.
- External API usage, OpenAI API calls, paid model calls, or private evidence transmission.
- Credential creation, credential storage, credential lookup beyond presence checks, and secret handling.
- Broker/API/live trading, real orders, real webhooks, OANDA integration, or any live execution path.
- Daemons, watchers, services, scheduler registration, recurring unattended execution, or production deployment.
- Destructive filesystem actions, broad cleanup, archive restoration, or evidence deletion.
- Promotion of a report, template, telemetry artifact, or generated output into authority.

## Recommended Build Order

1. Evidence schema first: define one shared CLI evidence envelope for reports, bridge state, queue state, validation, notifications, and approval decisions.
2. Read-only inventory commands: expose `aios status`, `aios queue status`, `aios approvals pending`, `aios bridge status`, and `aios reports list`.
3. Packet validation CLI: validate ownership, required fields, branch/worktree alignment, allowed/forbidden paths, placeholder defects, and duplicate-authority risk.
4. Approval projection CLI: list/show approval cards and validate decisions against archived task/outbox evidence without executing protected actions.
5. Validator CLI: run lane-specific validators and emit normalized evidence; keep PASS as evidence only.
6. Notification classifier CLI: separate display alerts from SOS wake alerts and keep real sends approval-gated.
7. Codex/worker handoff CLI: create non-executable handoff records for Codex, Claude, and future MCP/API layers.
8. Runtime bridge hardening: process exactly one task, fail closed, emit `executable=false`, archive safely, and block source/protected writes unless separately approved.
9. Protected action packet review CLI: generate and validate protected-action packets without staging, committing, pushing, or merging.
10. Optional API/MCP read-only adapters: add only after local evidence schema, approval gates, and redaction checks are stable.

## Risks and Blockers

- Duplicate authority risk: existing CLI Everything workflow text already exists; this report must not become a competing workflow authority.
- Tool sprawl risk: adding per-party CLIs without one shared evidence envelope will make autonomy harder to verify.
- Approval confusion risk: validators, dashboards, telemetry, and bridge state must never approve actions.
- SOS fatigue risk: routine `NEEDS_APPROVAL` or stale display alerts must not wake Anthony unless safe continuation is blocked.
- Secret risk: API/CLI integrations can accidentally expose tokens, chat logs, private evidence, or broker credentials.
- Recursive execution risk: Codex, OpenAI, Claude, MCP, or shell passthrough must not be allowed to self-trigger without reviewed policy.
- Branch-state risk: packets must stay aligned to observed repo state and dirty file ownership.
- Protected path risk: future APPLY packets must avoid broad source/governance edits unless explicitly scoped.
- Trading boundary risk: paper-only Trading Lab must not drift toward broker/API/live order execution.
- UI/display mismatch risk: dashboard or notification wording can imply urgency or approval authority when it is only evidence.
- External dependency risk: ChatGPT, Claude, OpenAI API, GitHub, ADB, Telegram, Tasker, and MCP can fail due to auth, network, account limits, or local device availability.

## Exact Next APPLY Packet Recommendation

Do not implement all party CLIs at once. The next safe APPLY should create a narrow evidence contract document only, not scripts or automation.

Recommended packet:

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
ChatGPT Chief Orchestrator

PACKET ID:
CLI_EVERYTHING_EVIDENCE_CONTRACT_APPLY_001

ZONE:
Reports / CLI Everything / Evidence Contract APPLY

WORKER IDENTITY:
Codex CLI Worker

MODE:
APPLY

BRANCH:
feature/full-operator-relief-closed-loop-v1

WORKTREE:
C:\Dev\Ai.Os

REPO STATE ALIGNMENT:
Use the current observed branch/worktree state. Do not switch branches.

APPROVAL AUTHORITY:
Anthony / AI_OS Owner / Human Approval Authority

ALLOWED PATHS:
Reports/cli_everything/

FORBIDDEN PATHS:
AGENTS.md
README.md
WHITEPAPER.md
docs/governance/
automation/
tools/
tests/
src/
config/
control/
Relay/
.github/
Any source, script, workflow, secret, trading, broker, commit, push, merge, delete, or production path.

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read docs/governance/operational-doctrine.md.
4. Read Reports/cli_everything/CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION.md.
5. Confirm branch and dirty file status.
6. Search for existing CLI evidence contract reports before writing.
7. Create only Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md.
8. Run git diff --check.
9. Report git status --short --branch.

STOP POINT:
Stop after report creation and validation. No commit. No push. No source edits. No automation creation.

MISSION:
Create a DRY_RUN-derived evidence contract report that defines the shared CLI evidence envelope and status vocabulary for future CLI Everything work.

TASK:
Create Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md with:
1. evidence envelope fields.
2. required status vocabulary.
3. display-alert vs SOS-wake rules.
4. approval evidence fields.
5. validation evidence fields.
6. blocked/protected action evidence fields.
7. redaction/no-secret requirements.
8. exact follow-up APPLY recommendation for read-only CLI inventory commands.

STRICT RULES:
- Report only.
- No source code changes.
- No scripts.
- No commits.
- No pushes.
- No protected file edits.
- No live trading paths.
- No broker paths.
- No secrets.
- No automation creation.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

## Final Recommendation

Build the shared evidence envelope before adding more CLI commands. That keeps every future party command measurable, fail-closed, reviewable, and compatible with SOS-only operator interruption.
