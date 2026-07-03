# AIOS Daily Forex Orchestrator V1

## Purpose

Adds a governed daily Forex validation orchestrator for AIOS in GitHub Actions and Codespaces.

## Schedule

Runs daily at 01:17 UTC and supports manual workflow_dispatch.

## Behavior

V1 is artifact-only. It uses read-only repository permissions, runs validation, writes reports to workflow artifacts, and does not push commits or open PRs.

## Clean Status Gate

The orchestrator blocks unresolved dirty worktree state before validation stages.

## Validation

- python -m pytest tests/forex_engine/test_demo_day_evidence_runner_v11_script.py -q
- pwsh -NoProfile -File scripts/forex_delivery/Get-AiOsDemoVerdict.ps1
- git diff --check

## Evidence Control

The workflow detects whether today’s UTC evidence exists but does not append evidence automatically.

## Safety Blocks

No broker calls, no live orders, no credential access, no .env reads, no money movement, no automatic evidence append, no automatic merge, and no trading authority expansion.

## Remaining Owner Action

Merge through PR, then allow the first scheduled/manual GitHub Actions run to produce an artifact report.
