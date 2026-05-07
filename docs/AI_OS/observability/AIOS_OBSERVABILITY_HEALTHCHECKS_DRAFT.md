# AIOS Observability Healthchecks Draft

Status: Draft scaffold

## Purpose

Define observability and health-check planning for AI_OS production readiness.

## Candidate Health Checks

- Repo clean status.
- Required folder presence.
- Required README_FOLDER_PURPOSE coverage.
- Documentation index coverage.
- Dry-run validator status.
- Dashboard build status.
- Report and checkpoint freshness.
- Secret exclusion status.

## Monitoring Boundaries

- Local-first by default.
- No production telemetry endpoint until approved.
- No user tracking without consent and retention rules.
- No broker telemetry from live accounts.
