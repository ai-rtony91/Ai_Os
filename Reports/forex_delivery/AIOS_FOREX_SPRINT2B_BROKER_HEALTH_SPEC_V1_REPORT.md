# AIOS Forex Sprint2B Broker Health Spec V1 Report

## Packet

- Packet ID: `AIOS-FOREX-SPRINT2B-BROKER-HEALTH-SPEC-V1`
- Future implementation ID: `AIOS-FOREX-BROKER-HEALTH-READONLY-IMPLEMENTATION-V1`
- Mode: `APPLY`
- Zone: `Reports Only`
- Lane: `Forex Broker Health Read-Only Implementation Spec`
- Created file: `Reports/forex_delivery/AIOS_FOREX_SPRINT2B_BROKER_HEALTH_SPEC_V1_REPORT.md`
- Report type: implementation specification only
- Runtime posture: no code changed, no tests changed, no schemas changed, no broker access

## 1. Purpose

Define a collision-free implementation specification for a deterministic read-only Forex broker health evaluator.

The future evaluator must classify sanitized local broker evidence before any supervised demo review stage consumes it. It must answer one narrow question:

```text
Is this sanitized broker-read snapshot healthy enough for read-only review handoff?
```

It must not approve trades, place trades, size positions, modify capital allocation, unlock demo execution, call brokers, read credentials, persist account identifiers, or override existing AIOS governance gates.

## 2. Scope

The future implementation should evaluate only already-sanitized local input. It should combine health signals for:

- spread availability and spread severity.
- price freshness.
- observed read latency.
- market-open state.
- requested instrument availability and tradeability.
- read-only permission boundary.
- account identifier rejection and redaction.
- no-network and no-broker-call guarantees.

The evaluator should be implemented as a pure local Python module with no file reads by default and no runtime side effects.

Recommended future module:

```text
automation/forex_engine/broker_health_readonly_v1.py
```

Recommended future test file:

```text
tests/forex_engine/test_broker_health_readonly_v1.py
```

Recommended future delivery report:

```text
Reports/forex_delivery/AIOS_FOREX_BROKER_HEALTH_READONLY_IMPLEMENTATION_V1_REPORT.md
```

## 3. Non-goals

This evaluator must not:

- connect to OANDA or any broker.
- call any broker API.
- read `.env`, process environment variables, credential stores, vaults, or secret files.
- submit, preview, amend, cancel, route, or approve orders.
- determine strategy quality or candidate ranking.
- determine risk budget or capital allocation.
- replace `broker_read_only_snapshot_contract_v1.py`.
- replace `demo_connector_readonly.py`.
- replace `candidate_scoring_v1.py`.
- create a live-trading exception.
- persist raw broker payloads.
- store or echo account identifiers.

## 4. Sanitized Input Contract

The future evaluator should accept a single mapping plus optional config:

```python
evaluate_broker_health_readonly(snapshot: Mapping[str, Any] | None, *, config: BrokerHealthConfig | None = None) -> BrokerHealthResult
```

Required sanitized snapshot fields:

```text
schema_version: string
source: string
sanitized: bool
account_present: bool
account_reference: string
instrument: string
instrument_tradeable: bool
instrument_available: bool
market_hours_open: bool
bid: decimal-compatible string or number
ask: decimal-compatible string or number
spread: decimal-compatible string or number
spread_present: bool
price_timestamp_utc: ISO-8601 string or epoch seconds
read_timestamp_utc: ISO-8601 string or epoch seconds
evaluation_timestamp_utc: ISO-8601 string or epoch seconds
latency_ms: integer or decimal-compatible number
read_only_reconciled: bool
permissions: mapping
blocked_reasons: list[string]
warnings: list[string]
```

Optional sanitized snapshot fields:

```text
mid: decimal-compatible string or number
price_age_seconds: integer or decimal-compatible number
max_allowed_spread_pips: decimal-compatible string or number
max_price_age_seconds: integer or decimal-compatible number
max_latency_ms: integer or decimal-compatible number
account_summary_present: bool
open_trades_present: bool
open_positions_present: bool
pending_orders_present: bool
last_transaction_id_present: bool
no_unknown_open_exposure: bool
broker_name: string
environment: string
```

Input must already be sanitized. If `sanitized` is not exactly `True`, the evaluator must block.

Account reference rule:

```text
Only DEMO_ACCOUNT_REFERENCE_PRESENT is accepted as account_reference.
Any other non-empty account_reference is treated as a real or unsafe identifier and must block.
```

The evaluator may accept data produced by existing snapshot/connector modules, but it must not require those modules to call broker runtime during evaluation.

