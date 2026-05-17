# Codex Tasks - Mission Control Safe Apply Test

Goal: Validate Mission Control safe generation

Copy one prompt at a time into Codex. Each worker must start in DRY_RUN.

## MC-01 - Convert goal into scoped work packet

```text
Task ID: MC-01
Mode: DRY_RUN first, APPLY only after explicit approval.
Goal: Validate Mission Control safe generation
Worker lane: mission-planner
Objective: Convert goal into scoped work packet
Allowed paths: repo-scoped paths explicitly approved by the mission plan.
Blocked paths: .aios_local_backup, protected root governance files unless approved, secrets, broker paths, live trading paths, startup tasks, scheduled tasks.
Validation: run relevant parser/check commands and git diff --check after changes.
Required report: files inspected, files created, files changed, validation result, git status, commit status, push status, blockers, next safe action.
```

## MC-02 - Implement approved mission slice

```text
Task ID: MC-02
Mode: DRY_RUN first, APPLY only after explicit approval.
Goal: Validate Mission Control safe generation
Worker lane: implementation-lane
Objective: Implement approved mission slice
Allowed paths: repo-scoped paths explicitly approved by the mission plan.
Blocked paths: .aios_local_backup, protected root governance files unless approved, secrets, broker paths, live trading paths, startup tasks, scheduled tasks.
Validation: run relevant parser/check commands and git diff --check after changes.
Required report: files inspected, files created, files changed, validation result, git status, commit status, push status, blockers, next safe action.
```

## MC-03 - Validate mission outputs and safety boundaries

```text
Task ID: MC-03
Mode: DRY_RUN first, APPLY only after explicit approval.
Goal: Validate Mission Control safe generation
Worker lane: validator-lane
Objective: Validate mission outputs and safety boundaries
Allowed paths: repo-scoped paths explicitly approved by the mission plan.
Blocked paths: .aios_local_backup, protected root governance files unless approved, secrets, broker paths, live trading paths, startup tasks, scheduled tasks.
Validation: run relevant parser/check commands and git diff --check after changes.
Required report: files inspected, files created, files changed, validation result, git status, commit status, push status, blockers, next safe action.
```

## MC-04 - Update mission dashboard and proof checklist

```text
Task ID: MC-04
Mode: DRY_RUN first, APPLY only after explicit approval.
Goal: Validate Mission Control safe generation
Worker lane: dashboard-and-proof-lane
Objective: Update mission dashboard and proof checklist
Allowed paths: repo-scoped paths explicitly approved by the mission plan.
Blocked paths: .aios_local_backup, protected root governance files unless approved, secrets, broker paths, live trading paths, startup tasks, scheduled tasks.
Validation: run relevant parser/check commands and git diff --check after changes.
Required report: files inspected, files created, files changed, validation result, git status, commit status, push status, blockers, next safe action.
```

