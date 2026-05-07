# AIOS Strategy Registry Schema Draft

Status: Draft planning document
Stage: 7

## Purpose

Define a draft schema for non-live strategy registry entries used by the signal intelligence layer.

## Required Fields

- strategy_id
- strategy_name
- description
- market_scope
- timeframe_scope
- allowed_signal_inputs
- blocked_signal_inputs
- regime_assumptions
- confluence_model_reference
- validation_rules_reference
- backtest_evidence_status
- paper_trading_status
- approval_status
- known_gaps
- source_evidence_paths

## Status Values

approval_status:

- DRAFT
- NEEDS_REVIEW
- PAPER_TRADING_ONLY
- BLOCKED
- RETIRED

backtest_evidence_status:

- NOT_STARTED
- IMPORT_READY
- IMPORTED_NEEDS_VALIDATION
- VALIDATED
- MISMATCH
- INVALID_DATA

paper_trading_status:

- NOT_ALLOWED
- PAPER_TRADING_ONLY
- PAUSED
- COMPLETE_NEEDS_REVIEW

## Safety Boundary

The strategy registry cannot authorize live execution, broker connectivity, credential use, or order routing.