## 5. Output Contract

The future result should be a frozen dataclass or JSON-safe mapping with these fields:

```text
engine_version: "broker_health_readonly_v1"
decision: BrokerHealthDecision
healthy_for_readonly_review: bool
severity: "pass" | "warn" | "block"
blockers: tuple[string, ...]
warnings: tuple[string, ...]
health_checks: mapping[string, string]
spread_health: string
price_freshness_health: string
latency_health: string
market_health: string
instrument_health: string
permission_health: string
account_identifier_health: string
next_safe_action: string
safety: mapping[string, bool]
sanitized_snapshot: mapping[string, Any]
```

The output `safety` map must always include:

```text
paper_only: true
read_only: true
network_used: false
broker_called: false
credentials_read: false
account_ids_persisted: false
orders_placed: false
demo_execution_allowed: false
live_trading_allowed: false
capital_allocation_modified: false
```

`healthy_for_readonly_review` may be `True` only when `decision == BROKER_HEALTH_READY`.

## 6. Broker Health Decision Enum

Use a new enum namespace and do not reuse candidate or snapshot decision constants.

Required decisions:

```text
BROKER_HEALTH_READY
BROKER_HEALTH_WARN_ONLY
BROKER_HEALTH_BLOCKED_INVALID_INPUT
BROKER_HEALTH_BLOCKED_UNSANITIZED
BROKER_HEALTH_BLOCKED_ACCOUNT_IDENTIFIER
BROKER_HEALTH_BLOCKED_PERMISSION_BOUNDARY
BROKER_HEALTH_BLOCKED_MARKET_CLOSED
BROKER_HEALTH_BLOCKED_INSTRUMENT_UNAVAILABLE
BROKER_HEALTH_BLOCKED_SPREAD
BROKER_HEALTH_BLOCKED_STALE_PRICE
BROKER_HEALTH_BLOCKED_LATENCY
BROKER_HEALTH_BLOCKED_UNRECONCILED
```

Decision priority must be deterministic and fail closed:

1. invalid input.
2. unsanitized input.
3. account identifier violation.
4. permission boundary violation.
5. unreconciled read-only snapshot.
6. market closed.
7. instrument unavailable or not tradeable.
8. missing or excessive spread.
9. missing or stale price.
10. missing or excessive latency.
11. warning-only degraded health.
12. ready.

Only one primary `decision` should be returned, but all discovered blockers and warnings should be preserved in `blockers` and `warnings`.

## 7. Spread Health Rules

Default config:

```text
default_max_allowed_spread_pips: 2.0
warn_spread_ratio: 0.75
block_on_missing_spread: true
block_on_negative_spread: true
```

Rules:

- If `spread_present` is not `True`, block with `BROKER_HEALTH_BLOCKED_SPREAD`.
- If `spread` cannot be parsed as a decimal, block with `BROKER_HEALTH_BLOCKED_SPREAD`.
- If `spread < 0`, block with `BROKER_HEALTH_BLOCKED_SPREAD`.
- If `bid` and `ask` are present and `ask < bid`, block with `BROKER_HEALTH_BLOCKED_SPREAD`.
- If `spread > max_allowed_spread_pips`, block with `BROKER_HEALTH_BLOCKED_SPREAD`.
- If `spread >= max_allowed_spread_pips * warn_spread_ratio`, return warning health when no blockers exist.
- If `spread == 0`, allow only when `bid == ask` and source explicitly marks the feed as synthetic/test fixture; otherwise warn.

Recommended health labels:

```text
spread_ok
spread_warning_near_limit
spread_missing
spread_invalid
spread_negative
spread_bid_ask_inverted
spread_exceeds_limit
```

## 8. Price Freshness Rules

Default config:

```text
max_price_age_seconds: 300
warn_price_age_ratio: 0.80
require_price_timestamp: true
```

Rules:

- `price_timestamp_utc` is required unless a sanitized `price_age_seconds` field is present.
- The evaluator must compute price age from supplied local timestamps only. It must not query current broker time.
- If both `price_timestamp_utc` and `price_age_seconds` are present, the explicit age may be used only if non-negative and internally consistent within a small tolerance.
- If computed or supplied price age is negative beyond clock-skew tolerance, block with stale/invalid price.
- If price age exceeds `max_price_age_seconds`, block with `BROKER_HEALTH_BLOCKED_STALE_PRICE`.
- If price age is at or above `max_price_age_seconds * warn_price_age_ratio`, warn when no blockers exist.
- If bid, ask, and spread are absent from a supposedly fresh price record, block because freshness without price content is not useful.

