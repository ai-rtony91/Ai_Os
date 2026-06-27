# AIOS Failure Memory V1

## Purpose

Define how AIOS records repeatable failures, recovery attempts, prevention rules, and promotion decisions without turning every report or incident into new governance authority.

## Scope

This governance memory applies to AIOS campaign checkpoints, final reports, validator evidence, and future promoted failure entries.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## Operational Failure Memory

Operational Failure Memory lives first in the active packet checkpoint and final report. It records what happened during the current lane so a resumed worker can continue without asking the owner to re-explain state.

Operational entries are evidence only. They do not approve APPLY, protected publishing, workflow changes, automation changes, broker/API access, credential access, trading execution, or production activation.

## Promoted Governance Memory

Promoted Governance Memory is durable doctrine or workflow text created only when a failure is repeatable, high-impact, likely to recur, or safety-relevant.

Promotion must happen through an approved governance/workflow packet. Promotion must update the existing canonical authority when one already owns the topic; it must not create duplicate authority or a parallel governance head.

## Failure Entry Schema

Each failure memory entry must preserve these required fields:

| Field | Requirement |
|---|---|
| `failure_id` | Stable identifier for the incident or pattern. |
| `first_seen` | Date or timestamp when first observed. |
| `source_packet` | Packet ID or `UNKNOWN` if not packet-bound. |
| `lane` | Lane name. |
| `worktree` | Absolute worktree path. |
| `branch` | Current branch when observed. |
| `command_or_action` | Command, validator, edit, or workflow action that exposed the failure. |
| `detection_signature` | Exact phrase, status, validator output, or observed mismatch. |
| `root_cause` | Best verified cause, or `UNKNOWN` if not verified. |
| `recovery_attempted` | What recovery was attempted, including retry count. |
| `recovery_result` | Result such as recovered, blocked, failed, handoff-ready, or no recovery attempted. |
| `validators_after_recovery` | Validation run after recovery or reason validation was blocked. |
| `prevention_rule` | Future prevention rule or classification guidance. |
| `promotion_status` | `operational_only`, `promoted`, `deferred`, `rejected`, or `needs_owner_review`. |

## Promotion Criteria

Promote an operational failure into governance memory only when one or more criteria apply:

- The same failure has occurred in multiple lanes.
- The failure can cause unsafe execution, protected-action confusion, or authority drift.
- The failure blocks long-running campaigns without clear recovery.
- The failure creates repeated owner interruptions.
- The failure causes report feedback loops, stale state, or validator false positives.
- The failure affects branch/worktree preservation, credential safety, broker/API safety, trading safety, or protected publishing.

Do not promote one-off tool noise unless it changes safe execution behavior.

## Anti-Bloat Rule

Failure memory must stay compact and useful. Do not add broad narrative, chat fragments, raw logs, private data, secrets, credentials, broker account data, live payloads, or unrelated terminal output.

If a failure is already covered by an existing playbook, update the playbook only when the prevention rule changes.

## Incident-To-Doctrine Rule

The promotion path is:

```text
incident -> checkpoint entry -> final report entry -> repeated pattern review -> existing authority update -> validation -> protected publishing handoff
```

An incident does not become doctrine by appearing in a report. Reports are evidence. Governance changes require explicit packet authority, allowed paths, validation, and protected publishing approval.

## Example: Windows Sandbox 1312

```text
failure_id: AIOS-FMEM-WIN-1312
first_seen: 2026-06-27
source_packet: AIOS-AEE-LONG-CAMPAIGN-DOCTRINE-AND-OPERATING-LAW-V1
lane: Autonomous Execution Engine Long Campaign Foundation
worktree: C:\Dev\Ai.Os
branch: lane/aios-aee-long-campaign-foundation-v1
command_or_action: read-only directory listing and report-directory creation attempt
detection_signature: CreateProcessAsUserW failed: 1312
root_cause: Windows sandbox process launch failure
recovery_attempted: retried read-only listing once; did not retry write command
recovery_result: recovered by continuing with targeted evidence and file patching
validators_after_recovery: checkpoint updated; final validation pending
prevention_rule: retry read-only inspection at most once; do not retry write or protected commands; hand off required protected actions to owner PowerShell
promotion_status: operational_only
```

