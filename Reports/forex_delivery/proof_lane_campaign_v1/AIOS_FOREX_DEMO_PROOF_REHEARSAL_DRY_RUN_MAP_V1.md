# AIOS Forex Demo Proof Rehearsal Dry-Run Map V1

## 1. Status
`PARTIAL`

## 2. Dry-run only scope
- This front is a local rehearsal map, not a broker-authorized execution path.
- It may use fake or sanitized inputs to prove shape, validation, and reporting.
- It may not call a broker, read credentials, or simulate a real order route with live endpoints.
- It may not claim demo execution, live execution, or profit.

## 3. Required fake/sanitized inputs
- Fake `run_id` and `receipt_id`.
- Fake `account_alias_non_secret`.
- Fake `broker` label such as `demo`.
- Fake `symbol`, `side`, `order_type`, `requested_units`, and `requested_price`.
- Fake `filled_units`, `fill_price`, `spread_observed`, and `slippage_observed`.
- Fake or sanitized `broker_order_id_redacted` and `broker_trade_id_redacted`.
- Sanitized `owner_approval_id` and local `validator_status`.

## 4. Expected receipt envelope
- The rehearsal should use the same non-secret envelope planned for the receipt schema gap map.
- The envelope should preserve chronology, order intent, fill outcome, risk controls, and redaction state.
- The envelope should never require raw broker payloads or private identifiers.
- The envelope should be hashable and replayable locally.

## 5. Owner approval gate
- A future broker-authorized demo requires current-session Human Owner approval.
- The approval must name the exact symbol, order type, size, stop loss, take profit, max loss, and approval window.
- The approval must be separate from this dry-run map.
- Without that approval, demo execution remains blocked.

## 6. Validator chain
- Compile the Python sources with `python -m compileall -q -j 0 automation tests scripts`.
- Run the Forex engine tests with `python -m pytest tests/forex_engine/ -q`.
- Run the local security credential broker test with `python -m pytest tests/security/test_aios_bitwarden_local_credential_broker_v1.py -q`.
- Finish with `git diff --check`.
- If `xdist` is installed, the Forex engine suite may also run with `-n auto`, but that is optional.

## 7. Failure modes
- Missing sanitized receipt fields.
- Raw account identifiers or raw broker IDs appearing in the fixture.
- Accidental network access or broker calls.
- Schema drift between the fake receipt and the validator.
- Approval fields that are stale, ambiguous, or missing.

## 8. Stop conditions
- Stop if the flow would call a broker, connect to a live endpoint, or request credentials.
- Stop if the flow would place or modify an order.
- Stop if the flow would send a notification or write a secret-bearing payload.
- Stop if the rehearsal would produce a profit claim or readiness claim beyond local preparation.

## 9. Safe transition into future broker-authorized demo
- First land the receipt schema and dry-run validator.
- Then prove the fixture set against the validator with local-only tests.
- Then obtain a separate current-session owner approval for a broker-authorized demo packet.
- Only then may a future broker-authorized demo lane be considered.

## 10. Explicit no-live/no-profit/no-broker-call claim boundary
- This map does not authorize live execution.
- This map does not authorize profit claims.
- This map does not authorize broker calls.
- This map is preparation-only.
