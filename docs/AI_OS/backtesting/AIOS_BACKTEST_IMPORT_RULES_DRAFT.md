# AIOS Backtest Import Rules Draft

Status: Draft planning document
Stage: 7

## Purpose

Define rules for importing backtest evidence into AI_OS planning records without enabling execution.

## Required Import Fields

- import_id
- strategy_id
- dataset_name
- dataset_source
- date_range_start
- date_range_end
- market_scope
- timeframe_scope
- assumptions
- fees_spread_slippage_notes
- result_summary_path
- raw_result_path
- validation_status
- known_gaps

## Import Rules

- Import records must identify source evidence.
- Missing values must be UNKNOWN.
- Conflicts with existing records must be marked MISMATCH.
- Unverified imported claims must be marked INVALID DATA.
- Backtest results must not be promoted to live execution.

## Blocked Inputs

- Real broker credentials.
- Live account identifiers.
- Live order records.
- Unredacted private data.
- Claims that cannot be tied to source evidence.

## Future Automation

Future dry-run automation may verify required files and fields, but must not import from live brokers or place trades.
