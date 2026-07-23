# AIOS Forex Extended Evidence Campaign V1 Validation

## Isolated Validation

Command:

```text
python -m pytest tests/forex_engine/test_forex_extended_evidence_campaign_v1.py -q
```

Result:

```text
13 passed in 0.08s
```

## Scope

The isolated validation covered missing and invalid ledgers, fixture exclusion, stale evidence, incomplete metrics, safety violations, insufficient samples, all four evidence tiers, low profit factor, and explicit live/profit-approval exclusions.

## Remaining Validation

Repository CI and the full Forex test suite must pass before merge.
