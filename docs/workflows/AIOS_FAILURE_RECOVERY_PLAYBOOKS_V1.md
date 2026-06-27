# AIOS Failure Recovery Playbooks V1

## Purpose

Provide deterministic recovery playbooks for common AIOS campaign failures so Codex can classify, record, recover, validate, and resume inside approved packet scope without improvising unsafe repair behavior.

## Scope

These playbooks apply to governed AIOS packets that already passed authorization and are running inside named worktree, branch, lane, allowed path, forbidden path, validator, and stop-point boundaries.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## Playbook Field Standard

Every playbook uses these fields:

- Detection signature.
- Immediate classification.
- Approved recovery.
- Forbidden recovery.
- Validator required.
- Stop condition.
- Failure memory entry.
- Resume instruction.

## Packet Validation Or Header Failure

- Detection signature: Missing `CODEX-ONLY PROMPT`, `AI_OS EXECUTION TOKEN`, `AI_OS BOOTSTRAP REQUIRED`, identity chain, mode, zone, lane, worktree, branch, allowed paths, forbidden paths, approval authority, validator chain, stop point, mission, preflight, or final report format.
- Immediate classification: `PACKET_INCOMPLETE_BLOCKED`.
- Approved recovery: Stop and list missing fields using the `AGENTS.md` failure response format.
- Forbidden recovery: Guess missing fields, invent branch state, create substitute authority, or execute partial packet content.
- Validator required: Packet completeness review against `AGENTS.md` and `docs/governance/aios-identity-and-lane-governance.md`.
- Stop condition: Any required execution field remains missing or contradictory.
- Failure memory entry: Record missing field group, source packet, and prevention rule.
- Resume instruction: Resume only after a corrected complete tokenized packet is provided.

## Missing Mission Name Program Name Epic Name Or Bucket Name

- Detection signature: IDs are present but one or more of Mission Name, Program Name, Epic Name, or Bucket Name is absent.
- Immediate classification: `IDENTITY_CHAIN_INCOMPLETE_BLOCKED`.
- Approved recovery: Stop and request a corrected packet with the complete hierarchy identity chain.
- Forbidden recovery: Use ID text as a guessed name or reuse names from unrelated packets.
- Validator required: Identity chain check against `docs/governance/AIOS-DEVELOPMENT-HIERARCHY-AND-GOVERNANCE-DOCTRINE-V1.md`.
- Stop condition: Any hierarchy name remains missing.
- Failure memory entry: Record which identity name was missing.
- Resume instruction: Resume from preflight after corrected identity fields are supplied.

## Invalid Mode Such As LOCAL_APPLY

- Detection signature: Packet mode is not exactly `DRY_RUN` or `APPLY`, including values such as `LOCAL_APPLY`.
- Immediate classification: `INVALID_MODE_BLOCKED`.
- Approved recovery: Stop and ask for a corrected mode.
- Forbidden recovery: Treat invalid mode as APPLY or downgrade it silently to DRY_RUN.
- Validator required: Mode validation against `AGENTS.md`.
- Stop condition: Mode remains invalid or ambiguous.
- Failure memory entry: Record invalid mode and source packet.
- Resume instruction: Resume only after the packet has a valid mode.

## AGENTS.md Governance Drift

- Detection signature: Packet, workflow, report, or generated text conflicts with `AGENTS.md`.
- Immediate classification: `AUTHORITY_CONFLICT_BLOCKED`.
- Approved recovery: Follow `AGENTS.md`, document the conflict, and stop if the conflict affects execution authority.
- Forbidden recovery: Create duplicate governance, override `AGENTS.md`, or treat templates/reports as equal authority.
- Validator required: Authority hierarchy review against `AGENTS.md`.
- Stop condition: Conflict changes packet law, approval authority, protected actions, or safety gates.
- Failure memory entry: Record conflicting file and higher authority that won.
- Resume instruction: Resume after the conflicting instruction is corrected or scoped out.

## Dirty Wrong-Branch Worktree

- Detection signature: Current branch is not the packet target or source branch and `git status --short --branch` shows dirty files.
- Immediate classification: `WORKTREE_STATE_MISMATCH_BLOCKED`.
- Approved recovery: Classify dirty files as same-campaign, unrelated, stale, or unsafe. Continue only if every dirty file is same-campaign and inside allowed paths.
- Forbidden recovery: Reset, clean, stash, branch switch away from dirty owner work, or overwrite unrelated changes.
- Validator required: State alignment check from `AGENTS.md`.
- Stop condition: Dirty files are unrelated, unsafe, or ownership cannot be verified.
- Failure memory entry: Record branch, dirty files, and overlap decision.
- Resume instruction: Resume on the same worktree only if dirty files are confirmed same-campaign.

