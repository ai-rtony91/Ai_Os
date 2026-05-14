# Phase 15.3.4 Validator Chain Automation

## Purpose

The validator chain creates one repeatable safety check path for AI_OS orchestration work.

Before APPLY, commit, or push, the operator and workers need the same answer:

- Is the repo state visible?
- Are changed files inside approved paths?
- Are blocked and protected paths untouched?
- Do JSON and PowerShell files parse?
- Are secrets and live trading enablement absent?
- Is human approval present for the requested stage?
- Is exact-file commit packaging ready?

## Why The Validator Chain Matters

Multi-worker work can move quickly, but speed creates risk when workers edit overlapping paths, miss dirty files, or assume approval exists.

The chain reduces that risk by making the required checks explicit and ordered. A worker does not need to remember every safety rule manually; the chain becomes the standard checklist.

## How It Reduces Manual Checking

The first implementation is DRY_RUN only.

It can:

- load the validator config
- print the repo root
- print the config path
- read `git status --short --branch`
- parse changed JSON files
- parse changed PowerShell files
- confirm required Markdown files exist
- flag blocked paths and sensitive path names
- remind the operator that approval and commit package review are required

It cannot:

- edit files
- stage files
- commit
- push
- install dependencies
- call external services
- create startup tasks
- create scheduled tasks
- connect to brokers
- enable live trading

## Why Failed Validators Stop Progress

Failed validators block progress because they indicate the package is not safe to promote.

Examples:

- invalid JSON can break runtime readers
- invalid PowerShell can fail later execution
- blocked path changes can violate the approved scope
- protected file changes can alter governance unexpectedly
- secret or API key paths can expose credentials
- live trading enablement can violate the paper-only safety boundary
- missing approval can turn planning work into unauthorized APPLY work

When any of these fail, commit and push must stop until the operator reviews the failure.

## Support For Safe Multi-Worker Automation

The validator chain supports parallel Codex workers by creating shared rules:

- every worker uses the same validator names
- every packet can require the same chain before APPLY
- every commit package can require exact-file review
- every push remains human-controlled
- warnings are visible before they become conflicts

This helps keep GitHub main clean while allowing separate worker branches and future friend C-drive clones to work safely through Git.

## Human Control

The validator chain does not replace the operator.

It reports `PASS`, `WARN`, or `FAIL`. The operator decides whether to approve APPLY, commit, or push after reviewing the evidence.

## Next Safe Action

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-ValidatorChainConfig.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1
```

