# AI-OS UI Spec (V1)

## Purpose
AI-OS UI is the control plane: visibility, approvals, logs, and orchestration control.

## Form factor
Web dashboard (browser) as V1.

## Screens (V1)
1) Dashboard
- System status: Idle / Planning / Awaiting Approval / Executing / Error
- Active agents list
- Running workflows list
- Pending approvals count

2) Workflow View
- Timeline of steps: Planned -> Awaiting Approval -> Executing -> Completed/Failed
- Each step shows: agent, action, status, timestamps, output

3) Approvals
- Queue of requested actions
- Approve / Deny / Modify (optional later)
- Reason required for Deny

4) Logs
- Filter by agent/workflow
- Timestamped
- Plain text first (no charts)

## Layout
Top bar: status + environment + emergency stop
Left nav: Dashboard / Workflows / Approvals / Logs / Settings
Main: selected view
Right panel: inspector (details + raw logs + approval actions)

## Non-goals (V1)
- Voice UI
- Drag/drop builders
- Multi-user RBAC UI (later)

## Standardization

- UI follows pipeline stages exactly
- Status labels must match: Idle / Planning / Awaiting Approval / Executing / Completed / Error
- All actions require audit logging
- Approvals must block execution