## Example: Aggregate Report Re-Ingestion

```text
failure_id: AIOS-FMEM-REPORT-REINGESTION
first_seen: UNKNOWN
source_packet: UNKNOWN
lane: UNKNOWN
worktree: C:\Dev\Ai.Os
branch: UNKNOWN
command_or_action: report review
detection_signature: generated aggregate report treated as source authority
root_cause: report evidence was not separated from canonical authority
recovery_attempted: re-anchor conclusions on current canonical docs
recovery_result: recovered when source precedence is explicit
validators_after_recovery: source-of-truth map review
prevention_rule: aggregate reports are evidence only and must not override root/governance authority
promotion_status: promoted
```

## Example: Account ID Not Included False Positive

```text
failure_id: AIOS-FMEM-ACCOUNT-ID-NOT-INCLUDED
first_seen: UNKNOWN
source_packet: UNKNOWN
lane: Forex evidence or report lane
worktree: C:\Dev\Ai.Os
branch: UNKNOWN
command_or_action: privacy or credential scan
detection_signature: account_id: not included
root_cause: scanner interpreted a negative evidence phrase as a sensitive field finding
recovery_attempted: classify as false positive only after confirming no identifier value is present
recovery_result: recovered with clearer wording and validator note
validators_after_recovery: credential/privacy scan rerun
prevention_rule: negative evidence statements must be phrased so scanners distinguish absence from assignment
promotion_status: operational_only
```

## Example: Dirty Source Worktree Campaign Conflict

```text
failure_id: AIOS-FMEM-DIRTY-WORKTREE-CONFLICT
first_seen: UNKNOWN
source_packet: UNKNOWN
lane: UNKNOWN
worktree: C:\Dev\Ai.Os
branch: non-main or unexpected lane branch
command_or_action: branch preflight
detection_signature: dirty files exist on a branch not matching the packet
root_cause: campaign attempted to start before source worktree ownership was classified
recovery_attempted: stop before branch switch; classify dirty files
recovery_result: owner handoff or isolated worktree decision
validators_after_recovery: git status readback
prevention_rule: never switch away from dirty owner work; use campaign arbitration
promotion_status: promoted
```

## Example: GitHub CI Secret-Assignment Scan Caused By Variable Assignment Names

```text
failure_id: AIOS-FMEM-CI-SECRET-ASSIGNMENT-NAME
first_seen: UNKNOWN
source_packet: UNKNOWN
lane: CI repair lane
worktree: C:\Dev\Ai.Os
branch: UNKNOWN
command_or_action: GitHub CI validation
detection_signature: secret-assignment scan flagged quoted status text near sensitive variable names
root_cause: non-sensitive status example used a sensitive assignment name
recovery_attempted: rename non-sensitive status fields and avoid sensitive assignment examples
recovery_result: recovered after CI passed
validators_after_recovery: GitHub CI checks and local pattern scan
prevention_rule: avoid source/config assignments using exact words api_key, apikey, secret, token, password, or broker with quoted non-placeholder values
promotion_status: promoted
```

## Example: Protected Git Command Routed To Codex After Known Sandbox Failure

```text
failure_id: AIOS-FMEM-PROTECTED-GIT-AFTER-1312
first_seen: UNKNOWN
source_packet: UNKNOWN
lane: protected publishing lane
worktree: C:\Dev\Ai.Os
branch: UNKNOWN
command_or_action: protected Git or GitHub command
detection_signature: protected action requested in Codex after prior 1312 process-launch failure
root_cause: publishing handoff was routed back to a known unreliable process launcher
recovery_attempted: stop and provide owner PowerShell command block
recovery_result: handoff-ready
validators_after_recovery: owner-run status/check output required
prevention_rule: if Codex hits 1312 on protected Git/GitHub actions, move protected publishing to owner PowerShell
promotion_status: promoted
```

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
- `docs/workflows/SAFE_REPAIR_AND_RECOVERY_STANDARD.md`
