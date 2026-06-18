# AIOS Live Data Source Gate V1

## Status

Status: REQUIRED_BEFORE_LIVE_MARKET_DISPLAY

Zone: DASHBOARD

Human Owner: Anthony Meza

## Purpose

Prevent fake, fixture, stale, delayed, demo, or mock data from being mistaken for real live market data.

This gate is a dashboard and market-data safety contract only. It does not implement broker/API calls, read secrets, call live data providers, modify dashboard code, place trades, or approve live trading.

## Core Rule

AIOS dashboard market data must always be labeled as one of:

- LIVE_BROKER_PERMITTED
- LIVE_LICENSED_PROVIDER
- DELAYED_PROVIDER
- DEMO_BROKER
- FIXTURE_NOT_LIVE
- STALE
- UNVERIFIED

Unknown or unlabeled market data is unsafe. AIOS must display it as blocked or unverified and must not use it for live trading decisions.

## Dashboard Rule

If data is not live and permitted for trading use, it must be visibly labeled and must not drive live trading decisions.

The dashboard displays truth. The dashboard does not create truth. A visual label cannot upgrade fixture, demo, stale, delayed, or unverified data into live permitted data.

## Allowed Real Data Sources

Allowed real market data sources are:

- broker-permitted market data
- licensed market data provider
- approved delayed provider when clearly labeled delayed

Broker or provider data may be used only according to provider terms. Live trading remains blocked unless all separate governance, risk, secret, broker, P/L truth, auto-exit, and Human Owner approval gates pass.

## Forbidden

AIOS must not treat any of these as live permitted market data:

- unlabeled fixture data
- fantasy/generated market prices
- copied TradingView data for automated trading unless explicitly licensed
- stale prices presented as live
- demo data presented as live
- unverified data driving trade decisions

## Required Data Source Fields

Every dashboard market-data payload or projection intended for operator display must include:

```text
DATA_SOURCE_TYPE:
DATA_SOURCE_NAME:
DATA_SOURCE_PERMISSION:
DATA_TIMESTAMP_UTC:
DATA_STALENESS_SECONDS:
MARKET_DATA_STATUS:
LIVE_TRADING_ALLOWED_FROM_THIS_DATA: true/false
DISPLAY_LABEL:
BLOCK_REASON:
```

`LIVE_TRADING_ALLOWED_FROM_THIS_DATA` may be `true` only when the data source is live, permissioned for the intended use, fresh, labeled, and accepted by future implementation gates. This field alone does not approve live trading.

`BLOCK_REASON` must be populated when the data source is fixture, demo, delayed, stale, unverified, missing, or not permitted for live trading decisions.

## Dashboard Labels

The dashboard may display only these market-data labels:

- LIVE
- DELAYED
- DEMO
- FIXTURE_NOT_LIVE
- STALE
- BLOCKED

Fixture data must be labeled `FIXTURE_NOT_LIVE`. Demo broker data must be labeled `DEMO`. Delayed data must be labeled `DELAYED`. Stale or unverified data must be labeled `STALE` or `BLOCKED`.

## Fail-Closed Rules

AIOS must block live trade decisions if:

- data source is missing
- data source is stale
- data is fixture/mock
- source permission is unknown
- timestamp missing
- provider license unclear
- broker permission unclear
- data label missing

When blocked, the dashboard should show the safest available label, reason, and next action. It must not imply the pair, chart, watchlist, or score is live-tradable.

## Relationship

This gate supports:

- Minimal Operator Dashboard Contract
- Live Watchlist and Pair Discovery Contract
- Secret Persistence Runtime Bridge Contract
- P/L Truth Layer
- Auto Exit Intelligence Gate

This gate does not replace those authorities. It adds a required market-data truth boundary so future watchlist, chart, and dashboard implementation cannot confuse fixture/mock/fantasy data with live permitted market data.

## Future Packets

Future implementation should be separately packetized:

- AIOS-LIVE-DATA-SOURCE-SCHEMA-V1
- AIOS-DASHBOARD-DATA-LABEL-ENFORCEMENT-V1
- AIOS-BROKER-MARKET-DATA-READONLY-BRIDGE-V1
- AIOS-WATCHLIST-LIVE-DATA-ADAPTER-V1

Each future packet must preserve the no-secret, no-broker-call, no-live-trade default boundary unless the Human Owner separately approves a narrower implementation scope.

## Stop Conditions

Stop market-data or dashboard work if:

- source permission cannot be proven
- timestamp or staleness cannot be computed
- fixture, mock, demo, or generated data could be displayed as live
- TradingView or another provider data would be used beyond license terms
- live trading would be implied from a display-only projection
- broker/API calls, secret reads, runtime trading changes, code changes, staging, committing, pushing, or PR creation are requested without separate approval
