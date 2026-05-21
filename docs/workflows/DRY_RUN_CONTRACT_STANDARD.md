# AI_OS DRY_RUN Contract Standard

Status: canonical workflow standard

## Purpose

This document defines the system-wide DRY_RUN contract for AI_OS scripts, workers, validators, repair tools, orchestration commands, and future automation.

In AI_OS, DRY_RUN means inspect, validate, simulate, and report without applying mutation. DRY_RUN output may describe what would happen during an approved APPLY path, but it must not perform that APPLY behavior.

DRY_RUN is a safety boundary, not only a naming convention. A script, command, worker, validator, or tool that claims DRY_RUN mode must preserve operator control, avoid hidden side effects, and produce enough evidence for a human to decide the next safe step.

Existing DRY_RUN drift should be treated as legacy contract drift unless direct evidence proves otherwise. The repair target is this contract.

## Contract Guarantees

During DRY_RUN, the following must always be true:

- No files are created, edited, deleted, moved, renamed, copied, or overwritten.
- No registries, ledgers, queues, checkpoints, reports, runtime memory, telemetry stores, or worker state files are modified.
- No git staging, commit, push, merge, reset, clean, branch mutation, or remote mutation is performed.
- No startup task, scheduled task, autonomous loop, worker cycle, daemon, runtime supervisor, browser launch, dashboard launch, or background process is started.
- No broker, webhook, OANDA, live trading, real order, credential, secret, or private data path is activated.
- No approval is inferred from validator output, dashboard output, terminal output, queue state, packet state, or script output.
- Any proposed mutation is reported as a skipped action, not executed.
- Any uncertainty about mutation risk fails closed as `STOP` or `CONTRACT_VIOLATION`.

## Allowed Operations

DRY_RUN may perform read-only inspection and reporting, including:

- Read files.
- Parse files.
- Inspect current state.
- Validate structure.
- Check path existence.
- Read git status, branch, diff, or log information without changing git state.
- Simulate decisions.
- Report planned actions.
- Identify required approvals.
- Generate console preview output.
- Generate diff or patch preview output without applying it.
- Validate schemas, contracts, registry entries, topology, or workflow structure without repairing them.
- Return PASS, WARN, STOP, or CONTRACT_VIOLATION findings.

Allowed operations must remain read-only. A command is not DRY_RUN-compliant if it writes a preview file, appends a log, updates a queue, refreshes telemetry, or modifies any state while claiming DRY_RUN.

## Forbidden Operations

DRY_RUN must not:

- Write files.
- Delete files.
- Rename files.
- Move files.
- Copy files as an applied change.
- Overwrite files.
- Modify registries.
- Modify ledgers.
- Modify queues.
- Enqueue work.
- Update runtime state.
- Update worker state.
- Update telemetry state.
- Update dashboard state.
- Create reports as files.
- Create checkpoints.
- Claim or release locks.
- Start autonomous worker cycles.
- Launch workers.
- Launch runtime supervisors.
- Launch daemons.
- Register startup behavior.
- Register scheduled tasks.
- Commit changes.
- Push changes.
- Merge branches.
- Perform hidden side effects.
- Silently fall back to APPLY-like behavior.

If a future workflow needs a file artifact, queue mutation, report write, lock mutation, or runtime update, that action must be in an APPLY path with explicit human approval, scoped validation, and a defined stop point.

## Reporting Requirements

Every DRY_RUN output must clearly show:

- DRY_RUN mode is active.
- What was inspected.
- What would have changed if APPLY were approved.
- What mutation was skipped.
- Whether findings are `PASS`, `WARN`, `STOP`, or `CONTRACT_VIOLATION`.
- Whether approval is required before any APPLY path.
- Whether files were changed.
- Whether git staging, commit, or push occurred.
- The next safe action.

Recommended status meanings:

- `PASS`: DRY_RUN inspection completed and no blocking issue was found.
- `WARN`: DRY_RUN inspection found a non-blocking issue that requires review before escalation.
- `STOP`: DRY_RUN inspection found a blocker. Do not proceed to APPLY, launch, commit, push, or worker execution.
- `CONTRACT_VIOLATION`: A DRY_RUN path attempted, contained, or depended on mutation behavior that violates this standard.

DRY_RUN output must not imply that a planned action was approved. Output is evidence only.

## Validator Expectations

Validators must treat DRY_RUN mutation as a STOP-level governance issue.

Validators should fail closed when a DRY_RUN script:

- Contains file-writing or file-mutating commands.
- Mutates queues, registries, ledgers, checkpoints, runtime memory, worker state, telemetry, or reports.
- Starts processes, workers, autonomous loops, daemons, runtime supervisors, startup actions, or scheduled tasks.
- Calls another script that performs mutation while preserving a DRY_RUN label.
- Uses output from another command as execution approval.
- Hides side effects behind helper names or preview labels.

Validator output must report the evidence path, the suspected mutation behavior, the failed contract rule, and the next safe action. Validators must not auto-repair DRY_RUN violations unless a separate APPLY task explicitly approves that exact repair.

## Legacy Repair Guidance

Existing scripts using DRY_RUN should be repaired one at a time against this contract.

Repair work should:

- Inspect the script behavior before editing.
- Classify the violation precisely.
- Preserve useful read-only inspection logic where possible.
- Move mutation behavior to an explicitly approved APPLY path when needed.
- Rename or reclassify scripts only through a separate approved task.
- Keep validators report-only unless a future task explicitly approves repair behavior.
- Avoid blame language in reports and documentation.

Existing violations should be described as legacy contract drift unless evidence clearly proves intentional bypass. The goal is to converge behavior on this standard, not to assign fault.

## Naming Rule

Any script named `*.DRY_RUN.ps1` must fully obey this contract.

A DRY_RUN filename is a promise that the script is read-only, report-only, and mutation-free. If a script must write files, mutate state, enqueue work, launch a process, or change git state, it must not rely on a DRY_RUN name to appear safe.

## Non-Goals

This document does not:

- Repair any script.
- Modify any validator.
- Modify any execution registry.
- Wire this standard into automation.
- Resolve TODO duplication.
- Approve APPLY behavior.
- Approve worker launch.
- Approve runtime execution.
- Approve startup behavior.
- Approve commit, push, merge, deployment, broker execution, webhook execution, OANDA, or live trading.

This document defines the contract future repairs and validators should enforce.
