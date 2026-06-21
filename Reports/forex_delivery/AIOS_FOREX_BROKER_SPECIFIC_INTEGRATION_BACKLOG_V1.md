# AIOS Forex Broker Specific Integration Backlog V1

## Ordered Tickets

1. Broker Transport Interface Design
   - Define transport contract only. No network calls.

2. External Credential Provider Adapter Plan
   - Plan external secret access boundary. No secret reads.

3. Sanitized Account Metadata Mapping
   - Define allowed metadata and account ID redaction.

4. OANDA Demo Endpoint Verifier Contract
   - Define OANDA demo endpoint mode proof. No endpoint calls.

5. Read-Only Account Summary Probe Skeleton
   - Skeleton only. No broker access.

6. Read-Only Pricing Probe Skeleton
   - Skeleton only. No broker access.

7. Broker Response Sanitizer
   - Remove secrets, account IDs, and unsafe fields.

8. Broker Evidence Recorder
   - Record sanitized broker-facing event evidence.

9. Broker Connectivity Dry-Run Validator
   - Validate intended connectivity without network access.

10. Final Protected Demo Connectivity Review
   - Human-reviewed gate before any future connectivity authorization.

## Constraints
No broker SDK, credentials, account identifiers, network transport, endpoint calls, order execution, demo trading, or live trading.
