# AI_OS Execution Registry Model

## Purpose

The execution registry defines which scripts are trusted, restricted, review-required, legacy, or blocked inside AI_OS V2.

It is the execution authority map for orchestration.

---

# Classification Levels

## ACTIVE

Meaning:
- governed
- trusted
- validated
- approved for operational chain usage

Requirements:
- no hidden mutation
- no unsafe launch behavior
- no unregistered dependency chains
- no legacy repo assumptions
- validator compatible
- topology compliant

ACTIVE must remain minimal.

---

## HELPER

Meaning:
- utility/helper/display/report tooling
- not authoritative execution paths
- safe for operational assistance
- lower trust requirement than ACTIVE

Examples:
- dashboards
- previews
- status viewers
- summaries
- menus
- display helpers

---

## REVIEW_REQUIRED

Meaning:
- behavior unclear
- dependency chain uncertain
- mutation risk not fully audited
- requires deeper inspection before trust elevation

These scripts are quarantined from trusted orchestration paths until reviewed.

---

## BLOCKED

Meaning:
- unsafe
- bypasses governance
- launches uncontrolled runtime behavior
- mutates state unexpectedly
- references blocked dependencies
- violates DRY_RUN expectations

BLOCKED scripts must not participate in governed orchestration flows.

---

## LEGACY

Meaning:
- older architecture
- retained for historical reference
- incompatible assumptions
- outdated repo topology

---

## ARCHIVE

Meaning:
- deprecated
- historical only
- retained for reference
- not operational

---

# Core Principles

- minimal ACTIVE boundary
- fail closed
- explicit approval for mutation
- report-only validators preferred
- no hidden autonomous execution
- no silent worker launch
- no fake DRY_RUN behavior

---

# Long-Term Goal

The registry becomes the enforcement backbone for:
- validator chains
- runtime authorization
- worker execution
- orchestration routing
- future autonomous systems