## Wrong Branch For Packet

- Detection signature: `git branch --show-current` returns a branch that does not match the packet target after preflight or branch creation.
- Immediate classification: `BRANCH_MISMATCH_BLOCKED`.
- Approved recovery: Stop and report assumed branch, observed branch, dirty files, overlap, and safest next action.
- Forbidden recovery: Switch branches while dirty, force branch creation, reset, clean, or silently continue.
- Validator required: `git status --short --branch` and branch-name readback.
- Stop condition: Observed branch remains wrong and no explicit safe preservation plan exists.
- Failure memory entry: Record `AIOS-PROMPT-AUTH-STATE-MISMATCH` if packet assumptions caused the mismatch.
- Resume instruction: Resume after owner-approved branch/worktree correction.

## CreateProcessAsUserW Failed 1312

- Detection signature: Shell tool returns `CreateProcessAsUserW failed: 1312`.
- Immediate classification: `WINDOWS_SANDBOX_PROCESS_LAUNCH_FAILURE`.
- Approved recovery: Retry at most once for read-only inspection. Do not retry write or protected commands. Record failure in checkpoint. Continue only when remaining work can proceed safely without the blocked command.
- Forbidden recovery: Loop retries, escalate to destructive commands, run protected Git/GitHub commands again in Codex after known sandbox failure, or hide the blocked command.
- Validator required: Checkpoint entry plus alternate deterministic validation when available.
- Stop condition: The blocked command is required to continue.
- Failure memory entry: Record command, retry count, whether it was read-only, and owner PowerShell handoff if needed.
- Resume instruction: Resume with the next safe non-blocked work item, or wait for owner PowerShell if required.

## Apply Deny-Read ACL

- Detection signature: File read fails with access denied, deny-read ACL, or permission error on a required source file.
- Immediate classification: `ACL_READ_BLOCKED`.
- Approved recovery: Stop if the file is required. If optional, record blocked validator and continue with available evidence.
- Forbidden recovery: Change ACLs, copy private data, bypass permissions, or use alternate private paths.
- Validator required: Missing-read evidence in checkpoint or report.
- Stop condition: Required authority or target file cannot be read.
- Failure memory entry: Record path, command, and required/optional classification.
- Resume instruction: Resume after owner grants access or assigns an alternate safe source.

## Git Index Lock

- Detection signature: Git reports `.git/index.lock` or another index lock blocking a Git operation.
- Immediate classification: `GIT_INDEX_LOCK_BLOCKED`.
- Approved recovery: Stop and produce owner PowerShell handoff for status and process review.
- Forbidden recovery: Delete `.git/index.lock`, reset, clean, or kill processes without explicit owner approval.
- Validator required: Git status attempt and exact lock error.
- Stop condition: Any Git operation required for continuation remains blocked.
- Failure memory entry: Record Git command, lock path, and protected-action boundary.
- Resume instruction: Resume after owner confirms lock is cleared and worktree state is safe.

## Parser False Positive

- Detection signature: Validator flags safe prose, path text, or report language as a violation even though no executable command or sensitive value exists.
- Immediate classification: `VALIDATOR_FALSE_POSITIVE_REVIEW`.
- Approved recovery: Narrow the text, add context, or adjust wording inside approved docs. Record the false positive and rerun the validator.
- Forbidden recovery: Disable the validator, weaken safety language, or remove required governance statements.
- Validator required: Original validator result and rerun result.
- Stop condition: Validator still fails or the fix would weaken safety.
- Failure memory entry: Record pattern, file, and prevention wording.
- Resume instruction: Resume after validator passes or a reviewer classifies the false positive.

## Aggregate Report Re-Ingestion

- Detection signature: A generated aggregate report is re-read as current source authority and causes duplicate conclusions or stale blockers.
- Immediate classification: `REPORT_REINGESTION_RISK`.
- Approved recovery: Mark aggregate reports as evidence only, re-anchor on current canonical files, and record source precedence.
- Forbidden recovery: Promote aggregate text into governance without explicit packet authority.
- Validator required: Source-of-truth check against `docs/governance/source-of-truth-map.md`.
- Stop condition: Active source cannot be distinguished from aggregate evidence.
- Failure memory entry: Record aggregate path and canonical replacement source.
- Resume instruction: Resume from canonical docs, not the aggregate report.

## Report Feedback Loop

