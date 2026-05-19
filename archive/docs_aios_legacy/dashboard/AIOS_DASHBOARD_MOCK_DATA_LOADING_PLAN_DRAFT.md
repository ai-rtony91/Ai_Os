# AI_OS Dashboard Mock Data Loading Plan Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.16 - Dashboard Read-Only Mock Status Wiring

## Purpose

Plan how a future dashboard implementation can load local mock-data JSON files for read-only status display.

## Mock Data Mapping

| Dashboard Card | Local Fixture |
| --- | --- |
| Overall status | apps/dashboard/mock-data/aios-status-fixture.example.json |
| Development metrics | apps/dashboard/mock-data/development-metrics-fixture.example.json |
| Phase completion | apps/dashboard/mock-data/phase-completion-fixture.example.json |
| Validator health | apps/dashboard/mock-data/validator-health-fixture.example.json |
| Checkpoint status | apps/dashboard/mock-data/checkpoint-status-fixture.example.json |
| Safety status | apps/dashboard/mock-data/safety-status-fixture.example.json |
| Next action | apps/dashboard/mock-data/next-action-fixture.example.json |
| Progress ledger | apps/dashboard/mock-data/progress-ledger-fixture.example.json |

## Loading Rules

- Load local JSON only.
- Parse JSON defensively.
- Render fallback text for missing or malformed files.
- Do not write data back to disk.
- Do not call network APIs.
- Do not read secrets or broker data.

## Error States

- UNKNOWN for missing fixture.
- INVALID DATA for malformed JSON.
- STALE for outdated fixture evidence.
- MISMATCH for conflicting fixture values.

