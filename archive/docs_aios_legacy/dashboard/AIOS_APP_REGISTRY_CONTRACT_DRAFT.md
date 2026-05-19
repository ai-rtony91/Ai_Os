# AI_OS App Registry Contract Draft

## Purpose

The App Registry defines how future AI_OS apps or panels are proposed, reviewed, validated, approved, and added through generated work packets.

This contract is static/planning only and does not create live app behavior.

## App Registry Fields

- `app_name`: App or panel name.
- `app_purpose`: Operator-facing purpose.
- `allowed_files`: Files or folders the packet may create or edit after approval.
- `blocked_actions`: Actions that remain prohibited.
- `required_approvals`: Human approvals required before APPLY, commit, publishing, or activation.
- `tools_needed`: Tool Registry entries needed for the packet.
- `validation_commands`: Commands required before commit.
- `preview_command`: Command to visually inspect the static result.
- `rollback_plan`: How to recover if the approved change fails.
- `risk_level`: LOW, MEDIUM, HIGH, or BLOCKED.
- `status`: PASS, REVIEW, NEEDS_REFACTOR, BLOCKED, or INVALID DATA.
- `notes`: Additional boundaries or dependencies.

## App Categories

Initial candidate app categories:

- Calendar
- Notes
- Reports
- Telemetry
- Dashboard Panels
- Admin/Settings
- Trading Readiness Panel

## Approval Rules

Each app packet must define exact allowed files before APPLY. Any protected root file change, credential access, backend/API call, service-worker registration, persistence, broker/trading automation, live order path, delete, move, rename, or overwrite requires separate explicit approval.

## Validation Rules

Every future app packet should include:

- git status check
- exact target file existence check
- path allowlist check
- JSON parse check when JSON is created
- unsafe keyword scan
- preview command when visual UI changes
- final git status check

## Trading Readiness Boundary

Trading-related panels may display readiness, blocked status, paper-review labels, or educational context only. They must not place orders, route orders, approve orders, access broker credentials, or touch a live order path.

## Safety Boundary

The App Registry grants no approval to activate apps, connect APIs, persist data, register service workers, edit protected root files, or touch broker/trading automation.