- Detection signature: A report cites a prior report that cites the same report chain until stale conclusions reinforce themselves.
- Immediate classification: `REPORT_FEEDBACK_LOOP_REVIEW`.
- Approved recovery: Break the loop by citing direct repo evidence, current authority docs, or terminal output.
- Forbidden recovery: Treat repeated report claims as proof.
- Validator required: Direct-source evidence readback.
- Stop condition: No direct source can verify the claim.
- Failure memory entry: Record loop path and direct evidence replacement.
- Resume instruction: Resume after report summary is re-anchored to current files.

## Missing Module

- Detection signature: Test or command reports an import/module not found.
- Immediate classification: `MISSING_MODULE_REVIEW`.
- Approved recovery: For documentation campaigns, record as out-of-scope unless the packet explicitly allows code or dependency changes.
- Forbidden recovery: Install packages, edit code, or change module paths in a docs-only lane.
- Validator required: Exact command output and scope classification.
- Stop condition: The module is required for packet validation and no in-scope alternative exists.
- Failure memory entry: Record module name and why it was out-of-scope or recovered.
- Resume instruction: Resume with documentation validators or wait for a code/dependency packet.

## Missing Runner

- Detection signature: Expected validator or runner script path is absent.
- Immediate classification: `MISSING_RUNNER_REVIEW`.
- Approved recovery: Use a deterministic alternative if allowed, or record validator blocked.
- Forbidden recovery: Create runner automation in a docs-only lane or run unreviewed scripts.
- Validator required: Path existence evidence and alternate validation result.
- Stop condition: Required validation has no approved alternative.
- Failure memory entry: Record missing runner and alternate used.
- Resume instruction: Resume after alternate validation passes or owner assigns a runner-creation packet.

## Missing Test

- Detection signature: Referenced test file or test command does not exist.
- Immediate classification: `MISSING_TEST_REVIEW`.
- Approved recovery: Record missing test as validation gap and run available structural checks.
- Forbidden recovery: Create tests outside allowed paths or claim unrun tests passed.
- Validator required: Test path readback and available validator output.
- Stop condition: The missing test is required for safety readiness.
- Failure memory entry: Record test gap and prevention rule.
- Resume instruction: Resume with available validators or wait for a test-authoring packet.

## Missing Report

- Detection signature: Required report file or report directory does not exist.
- Immediate classification: `REPORT_COVERAGE_GAP_RECOVERABLE`.
- Approved recovery: Create the approved report path if inside allowed paths and packet requires it.
- Forbidden recovery: Write reports outside approved paths or overwrite unrelated reports.
- Validator required: Report existence check and content structure check.
- Stop condition: Report path cannot be created safely.
- Failure memory entry: Record missing path and creation method.
- Resume instruction: Resume after report exists and checkpoint records creation.

## Schema Drift

- Detection signature: Structured data or docs describe fields that differ from canonical schema or target field names.
- Immediate classification: `SCHEMA_DRIFT_REVIEW`.
- Approved recovery: In docs-only lanes, document drift without changing implementation schemas unless explicitly scoped.
- Forbidden recovery: Rewrite schemas, services, or validators outside allowed paths.
- Validator required: Schema/reference readback and drift note.
- Stop condition: Drift affects execution safety or validator trust.
- Failure memory entry: Record source schema, observed drift, and future packet needed.
- Resume instruction: Resume after drift is documented or a schema packet is assigned.

## Report Drift

- Detection signature: Generated report status conflicts with current Git, file, validator, or authority evidence.
- Immediate classification: `REPORT_MISMATCH_REVIEW`.
- Approved recovery: Correct the current report inside approved paths and mark prior evidence stale or superseded.
- Forbidden recovery: Hide the mismatch or update authority to match stale report language.
- Validator required: Direct evidence readback and updated report check.
- Stop condition: Current state cannot be verified.
- Failure memory entry: Record stale report field and corrected evidence.
- Resume instruction: Resume after report reflects current evidence.

## Broad Pytest Failure

- Detection signature: A broad `pytest` run fails across unrelated modules during a docs-only or narrow lane.
- Immediate classification: `BROAD_VALIDATION_FAIL_REVIEW`.
- Approved recovery: Record broad failure, identify whether failures overlap allowed paths, and run narrower deterministic validators when appropriate.
- Forbidden recovery: Repair unrelated code, silence failures, or claim full test pass.
- Validator required: Failing command summary and scoped validator result.
- Stop condition: Failures overlap safety-critical current work and cannot be isolated.
- Failure memory entry: Record command, failing area, and overlap decision.
- Resume instruction: Resume with scoped validators or wait for a test-fix packet.

