# CLI Everything Evidence Contract

Status: APPLY REPORT - evidence contract draft, not source authority.
Packet ID: CLI_EVERYTHING_EVIDENCE_CONTRACT_APPLY_002
Lane: CLI_EVERYTHING_CORE_SPINE
Worker: Codex CLI Worker
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os

## Purpose

Define the shared evidence envelope every CLI Everything party must emit before AI_OS builds more CLI command surfaces, dashboards, validators, approval gates, relay items, or SOS events.

This report creates no source code, scripts, automation, protected authority edits, commits, pushes, broker paths, live trading behavior, or secrets.

## Source Reports Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/cli_everything/CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION.md`
- `Reports/cli_everything/CLI_EVERYTHING_EXISTING_WORKFLOW_GAP_CHECK.md`

## Contract Rules

1. Every CLI party emits evidence before action claims.
2. Evidence is not approval.
3. Validator PASS is evidence only.
4. Dashboard, telemetry, reports, bridge state, relay items, and notifications are not approval authority.
5. `executable=false` is default unless a separately approved packet explicitly authorizes execution.
6. Protected actions remain blocked until current-session Human Owner approval and protected-action gate evidence exist.
7. Secrets, broker/API paths, live trading, real orders, real webhooks, and credential handling remain blocked.
8. Display alerts do not wake Anthony unless `sos_wake_required=true`.

## Universal Evidence Envelope

Every CLI party should emit one JSON-compatible envelope with these fields:

| Field | Required | Meaning |
|---|---:|---|
| `schema` | yes | Stable schema name, e.g. `AIOS_CLI_EVIDENCE.v1`. |
| `event_id` | yes | Unique event ID for deduplication and replay protection. |
| `created_at_utc` | yes | UTC timestamp in ISO-8601 format. |
| `source_party` | yes | Party/layer that emitted the evidence. |
| `source_command` | yes | Command or mode requested, with secrets redacted. |
| `packet_id` | conditional | Required for packet-driven work. |
| `lane` | conditional | Required for worker, validator, queue, approval, and repo tasks. |
| `mode` | yes | One of the approved mode values. |
| `repo_root` | conditional | Required when repo state matters. |
| `branch` | conditional | Required when repo state matters. |
| `worktree` | conditional | Required when repo state matters. |
| `git_status_short_branch` | conditional | Current git status evidence when repo state matters. |
| `dirty_state_class` | conditional | `CLEAN`, `REPORT_ONLY_UNTRACKED`, `DIRTY_TRACKED`, `DIRTY_UNTRACKED_UNSAFE`, or `UNKNOWN`. |
| `allowed_paths` | conditional | Required for any filesystem-scoped task. |
| `forbidden_paths` | conditional | Required for any filesystem-scoped task. |
| `read_paths` | recommended | Files read as evidence. |
| `write_paths` | conditional | Files created or modified, if any. |
| `input_hashes` | recommended | Hashes for packets, task files, or source evidence. |
| `output_paths` | recommended | Report, telemetry, queue, manifest, or result paths. |
| `status` | yes | Current event status from the status vocabulary. |
| `status_impact` | yes | Whether this status affects top-level system state. |
| `blocked_reasons` | yes | Empty list when not blocked. |
| `risk_flags` | yes | Empty list when no risk flags apply. |
| `validator_chain` | conditional | Required when validators apply. |
| `validator_results` | conditional | Required when validators run or are skipped. |
| `approval_required` | yes | Boolean. |
| `approval_status` | yes | Approval status vocabulary value. |
| `protected_action_requested` | yes | Boolean. |
| `protected_action_type` | conditional | Required when a protected action is requested. |
| `display_alert` | yes | Boolean for UI/display visibility. |
| `sos_wake_required` | yes | Boolean for true wake/interruption. |
| `wake_class` | yes | `NONE`, `DISPLAY_ONLY`, `REVIEW_ONLY`, or `SOS`. |
| `redaction_status` | yes | Redaction/no-secret state. |
| `executable` | yes | Default `false`; true only under separately approved execution policy. |
| `next_safe_action` | yes | One concrete safe next action. |
| `stop_point` | yes | Where processing stops. |

## Status Vocabulary

Approved primary status values:

- `READY`
- `PREVIEW`
- `DRY_RUN_COMPLETE`
- `APPLY_COMPLETE`
- `VALIDATION_PASSED`
- `VALIDATION_FAILED`
- `NEEDS_APPROVAL`
- `BLOCKED`
- `FAILED`
- `SKIPPED`
- `STALE`
- `SUPERSEDED`
- `UNKNOWN`

Approved `status_impact` values:

- `CURRENT_ACTIVE`
- `CURRENT_DETAIL_ONLY`
- `HISTORICAL_DETAIL_ONLY`
- `NO_STATUS_IMPACT`

Rule: historical reports, stale relay artifacts, examples, completed approvals, and old errors must not drive top-level status unless explicitly promoted by current evidence.

## Display Alert vs SOS Wake Rules

`display_alert=true` means the event should be visible to an operator surface.

`sos_wake_required=true` means Anthony should be interrupted because AI_OS cannot safely continue or protected approval is required.

| Condition | display_alert | sos_wake_required | wake_class |
|---|---:|---:|---|
| Routine success | false | false | `NONE` |
| Routine summary or digest | true | false | `DISPLAY_ONLY` |
| Recommendation-only approval visibility | true | false | `REVIEW_ONLY` |
| Missing protected-action approval | true | true | `SOS` |
| Validator failure blocking continuation | true | true | `SOS` |
| Invalid executable packet | true | true | `SOS` |
| Branch/worktree mismatch blocking task | true | true | `SOS` |
| Forbidden path or secret risk | true | true | `SOS` |
| Broker/API/live trading risk | true | true | `SOS` |
| Tool or sandbox failure blocking task | true | true | `SOS` |

Rule: `NEEDS_APPROVAL` is not automatically SOS. It becomes SOS only when continuation is blocked or a protected action needs explicit Anthony approval.

## Approval Evidence Fields

Approval-capable events must include:

- `approval_required`
- `approval_status`
- `approval_authority`
- `approval_scope`
- `approval_decision_id`
- `approval_decision_path`
- `approval_created_at_utc`
- `approval_expires_at_utc`
- `approval_consumed_at_utc`
- `approval_replay_protection`
- `approval_matches_packet`
- `approval_matches_allowed_paths`
- `approval_matches_protected_action`

Approved approval status values:

- `NOT_REQUIRED`
- `REQUIRED`
- `PENDING`
- `APPROVED`
- `REJECTED`
- `EXPIRED`
- `MALFORMED`
- `MISMATCHED`
- `CONSUMED`
- `UNKNOWN`

Rule: approval for one action never transfers to another action.

## Validation Evidence Fields

Validator events must include:

- `validator_chain`
- `validator_results`
- `validator_status`
- `validator_command`
- `validator_exit_code`
- `validator_output_path`
- `validator_skipped_reason`
- `validated_paths`
- `validation_covers_changed_files`
- `validation_timestamp_utc`

Approved validator status values:

- `NOT_REQUIRED`
- `PENDING`
- `PASSED`
- `FAILED`
- `SKIPPED`
- `PARTIAL`
- `UNKNOWN`

Rule: `PASSED` proves only that the validator passed. It does not approve APPLY, commit, push, merge, PR creation, protected edits, or production behavior.

## Protected-Action Evidence Fields

Protected-action review events must include:

- `protected_action_requested`
- `protected_action_type`
- `protected_action_command_preview`
- `protected_action_scope`
- `protected_action_files`
- `protected_action_branch`
- `protected_action_remote`
- `protected_action_pr`
- `human_approval_required`
- `human_approval_present`
- `validator_evidence_present`
- `cached_diff_reviewed`
- `blocked_paths_touched`
- `risk_flags`
- `protected_action_decision`

Protected action types:

- `GIT_ADD`
- `GIT_COMMIT`
- `GIT_PUSH`
- `GH_PR_CREATE`
- `GH_PR_MERGE`
- `GIT_MERGE`
- `GIT_RESET`
- `GIT_CLEAN`
- `BRANCH_DELETE`
- `PROTECTED_FILE_EDIT`
- `SECRET_OR_CREDENTIAL_ACTION`
- `BROKER_API_OR_LIVE_TRADING_ACTION`
- `SCHEDULER_SERVICE_OR_DAEMON_ACTION`

Protected action decisions:

- `NOT_REQUESTED`
- `BLOCKED`
- `HUMAN_APPROVAL_REQUIRED`
- `SAFE_TO_PRESENT`
- `SAFE_TO_COMMIT`
- `SAFE_TO_PUSH`
- `REJECTED`

Rule: `SAFE_TO_PRESENT` is not approval to execute.

## No-Secret and Redaction Rules

Every evidence envelope must include:

- `redaction_status`
- `secret_scan_status`
- `secret_values_present`
- `secret_values_redacted`
- `external_transmission`
- `private_evidence_included`
- `broker_or_api_credential_reference`

Approved redaction status values:

- `NO_SECRETS_DETECTED`
- `REDACTED`
- `SECRET_RISK_BLOCKED`
- `NOT_SCANNED`
- `UNKNOWN`

Rules:

- Do not print plaintext API keys, tokens, passwords, seed phrases, private keys, broker credentials, account IDs, or live trading credentials.
- Presence checks may report only that a credential exists or does not exist.
- External API/MCP use must be read-first, scoped, redacted, and separately approved when it sends private evidence.
- Raw private local evidence must not be imported into repo telemetry without explicit approval.

## Trading Lab Paper-Only Evidence

Any Trading Lab event must include:

- `paper_only`
- `broker_path_touched`
- `api_key_used`
- `real_order_requested`
- `real_webhook_requested`
- `live_execution_path`
- `paper_ledger_path`
- `paper_validator_status`

Required safe values:

- `paper_only=true`
- `broker_path_touched=false`
- `api_key_used=false`
- `real_order_requested=false`
- `real_webhook_requested=false`
- `live_execution_path=false`

Rule: any broker/API/live order/real webhook signal sets `status=BLOCKED`, `display_alert=true`, and `sos_wake_required=true`.

## Example Envelope Skeleton

```json
{
  "schema": "AIOS_CLI_EVIDENCE.v1",
  "event_id": "AIOS-EVENT-000000",
  "created_at_utc": "2026-06-07T00:00:00Z",
  "source_party": "Codex East",
  "source_command": "aios status --read-only",
  "packet_id": "",
  "lane": "CLI_EVERYTHING_CORE_SPINE",
  "mode": "READ_ONLY",
  "repo_root": "C:\\Dev\\Ai.Os",
  "branch": "feature/full-operator-relief-closed-loop-v1",
  "worktree": "C:\\Dev\\Ai.Os",
  "dirty_state_class": "REPORT_ONLY_UNTRACKED",
  "allowed_paths": [],
  "forbidden_paths": [],
  "read_paths": [],
  "write_paths": [],
  "output_paths": [],
  "status": "READY",
  "status_impact": "CURRENT_ACTIVE",
  "blocked_reasons": [],
  "risk_flags": [],
  "validator_chain": [],
  "validator_results": [],
  "approval_required": false,
  "approval_status": "NOT_REQUIRED",
  "protected_action_requested": false,
  "protected_action_type": "",
  "display_alert": false,
  "sos_wake_required": false,
  "wake_class": "NONE",
  "redaction_status": "NO_SECRETS_DETECTED",
  "executable": false,
  "next_safe_action": "Create read-only CLI inventory command report.",
  "stop_point": "Stop after evidence emission."
}
```

## Exact Next APPLY Packet Recommendation

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
ChatGPT Chief Orchestrator

PACKET ID:
CLI_EVERYTHING_READ_ONLY_INVENTORY_REPORT_APPLY_001

LANE:
CLI_EVERYTHING_CORE_SPINE

ZONE:
CLI Everything / Read-Only Inventory / Report

WORKER IDENTITY:
Codex CLI Worker

MODE:
APPLY

BRANCH:
feature/full-operator-relief-closed-loop-v1

WORKTREE:
C:\Dev\Ai.Os

APPROVAL AUTHORITY:
Anthony / AI_OS Owner / Human Approval Authority

ALLOWED PATHS:
Reports/cli_everything/

PROTECTED AUTHORITY PATHS:
AGENTS.md
README.md
WHITEPAPER.md
docs/governance/
docs/AI_OS/governance/
automation/
tools/
scripts/
tests/
src/
config/
control/
Relay/
.github/

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md if present.
4. Read Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md.
5. Create only Reports/cli_everything/CLI_EVERYTHING_READ_ONLY_INVENTORY_COMMANDS.md.
6. Define read-only command targets for status, queue, approvals, bridge, reports, validators, notifications, and Trading Lab paper status.
7. Ensure every command emits the evidence envelope and remains executable=false.
8. Run git diff --check.
9. Report git status --short --branch.

STOP POINT:
Stop after report creation and validation. No commit. No push. No source edits. No scripts. No automation creation.

MISSION:
Define the read-only CLI inventory command report that follows the CLI Everything evidence contract before implementation.

STRICT RULES:
- Report only.
- No source code changes.
- No scripts.
- No commits.
- No pushes.
- No protected authority file edits.
- No live trading paths.
- No broker paths.
- No secrets.
- No automation creation.
- Do not switch branches.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

## Final Finding

The CLI loop should close around evidence first: every party emits the same envelope, every status has the same meaning, display-only alerts do not wake Anthony, SOS is reserved for blocked continuation or protected approval, and protected actions remain human-approved.
