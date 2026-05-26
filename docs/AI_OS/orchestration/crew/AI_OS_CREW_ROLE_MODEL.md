# AI_OS Crew Role Model

## Crew Roles

| Role | Purpose | Output | Must not do |
| --- | --- | --- | --- |
| Crew Dispatcher | Receives a human goal and routes it into task intake. | Task intake preview | Approve APPLY or bypass packets |
| Packet Builder | Converts task intake into a work packet candidate. | Work packet preview | Mutate active packet state without approval |
| File Lock Manager | Checks assigned paths against lock policy. | Lock recommendation | Claim or release locks without approval |
| DRY_RUN Worker | Produces a report-only implementation preview. | DRY_RUN result | Edit files or run APPLY |
| Validator Runner | Selects and runs approved validators. | Validator evidence | Treat validation as approval |
| Approval Inbox Manager | Prepares approval request metadata. | Approval inbox preview | Approve its own request |
| Commit Package Builder | Builds exact selective staging preview. | Commit package preview | Stage files or use `git add .` |
| Trading Lab Builder | Designs paper-only Trading Lab work. | Paper-only task preview | Add broker, OANDA, API-key, real-money, or live-order logic |

## Assignment Rule

One packet maps to one worker for one bounded path set. Shared paths require explicit lock review, approval routing, and validator selection before APPLY.

## Authority Rule

Human Owner approval is required before APPLY. Validators are evidence only. Commit and push require separate approval after validation and exact-file package review.
