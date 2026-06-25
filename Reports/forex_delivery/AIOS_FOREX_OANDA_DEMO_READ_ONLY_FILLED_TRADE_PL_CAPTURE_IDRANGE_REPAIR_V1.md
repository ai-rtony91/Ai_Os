# AIOS Forex OANDA Demo Read-Only Filled Trade P/L Capture Idrange Repair V1

## Scope

- Packet: AIOS-FOREX-OANDA-DEMO-READ-ONLY-FILLED-TRADE-PL-CAPTURE-IDRANGE-REPAIR-V1
- Mode: APPLY
- Lane: oanda-demo-read-only-filled-trade-pl-capture-idrange-repair
- Boundary: read-only OANDA demo filled-trade P/L capture repair

## Root Cause

The capture defaulted transaction-window evidence to:

```text
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/transactions?from=<id>&to=<id>
```

That shape can be interpreted as a time-range transaction list request, so the owner-observed `from=327&to=330` request returned `416 INVALID_TIME_RANGE`.

The evaluator then treated any non-200 transaction-window response as a full blocker before building `openTrades` and `openPositions` P/L evidence. That blocked classification even though owner evidence showed trade `328` was open, `EUR_USD`, `currentUnits` `1`, `price` `1.13689`, `realizedPL` `0.0000`, `unrealizedPL` `-0.0001`, with take-profit order `329` and stop-loss order `330`.

## Repair

- Default transaction-window URL now uses the read-only id-range shape:

```text
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/transactions/idrange?from=<id>&to=<id>
```

- The endpoint validator allowlist now permits the read-only `transactions/idrange` shape while preserving GET-only, practice-host-only, no-live-endpoint, and no-mutation rules.
- The evaluator now builds P/L evidence from all read results before deciding whether read failures are fatal.
- A transaction-window read failure is non-blocking only when `openTrades` or `openPositions` provides open trade/position proof.
- If no open trade or open position proof exists, the transaction-window failure remains blocking.

## Validation

- `python -m pytest tests/forex_engine/test_oanda_demo_read_only_filled_trade_pl_capture_v1.py -q`: PASS, 9 passed.
- `python -m py_compile automation/forex_engine/oanda_demo_read_only_filled_trade_pl_capture_v1.py scripts/forex_delivery/run_oanda_demo_read_only_filled_trade_pl_capture_v1.py`: PASS.
- `git diff --check`: PASS.
- `git status --short --branch`: branch `feature/forex-oanda-demo-read-only-filled-trade-pl-capture-idrange-repair-v1` with only allowed-path changes after this APPLY.

## Safety

- No broker call was run by Codex.
- No owner-run command was run by Codex.
- Tests use fake vault and fake HTTP adapters only.
- No order placement, order close, order mutation, trade mutation, position mutation, live endpoint, credential/account printing, dotenv read, or env read path was added.
- Windows Vault remains runtime-only through the approved adapter boundary.
- Runtime token and account values remain redacted from returned payloads.

## Next Safe Action

Anthony may review the scoped diff and, if satisfied, run the owner-side read-only capture command separately. Codex did not commit, push, open a PR, merge, or call the broker.
