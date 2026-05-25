# AI_OS DRY_RUN Contract

## Purpose

DRY_RUN mode exists to guarantee safe preview execution without mutation, launch, routing, persistence, commit activity, or autonomous behavior.

DRY_RUN must simulate only.

---

# DRY_RUN Rules

A DRY_RUN script must NEVER:

- write files
- modify files
- delete files
- launch workers
- launch terminals
- mutate queues
- mutate runtime memory
- route packets
- create commits
- push branches
- open pull requests
- invoke APPLY-only execution paths
- perform hidden side effects

---

# Allowed DRY_RUN Behavior

DRY_RUN scripts MAY:

- inspect state
- validate topology
- validate configuration
- preview planned actions
- generate report-only output
- simulate routing
- simulate mutation
- print execution plans
- emit WARN or STOP findings

---

# Required DRY_RUN Output

Every DRY_RUN script should clearly report:

- mode
- scope
- inspected targets
- simulated actions
- validation findings
- mutation risk
- blocked dependencies
- next safe action

---

# Fail-Closed Principle

If uncertainty exists:
- STOP
- do not mutate
- require explicit APPLY approval

---

# Long-Term Goal

All AI_OS DRY_RUN scripts become:
- deterministic
- report-only
- validator compatible
- governance-safe
- automation-safe
