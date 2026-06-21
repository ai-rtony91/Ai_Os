# AIOS FOREX NO-ORDER CONNECTOR TEST STRATEGY V1

## Test Scope

Future-only test strategy for a no-order connector phase. No test implementation files are created in this packet.

## Required Test Cases

1. Rejects live endpoint
- Input endpoint classification: live/production
- Expected: `BLOCKED`, blocker includes endpoint rejection

2. Rejects missing demo mode
- Missing or malformed demo/paper marker
- Expected: `BLOCKED`, fail-closed

3. Rejects credentials in repo context
- Credential-like fields present in input or evidence
- Expected: `BLOCKED`, credential boundary required blockers

4. Rejects account id exposure
- Account id-like fields or access flags present
- Expected: `BLOCKED`, no-account-id enforced

5. Rejects order placement
- Any request/order placement intent in connector payload
- Expected: `BLOCKED`, order-route attempts rejected

6. Rejects order modification
- Modify/cancel hints present
- Expected: `BLOCKED`

7. Rejects order cancellation
- Cancel path present
- Expected: `BLOCKED`

8. Rejects position mutation
- Position change field present
- Expected: `BLOCKED`

9. Permits read-only planning
- Input path only contains governance/metadata/evidence
- Expected: `READY` or equivalent non-blocked readiness

10. Records denied attempt
- Any denied transition from above
- Expected: blocked attempt evidence generated with reason and correlation id

11. Records kill-switch block
- Kill-switch active during preflight
- Expected: blocked attempt record with halt reason and halt source

12. Records replay evidence
- Replay reference requested and mismatch checks run
- Expected: replay references stored and replay validation status preserved

## Suggested Test Domains

- Boundary evaluators
- Handoff preflight evaluators
- Read-only connector policy tests
- Evidence generation determinism tests
- Halt propagation tests

## Test Output Expectations

- Every failure path yields deterministic blockers
- Every denied path yields immutable blocked-attempt evidence
- No pathway should produce broker network state or execution-authority flags in current phase