Recommended health labels:

```text
price_fresh
price_warning_near_stale
price_timestamp_missing
price_age_invalid
price_stale
price_content_missing
```

## 9. Latency Health Rules

Default config:

```text
max_latency_ms: 1500
warn_latency_ratio: 0.80
require_latency: true
```

Rules:

- If `latency_ms` is missing and `require_latency` is `True`, block with `BROKER_HEALTH_BLOCKED_LATENCY`.
- If `latency_ms` cannot be parsed as a non-negative number, block.
- If `latency_ms > max_latency_ms`, block.
- If `latency_ms >= max_latency_ms * warn_latency_ratio`, warn when no blockers exist.
- Latency must be descriptive telemetry only. It must not authorize execution or order placement.

Recommended health labels:

```text
latency_ok
latency_warning_near_limit
latency_missing
latency_invalid
latency_exceeds_limit
```

## 10. Market-open Rules

Rules:

- If `market_hours_open` is not exactly `True`, block with `BROKER_HEALTH_BLOCKED_MARKET_CLOSED`.
- The evaluator must not calculate exchange hours from the internet or broker APIs.
- The evaluator may trust only sanitized upstream market-open evidence.
- If `market_hours_open` is missing, block fail-closed.
- Closed market health may still be useful for diagnostics, but `healthy_for_readonly_review` must be `False`.

Recommended health labels:

```text
market_open
market_closed
market_state_missing
```

## 11. Instrument Availability Rules

Rules:

- `instrument` is required and must be a non-empty sanitized symbol such as `EUR_USD`.
- `instrument_available` must be exactly `True`.
- `instrument_tradeable` must be exactly `True`.
- If either availability or tradeability is missing or false, block with `BROKER_HEALTH_BLOCKED_INSTRUMENT_UNAVAILABLE`.
- The evaluator must not fetch an instrument list from a broker.
- The evaluator must not normalize unsupported broker-specific symbols by guessing.

Recommended health labels:

```text
instrument_available
instrument_missing
instrument_not_available
instrument_not_tradeable
```

## 12. Permission Boundary Rules

The input `permissions` mapping must either be absent and treated as locked, or present with locked values.

Allowed read-only values:

```text
read_only: true
paper_only: true
broker_write: false
order_submission: false
network_submit: false
credentials_present: false
live_trading: false
demo_execution_active: false
capital_allocation_modified: false
```

Rules:

- Any truthy broker-write, order-submit, network-submit, credentials-present, live-trading, or capital-modified flag must block with `BROKER_HEALTH_BLOCKED_PERMISSION_BOUNDARY`.
- Missing `read_only` should warn only if all dangerous permissions are explicitly false.
- Missing dangerous permission keys should be treated as false only when upstream `sanitized` is true and no runtime material is present.
- Permission boundary output must remain fixed even when input claims otherwise; output safety flags must never echo unsafe authorization as true.

## 13. Account Identifier Rejection/redaction Rules

The evaluator must reject account identifiers before any positive health decision.

Accepted placeholder:

```text
DEMO_ACCOUNT_REFERENCE_PRESENT
```

Rules:

- If `account_present` is not exactly `True`, block with `BROKER_HEALTH_BLOCKED_ACCOUNT_IDENTIFIER`.
- If `account_reference` is missing, empty, or not the accepted placeholder, block.
- If any input key name implies account ID, account number, account identifier, credential, token, API key, bearer, password, secret, or authorization material, block unless the value is the accepted placeholder or a known redaction marker.
- If any value looks like a raw account identifier, credential, token, or secret, block.
- The output must not include the raw rejected value.
- The output blocker should use a generic phrase such as `account identifier detected or account placeholder missing`.

Recommended redaction marker:

```text
[REDACTED_ACCOUNT_IDENTIFIER]
```

The evaluator should not attempt to partially mask account IDs. It should reject and emit only a redaction label.

## 14. No-network Guarantee

The future implementation must have no imports or calls that perform network activity.

Disallowed implementation patterns:

```text
requests
httpx
urllib.request
socket
websocket
aiohttp
oandapy
oanda
broker client construction
subprocess invocation for network calls
```

Allowed patterns:

```text
dataclasses
decimal
datetime
enum
typing
pure local parsing helpers
```

The test suite should include a source guard that scans the implementation for forbidden network and broker-call markers.

## 15. No-broker-call Guarantee

The evaluator must not call, instantiate, import, or dynamically load broker clients. It may consume sanitized snapshots created elsewhere, but it must not create or refresh those snapshots.

Required output safety fields must always report:

```text
network_used: false
broker_called: false
orders_placed: false
```

If input says a broker call happened upstream, the evaluator may include a warning such as `upstream_broker_read_claimed`, but it still must not perform a broker call itself.

## 16. Failure Modes

Required failure handling:

- `None` input: block invalid input.
- non-mapping input: block invalid input.
- unsanitized mapping: block unsanitized.
- missing accepted account placeholder: block account identifier.
- real or suspicious account identifier: block account identifier and redact.
- dangerous permission flag: block permission boundary.
- unreconciled snapshot: block unreconciled.
- market closed or missing market state: block market closed.
- instrument missing, unavailable, or not tradeable: block instrument unavailable.
- spread missing, invalid, negative, inverted, or above max: block spread.
- price timestamp missing, invalid, negative age, missing content, or stale: block stale price.
- latency missing, invalid, negative, or above max: block latency.
- warnings only: return `BROKER_HEALTH_WARN_ONLY` with `healthy_for_readonly_review == False` unless the future packet explicitly approves warn-as-reviewable behavior.
- all checks pass: return `BROKER_HEALTH_READY`.

All failures must be deterministic, local, and side-effect free.

## 17. Test Plan

Minimum future tests:

1. Valid sanitized snapshot returns `BROKER_HEALTH_READY`.
2. `None` input returns `BROKER_HEALTH_BLOCKED_INVALID_INPUT`.
3. non-mapping input returns `BROKER_HEALTH_BLOCKED_INVALID_INPUT`.
4. `sanitized: false` returns `BROKER_HEALTH_BLOCKED_UNSANITIZED`.
5. missing account placeholder returns `BROKER_HEALTH_BLOCKED_ACCOUNT_IDENTIFIER`.
6. raw-looking account identifier is rejected and not echoed in output.
7. dangerous `broker_write: true` blocks permission boundary.
8. dangerous `order_submission: true` blocks permission boundary.
9. dangerous `credentials_present: true` blocks permission boundary.
10. `read_only_reconciled: false` blocks unreconciled snapshot.
11. market closed blocks market health.
12. missing market-open state blocks fail-closed.
13. instrument unavailable blocks instrument health.
14. instrument not tradeable blocks instrument health.
15. missing spread blocks spread health.
16. negative spread blocks spread health.
17. `ask < bid` blocks spread health.
18. spread above max blocks spread health.
19. spread near max returns warning-only when all other checks pass.
20. stale price timestamp blocks price freshness.
21. missing price timestamp and missing price age blocks price freshness.
22. negative price age beyond tolerance blocks price freshness.
23. missing bid/ask/spread content blocks price freshness even with fresh timestamp.
24. latency above max blocks latency health.
25. latency near max returns warning-only when all other checks pass.
26. output safety flags are fixed false for network, broker calls, credentials, orders, demo execution, and live trading.
27. source guard confirms implementation has no network, OANDA, broker client, credential, order-submission, subprocess, or environment-variable access patterns.
28. decision priority returns account identifier block before spread/price/latency blockers when multiple failures exist.
29. all blockers are preserved even when one primary decision is selected.
30. JSON conversion preserves decimals as strings or stable JSON-safe values.

## 18. Validator Chain

Required validators for the future implementation packet:

```powershell
python -m pytest tests/forex_engine/test_broker_health_readonly_v1.py
git diff --check
git status --short --branch
```

Optional source guard test:

```text
Scan automation/forex_engine/broker_health_readonly_v1.py for forbidden markers:
requests, httpx, urllib, socket, websocket, aiohttp, oanda, broker client, os.environ, dotenv, subprocess, place_order, submit_order, cancel_order, trade_create
```

For this spec-only packet, the validator chain is:

```powershell
git status --short --branch
git diff --check
```

## 19. Expected Future Implementation Paths

Expected future files, not created by this packet:

```text
automation/forex_engine/broker_health_readonly_v1.py
tests/forex_engine/test_broker_health_readonly_v1.py
Reports/forex_delivery/AIOS_FOREX_BROKER_HEALTH_READONLY_IMPLEMENTATION_V1_REPORT.md
```

Optional future docs path if separately approved:

```text
docs/orchestration/AIOS_FOREX_BROKER_HEALTH_READONLY.md
```

No future implementation should write to protected live-trading, broker credential, order-routing, or capital-allocation paths without a separate protected-action packet and Human Owner approval.

## 20. Collision Notes With Existing Candidate And Risk Modules

### `automation/forex_engine/candidate_scoring_v1.py`

