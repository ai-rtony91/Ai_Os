# AI_OS Crew Core

Status: foundation APPLY candidate

AI_OS Crew Core is the internal builder crew model for AI_OS. It is a wrapper over the existing orchestration systems, not a replacement for them.

Crew Core routes work through the existing spine:

```text
Task Intake -> Crew Roles -> Work Packet Queue -> Worker Assignment -> File Lock -> DRY_RUN Result -> Approval Inbox -> APPLY Candidate -> Validator -> Commit Package
```

## Existing Systems Used

| Responsibility | Existing system |
| --- | --- |
| Work packets | `automation/orchestration/work_packets/` |
| File locks | `automation/orchestration/locks/` |
| Approval inbox | `automation/orchestration/approval_inbox/` |
| Validators | `automation/orchestration/validators/` |
| Commit packages | `automation/orchestration/commit_packages/` |

## Boundary

Crew Core may inspect, normalize, preview, and recommend. It must not approve APPLY, mutate files, stage files, commit, push, connect brokers, handle API keys, create real webhooks, or place real orders.

Trading Lab Builder is paper-only until a future Human Owner packet changes that boundary.