## GitHub CI Secret-Assignment False Positive

- Detection signature: CI flags prose or code because source/config assignments use exact sensitive words such as api_key, apikey, secret, token, password, or broker with quoted non-placeholder values.
- Immediate classification: `CI_SECRET_SCAN_FALSE_POSITIVE_REVIEW`.
- Approved recovery: Rename non-sensitive variables, avoid sensitive assignment names in examples, and prefer neutral names such as `broker_status` for quoted status values.
- Forbidden recovery: Disable CI, add real secrets, print credentials, or weaken secret prevention policy.
- Validator required: CI log inspection and local text scan for the flagged pattern.
- Stop condition: CI still flags the pattern or real sensitive data is suspected.
- Failure memory entry: Record flagged file, pattern family, and neutral replacement.
- Resume instruction: Resume after CI passes or owner assigns a focused CI repair packet.

## Markdown Validation Failure

- Detection signature: Markdown validator or structural check reports missing H1, missing Purpose, missing Scope, bad link, trailing whitespace, or diff whitespace issue.
- Immediate classification: `MARKDOWN_STRUCTURE_RECOVERABLE`.
- Approved recovery: Repair markdown structure inside approved docs and rerun validator.
- Forbidden recovery: Remove required safety text, skip validation, or edit unrelated files.
- Validator required: Markdown structural check and `git diff --check`.
- Stop condition: The failing markdown issue cannot be repaired inside allowed paths.
- Failure memory entry: Record file, rule, and repair.
- Resume instruction: Resume after markdown validation passes.

## Context Exhaustion

- Detection signature: Conversation compaction, missing prior tool output, or loss of working memory threatens safe continuation.
- Immediate classification: `CONTEXT_RECOVERY_REQUIRED`.
- Approved recovery: Read checkpoint, read current files, run `git status --short --branch`, and resume from recorded next safe action.
- Forbidden recovery: Restart from memory, redo unrelated work, or assume protected actions occurred.
- Validator required: Checkpoint readback and git status.
- Stop condition: Checkpoint is missing, stale, or conflicts with current repo state.
- Failure memory entry: Record compaction point and resume evidence used.
- Resume instruction: Resume from checkpoint only after current branch and dirty files match.

## Protected Action Required

- Detection signature: Completion requires git add, commit, push, PR creation, check watching, merge, reset, clean, branch deletion, local main sync, or destructive cleanup.
- Immediate classification: `PROTECTED_ACTION_HANDOFF_REQUIRED`.
- Approved recovery: Stop and produce exact owner PowerShell commands.
- Forbidden recovery: Run protected commands in Codex without current-session exact approval or continue after known 1312 protected-action failures.
- Validator required: Diff/status evidence and protected handoff review.
- Stop condition: Protected action remains required.
- Failure memory entry: Record protected action, file list, command block, and owner handoff.
- Resume instruction: Resume after owner performs or approves the protected action.

## External Evidence Dependency

- Detection signature: Required source lives outside the repo, requires network, requires GitHub UI, requires third-party access, or may have changed recently.
- Immediate classification: `EXTERNAL_EVIDENCE_DEPENDENCY_REVIEW`.
- Approved recovery: Use official/current source if available and allowed, or stop and request owner-provided evidence.
- Forbidden recovery: Invent current external state or use stale screenshots as proof.
- Validator required: Source URL, timestamp, or owner-provided evidence reference.
- Stop condition: External evidence is required and unavailable.
- Failure memory entry: Record external dependency and source status.
- Resume instruction: Resume after evidence is provided or packet scope is narrowed.

## Safety Boundary

- Detection signature: Any request or discovery touches broker/API access, credentials, secrets, trading execution, real orders, money movement, production activation, schedulers, webhooks, daemons, startup persistence, or unapproved runtime mutation.
- Immediate classification: `SAFETY_BOUNDARY_HARD_STOP`.
- Approved recovery: Stop immediately and report the boundary.
- Forbidden recovery: Continue in adjacent files, sanitize by assumption, or transform blocked execution into implementation.
- Validator required: `RISK_POLICY.md` and `AGENTS.md` boundary reference.
- Stop condition: Safety boundary remains in scope.
- Failure memory entry: Record boundary type and source path or prompt segment.
- Resume instruction: Resume only with a new packet that explicitly scopes a safe non-execution review path, if any.

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md`
- `docs/workflows/SAFE_REPAIR_AND_RECOVERY_STANDARD.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