Observed role:

- Scores local candidate dictionaries.
- Uses decision constants such as `REVIEW_READY`, `REQUIRE_MORE_EVIDENCE`, `REJECT`, `BLOCKED_BY_RISK`, `BLOCKED_BY_EVIDENCE`, and `BLOCKED_BY_DEMO_READINESS`.
- Declares safety flags for no network, no broker calls, no credential reads, no account IDs, no orders, and no live trading.
- Does not own broker spread, price freshness, latency, or market-open health evaluation.

Collision rule:

- The future broker health evaluator must not import candidate scoring.
- The future broker health evaluator must not reuse candidate decision constants.
- Candidate scoring may later consume broker health output as an input signal, but broker health must remain independently deterministic and read-only.
- A `BROKER_HEALTH_READY` result is not equivalent to `REVIEW_READY`; it means only that sanitized broker health evidence is acceptable for read-only review handoff.

### `risk_budget_v1.py`

Observed role:

- No `risk_budget_v1.py` file was found in the current repository search.

Collision rule:

- The future broker health evaluator must not create `risk_budget_v1.py`.
- The future broker health evaluator must not calculate, reserve, consume, or approve risk budget.
- If a risk budget module is introduced later, it should consume broker health as a blocking precondition only. Broker health must not decide trade size, leverage, position limits, drawdown allocation, or capital movement.

### `automation/forex_engine/broker_read_only_snapshot_contract_v1.py`

Observed role:

- Owns the existing sanitized broker snapshot contract.
- Accepts only the `DEMO_ACCOUNT_REFERENCE_PRESENT` account placeholder.
- Blocks missing balance, missing margin, unknown exposure, market closed, instrument not tradeable, missing spread, stale/unreconciled, and unsanitized snapshots.
- Keeps broker action, live trading, credential access, account ID persistence, and capital movement disabled.

Collision rule:

- The future broker health evaluator should not replace this contract.
- It should either consume a compatible sanitized snapshot or mirror the same account-placeholder and permission posture.
- It should add finer health detail for spread severity, price freshness, and latency.

### `automation/forex_engine/demo_connector_readonly.py`

Observed role:

- Validates and normalizes read-only demo connector snapshots.
- Rejects account identifiers, credential/runtime material, live control, broker write, order submission, network submission, stale data, invalid snapshots, and unsupported modes.

Collision rule:

- The future broker health evaluator should not create connector snapshots or call connector runtime.
- It may consume connector output only after sanitization.
- It must keep output safety flags locked even if connector input is malformed.

## Implementation Shape

Recommended public API:

```python
BROKER_HEALTH_VERSION = "broker_health_readonly_v1"

class BrokerHealthDecision(str, Enum):
    ...

@dataclass(frozen=True)
class BrokerHealthConfig:
    max_allowed_spread_pips: Decimal = Decimal("2.0")
    warn_spread_ratio: Decimal = Decimal("0.75")
    max_price_age_seconds: Decimal = Decimal("300")
    warn_price_age_ratio: Decimal = Decimal("0.80")
    max_latency_ms: Decimal = Decimal("1500")
    warn_latency_ratio: Decimal = Decimal("0.80")
    placeholder_account_reference: str = "DEMO_ACCOUNT_REFERENCE_PRESENT"

@dataclass(frozen=True)
class BrokerHealthResult:
    ...

def evaluate_broker_health_readonly(snapshot, *, config=None) -> BrokerHealthResult:
    ...

def broker_health_result_to_jsonable_dict(result: BrokerHealthResult) -> dict[str, Any]:
    ...
```

Recommended internal helpers:

```text
_coerce_decimal
_parse_timestamp
_price_age_seconds
_collect_account_identifier_violations
_evaluate_permissions
_evaluate_spread
_evaluate_price_freshness
_evaluate_latency
_primary_decision
_permission_defaults
_json_value
```

All helpers must remain local and side-effect free.

## Next Recommended Packet

Create a separate APPLY packet for:

```text
AIOS-FOREX-BROKER-HEALTH-READONLY-IMPLEMENTATION-V1
```

Expected allowed paths for that future packet:

```text
automation/forex_engine/broker_health_readonly_v1.py
tests/forex_engine/test_broker_health_readonly_v1.py
Reports/forex_delivery/AIOS_FOREX_BROKER_HEALTH_READONLY_IMPLEMENTATION_V1_REPORT.md
```

That future packet should run the targeted pytest file, `git diff --check`, and `git status --short --branch`, and it should not stage, commit, push, or open a PR unless separately approved.
