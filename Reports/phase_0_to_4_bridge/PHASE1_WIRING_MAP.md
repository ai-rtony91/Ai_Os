# Phase 1 Wiring Map

Status: evidence, not authority.

## SUMMARY

Bridge adapters read existing queue, approval, lock, and validator surfaces without replacing them.

## SYSTEMS WIRED

- `read-only queue inventory`
- `read-only approval inventory`
- `validator discovery`

## SYSTEMS LEFT DOC ONLY

- `hook installation`
- `CI enforcement hardening`
- `Night Supervisor activation`

## SYSTEMS REQUIRING APPROVAL

- `commit`
- `push`
- `merge`
- `protected root edits`

## SAFE NEXT ACTION

Run python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .
