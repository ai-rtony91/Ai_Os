# AIOS Forex Builder Broker-Paper Dry-Run Risk Governor

This packet adds a local-only dry-run risk governor contract for fake broker-paper intent ledger records. It is not broker integration, it does not read credentials, and it does not place paper or live orders.

The governor evaluates in-memory dry-run ledger records before any future broker-paper layer can exist. Each record must remain a dry-run stub result, include operator approval, carry a stop loss, stay inside a small per-intent loss cap, use an approved fake/local forex symbol, and preserve the stub flags proving no request or order was sent.

Risk defaults are intentionally conservative:

- Max loss per intent: 2.00 USD.
- Max daily loss: 5.00 USD.
- Max intents per day: 3.
- Max quantity units: 1000.
- Kill switch armed: true.

Daily stop logic is aggregate-only in this gate. Accepted dry-run records contribute their max loss to the in-memory aggregate. If the aggregate exceeds the daily cap, the ledger is not ready and the next safe action is risk-governor repair.

The kill switch is modeled as a required armed contract flag. If it is not armed, every decision is rejected. This preserves a hard safety boundary for future replay or adapter work.

Rejected records are useful evidence. They prove unsafe fake intents are blocked and audited instead of treated as profit or silently ignored. A rejected record is never placed, never transmitted, never written to Reports, and never allowed to imply broker readiness.

This gate keeps these capabilities blocked:

- broker SDKs
- credentials and `.env` reads
- network/API calls
- webhooks
- scheduler or daemon activation
- broker-paper orders
- live orders
- file writes and Reports writes

The next packet after a ready risk governor is `PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1`. That is still dry-run replay work, not broker SDK integration.
