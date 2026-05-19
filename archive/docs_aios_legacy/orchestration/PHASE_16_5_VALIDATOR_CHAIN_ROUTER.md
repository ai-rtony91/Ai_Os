# Phase 16.5 Validator Chain Router

## Purpose

Phase 16.5 adds a read-only validator chain display for AI_OS orchestration work.

The validator chain helps an operator review validator order before deciding what checks to run in a separate approved workflow.

## Files Added

- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/show-validator-chain.ps1`
- `docs/AI_OS/orchestration/PHASE_16_5_VALIDATOR_CHAIN_ROUTER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_5_VALIDATOR_CHAIN_ROUTER.md`

## Script Behavior

`show-validator-chain.ps1` reads:

- `automation/orchestration/validator_chain.example.json`

It prints:

- validator order
- required validators
- optional validators
- blocked validator status

## Safety Boundary

This phase is display-only.

It does not:

- run validators
- create files during display
- modify files during display
- launch workers
- edit dashboard files
- connect to a broker
- connect to OANDA
- use API keys
- place orders
- enable live trading
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-validator-chain.ps1
git status --short --branch
```

Expected result:

- The script prints validator order.
- The script prints required and optional validators.
- The script prints blocked validator status.
- The script completes without running validators, changing files, or launching workers.

## Next Safe Action

Review the validator chain display and checkpoint, then decide whether to approve a separate selective commit prompt.
