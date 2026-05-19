# AI_OS Calendar App Static Packet Example Draft

## Purpose

This draft shows how a future Calendar App could be proposed through the App Registry and displayed on the Work Table.

The Calendar App example is static/planning only. It does not connect Google Calendar, Microsoft Graph, Outlook, CalDAV, browser profiles, local account data, credentials, notifications, background sync, persistence, broker systems, or trading automation.

## Calendar App Purpose

The Calendar App would show local planning dates, stage checkpoints, review reminders, and operator tasks using static placeholder data first.

## Example App Packet

- `app_name`: Calendar
- `app_purpose`: Show static planning dates, checkpoint reminders, and operator task windows.
- `allowed_files`: `apps/dashboard/mock-data/calendar-fixture.example.json`, future approved dashboard UI files.
- `blocked_actions`: no backend, no API calls, no credentials, no OAuth, no persistence, no service-worker registration, no notifications, no startup task, no broker/trading automation, no live order path.
- `required_approvals`: DRY_RUN packet approval, APPLY approval, validator pass, visual confirmation, commit approval.
- `tools_needed`: Codex, PowerShell, GitHub after approval, Reports only if a future report packet is approved.
- `validation_commands`: JSON parse, unsafe keyword scan, git status.
- `preview_command`: `Start-Process ".\\apps\\dashboard\\AIOS_STATIC_PREVIEW.html"`
- `rollback_plan`: revert only the approved Calendar App files after explicit human approval.
- `risk_level`: LOW for static fixture/docs; REVIEW for UI integration; BLOCKED for real calendar API integration.
- `status`: REVIEW.

## Example Workflow

1. Human proposes Calendar App.
2. Work Table displays Calendar packet fields.
3. Tool Registry confirms required tools and boundaries.
4. App Registry confirms allowed files and blocked actions.
5. Codex produces DRY_RUN plan.
6. Human approves APPLY.
7. Codex creates static fixture/docs only.
8. Validator confirms JSON parse, no unsafe calls, no credentials, no persistence, and no trading automation.
9. Human visually confirms any UI change.
10. Git commit/push happens only after approval.

## Missing Evidence

- Final Calendar UI placement is not approved.
- No production calendar provider is selected.
- No real date source is approved.
- No persistence model is approved.

## Safety Boundary

No backend, API call, credential, persistence, service-worker registration, broker/trading automation, or live order path is approved by this example.
