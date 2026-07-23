# AIOS Forex Extended Evidence Campaign V1

## Mission

Replace the single 30-trade pass/fail concept with a governed evidence ladder that requires larger, fresher, and more diverse market-demo samples before AIOS can become a production candidate.

## Evidence Ladder

| Tier | Market-demo trades | Distinct days | Walk-forward windows | Minimum profit factor | Maximum drawdown |
|---|---:|---:|---:|---:|---:|
| SYSTEM_MINIMUM | 30 | 5 | 2 | 1.10 | 10% |
| EARLY_CONFIDENCE | 100 | 20 | 4 | 1.15 | 8% |
| STRONG_CONFIDENCE | 300 | 45 | 6 | 1.20 | 7% |
| PRODUCTION_CANDIDATE | 500 | 60 | 8 | 1.25 | 6% |

Every tier also requires positive expectancy, complete trade-level PnL data, complete drawdown evidence, and evidence no older than 14 days.

## Evidence Integrity

The evaluator separates:

- engineering trades;
- fixture or simulation trades;
- unclassified trades;
- genuine market-demo trades.

Fixture, mock, synthetic, and `PAPER_SIMULATION` records remain useful for software testing but do not count toward the market-demo trust ladder.

## Safety Boundary

- Read-only ledger evaluation.
- No broker calls.
- No credential or `.env` access.
- No order placement.
- No automated evidence append.
- No money movement.
- No live trading authority.
- No profitability guarantee.
- Production-candidate status means owner review only.

## Files

- `automation/forex_engine/forex_extended_evidence_campaign_v1.py`
- `tests/forex_engine/test_forex_extended_evidence_campaign_v1.py`
- `scripts/forex_delivery/Get-AiOsExtendedEvidenceVerdict.ps1`
- `Reports/forex_delivery/AIOS_FOREX_EXTENDED_EVIDENCE_CAMPAIGN_V1_REPORT.md`
- `scripts/forex_delivery/Invoke-AiOsDailyForexOrchestrator.ps1` integration

## Validation

Isolated local validation:

```text
python -m pytest tests/forex_engine/test_forex_extended_evidence_campaign_v1.py -q
13 passed
```

Repository CI and full Forex-suite validation remain required before merge.

## Current Ledger Meaning

The existing paper-fixture records do not qualify as genuine market-demo evidence. The campaign must collect fresh owner-supervised OANDA practice records with complete sanitized trade-level results.

## Exact Next Safe Action

Run the extended read-only verdict through the daily orchestrator. Then collect fresh, owner-supervised OANDA practice evidence without bypassing the one-order, owner-approval, risk, receipt, or post-trade review gates.
