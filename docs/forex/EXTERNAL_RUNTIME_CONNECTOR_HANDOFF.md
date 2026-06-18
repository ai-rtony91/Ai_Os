# External Runtime Connector Handoff

Status: FOREX_DELIVERY operator handoff instructions. This document is value-free and non-executing. It does not store credentials, request credentials, connect to broker, call network APIs, fetch market data, place paper orders, place live orders, create `.env`, edit source code, grant approval, commit, push, or merge.

## Purpose

The first OANDA practice/demo connection proof is blocked until an external runtime connector is available outside AI_OS repo storage and outside Codex visibility.

Current blocker:

- `external_runtime_connector_required`

## Plain-English Meaning

An external runtime connector is the operator-controlled runtime layer that holds the real OANDA practice/demo access material and performs the broker-facing connection attempt outside the repo.

AI_OS provides the protected proof boundary and receives only sanitized status-only evidence. AI_OS, Codex, repo files, reports, tests, logs, and telemetry must not receive credential values, account IDs, endpoint values, raw broker payloads, screenshots, exact balances, market data payloads, order IDs, or private account data.

The existing protected proof boundary can fail closed or process sanitized status-only output. It must not become the place where credentials, account references, endpoint values, or raw connector output are entered or stored.

## Operator-Controlled Material

The Human Owner must keep the following outside Codex visibility and outside repo files:

- OANDA practice/demo credentials.
- Practice/demo account reference.
- Approved runtime handoff path or external runner location.

AI_OS may receive only value-free confirmations and labels such as:

- broker family: `OANDA_PRACTICE`
- endpoint class: `OANDA_PRACTICE_DEMO`
- auth reference status: `EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- account reference status: `EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- connector availability: `PRESENT` or `MISSING`
- connector handle status: `CALLABLE_VALUE_FREE_HANDLE_PRESENT` or `MISSING`

## Callable Connector Handle Requirement

The protected runner can use only an already-constructed callable connector handle. The handle must expose the expected connection method to the runner without exposing credential values, account IDs, endpoint values, endpoint URLs, raw broker payloads, screenshots, order IDs, exact balances, or private account data.

The handle must remain operator-controlled and must not be represented as a dictionary containing credential-like keys, account-like keys, endpoint-value keys, token values, secret values, live endpoint flags, order-route flags, retry flags, scheduler flags, daemon flags, webhook flags, or raw payload fields.

If the handle is missing, non-callable, live, endpoint-value-bearing, credential-bearing, account-ID-bearing, order-capable, retry-capable, or raw-payload-bearing, the protected runner must fail closed before broker contact.

## Safe Operator Rules

- Do not paste credentials into Codex, ChatGPT, reports, tests, logs, telemetry, or terminal output that Codex will read.
- Do not commit credentials.
- Do not print credentials.
- Do not print account IDs.
- Do not ask Codex to create `.env`.
- Do not ask Codex to read `.env`, a password manager, a secret manager, shell environment variables, browser storage, or private account screens.
- Redact account IDs from all reports and evidence.
- Do not provide endpoint URLs or endpoint values in repo artifacts.
- Do not provide raw connector output, screenshots, order IDs, transaction IDs, exact balances, or private account data.

## Next Proof Packet Prerequisites

Before a future proof packet can make one OANDA practice/demo connection proof attempt, all prerequisites must be true:

- Fresh Human Owner approval for exactly one status-only OANDA practice/demo connection proof.
- External runtime connector is available outside AI_OS and outside Codex visibility.
- Callable value-free connector handle is available to the protected runner.
- Practice/demo endpoint class only.
- One-shot proof only.
- Retry count is zero.
- No scheduler, daemon, webhook, queue, retry loop, or autonomous re-entry.
- No order route.
- No market-data route.
- No paper order.
- No live order.
- Sanitized evidence path is defined.
- Stop point is defined before the proof runs.

## Fail-Closed Stop Conditions

Stop before broker contact if any of these occur:

- Connector missing.
- Credential visible to Codex, AI_OS repo files, reports, logs, tests, telemetry, chat, or command output.
- Account ID visible to Codex, AI_OS repo files, reports, logs, tests, telemetry, chat, or command output.
- Live endpoint detected.
- Endpoint value or endpoint URL appears in a repo artifact.
- Raw broker payload appears.
- Market-data payload appears.
- Order route, paper order, live order, position open, position close, or position modify appears.
- Retry, scheduler, daemon, webhook, queue, or autonomous re-entry appears.
- Approval is missing, stale, ambiguous, or not one-shot.

## Sanitized Evidence Contract

The future proof result may contain only status-only fields:

- proof attempted: true or false
- proof result: connected, rejected, error, timeout, manual stop, or blocked
- endpoint class: demo/practice category only
- connector present: yes or no
- credential values: redacted or absent
- account IDs: redacted or absent
- order ID: absent
- live endpoint: absent
- token: absent
- secret: absent
- retry count: zero
- order route: not enabled
- market-data route: not enabled

## Next Packet

Recommended next packet after the external runtime connector is available and fresh Human Owner approval exists:

- `AIOS-FIRST-DEMO-CONNECTION-PROOF-APPLY-WITH-EXTERNAL-RUNTIME-V1`

Stop here until those prerequisites are true.
