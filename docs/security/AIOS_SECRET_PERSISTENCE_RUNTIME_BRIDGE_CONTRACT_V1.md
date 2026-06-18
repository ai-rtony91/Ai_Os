# AIOS Secret Persistence Runtime Bridge Contract V1

## Status

Status: DESIGN_CONTRACT

Zone: SECURITY

Human Owner: Anthony Meza

## Purpose

Reduce repeated API-key and operator burden while keeping secrets out of the repo, prompts, logs, reports, screenshots, evidence files, Codex output, dashboard output, and GitHub.

This document is a design contract only. It does not implement secret persistence, read secrets, print environment variables, create scripts, modify runtime code, modify dashboard code, call broker APIs, place trades, or approve live trading.

## Authority Boundary

This contract works under:

- `AGENTS.md`
- `README.md`
- `SECURITY.md`
- `docs/security/secret-prevention.md`
- `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md`
- `docs/security/approval-model.md`
- `docs/forex_delivery/AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1.md`
- `docs/dashboard/AIOS_MINIMAL_OPERATOR_DASHBOARD_CONTRACT_V1.md`
- `docs/forex_delivery/AIOS_AUTO_EXIT_INTELLIGENCE_GATE_V1.md`
- `docs/forex_delivery/AIOS_PL_TRUTH_LAYER_REQUIREMENTS_V1.md`

If this contract conflicts with root security, risk policy, secret-prevention guidance, credential-exclusion rules, or Human Owner approval requirements, the stricter safety rule wins.

## Primary Goal

Make secret access feel persistent for the Human Owner without making secrets visible or permanent in unsafe places.

AIOS should reduce repeated key entry by using a future approved local masked setup path, while Codex, ChatGPT, reports, dashboards, validators, evidence files, telemetry, GitHub, and repo files receive only non-sensitive status such as `PRESENT`, `MISSING`, `ARMED`, or `BLOCKED`.

## Core Secret Rules

- Secrets are runtime-only.
- Secret values never enter repo files.
- Secret values never enter Codex prompts.
- Secret values never enter ChatGPT messages.
- Secret values never enter reports.
- Secret values never enter screenshots.
- Secret values never enter dashboard output.
- Secret values never enter logs.
- Secret values never enter telemetry.
- Secret values never enter fixtures.
- Secret values never enter GitHub.

AIOS may handle only secret status, not secret content, unless a future Human Owner-approved implementation packet defines a narrower local runtime path.

## Approved Operator Method

Future implementation packets may define a local masked PowerShell setup method with this operator flow:

1. The Human Owner runs a local PowerShell helper or one-time local block.
2. PowerShell prompts with `Read-Host -AsSecureString`.
3. The Human Owner pastes the secret only into the masked prompt.
4. The secret is stored only in the local user runtime environment or an approved operating-system secret store.
5. No secret value is printed.
6. No secret value is written to the repo.
7. No secret value is included in prompts, reports, screenshots, logs, dashboard output, telemetry, fixtures, or evidence files.
8. Future AIOS runtime checks report only `PRESENT` or `MISSING`.

This contract does not create that helper and does not approve any specific storage mechanism. The helper requires a separate implementation packet with exact allowed paths, forbidden paths, validation, approval authority, and stop point.

## Required Secret Status Model

Future runtime checks should expose only this kind of status evidence:

```text
OPENAI_API_KEY_STATUS: PRESENT/MISSING
OANDA_API_KEY_STATUS: PRESENT/MISSING
OANDA_ACCOUNT_ID_STATUS: PRESENT/MISSING
SECRET_VALUES_PRINTED: false
SECRET_VALUES_RECORDED: false
ACCOUNT_ID_RECORDED: false
RAW_BROKER_PAYLOAD_RECORDED: false
```

`PRESENT` means the required value appears available to the approved local runtime check without revealing the value.

`MISSING` means the required value is unavailable, expired, inaccessible, or not safely checkable.

Any unknown, ambiguous, logged, printed, recorded, or exposed state must fail closed.

## Dashboard Rules

Dashboard may show only:

```text
SECRET_BRIDGE: PRESENT/MISSING
BROKER_BRIDGE: ARMED/BLOCKED
```

Dashboard must never show:

- API keys
- tokens
- account IDs
- endpoint secrets
- raw broker payloads
- private order identifiers unless explicitly approved
- transaction identifiers unless explicitly approved
- secret-store paths that expose private user data

The dashboard displays status only. It does not read secrets, create secrets, approve secret use, arm broker access, approve live trading, or create truth.

## Forex Rules

No future live forex action may proceed unless:

- required secret statuses are `PRESENT`
- no secret values are printed
- no secret values are logged
- no secret values enter the repo
- no account IDs are logged
- no raw broker payloads are stored
- sanitized evidence path is active
- auto-exit readiness is satisfied
- P/L truth-layer capture is available
- Human Owner approval and all applicable risk gates are present

Secret presence is necessary but never sufficient for live action. Secret presence does not approve broker calls, orders, retries, re-entry, live trading, dashboard control, runtime mutation, commit, push, or PR work.

## Fail-Closed Conditions

AIOS must block if:

- secret is missing
- secret would be printed
- secret would be logged
- secret would enter the repo
- secret would enter a prompt
- secret would enter dashboard output
- secret would enter a report
- secret would enter a screenshot
- secret would enter telemetry or fixtures
- account ID would be exposed
- raw broker payload would be captured
- dashboard attempts to display secret values
- runtime check cannot distinguish `PRESENT` from `MISSING`
- a future implementation packet lacks exact approval, allowed paths, forbidden paths, validation, or stop point

## Evidence Rules

Allowed evidence:

- `PRESENT`
- `MISSING`
- `ARMED`
- `BLOCKED`
- timestamp of a status check when safe
- check result source name when safe
- non-sensitive block reason

Forbidden evidence:

- secret values
- partial secret values
- account IDs
- raw broker payloads
- endpoint secrets
- raw environment dumps
- screenshots containing private data
- private order identifiers unless explicitly approved
- transaction identifiers unless explicitly approved

## Future Implementation Packets

Future work must be separately packetized:

- `AIOS-LOCAL-MASKED-SECRET-SETUP-HELPER-V1`
- `AIOS-SECRET-PRESENT-MISSING-RUNTIME-CHECK-V1`
- `AIOS-DASHBOARD-SECRET-BRIDGE-STATUS-V1`
- `AIOS-BROKER-BRIDGE-ARMING-GATE-V1`

Each future packet must keep secret values outside Codex, ChatGPT, repo files, logs, reports, screenshots, dashboards, validators, fixtures, telemetry, GitHub, and generated evidence.

## Stop Conditions

Stop if:

- any secret value is requested in chat or prompt text
- any secret value would be printed or logged
- any `.env` file would be read, written, staged, or committed
- any broker/API/runtime code change is required outside an approved implementation packet
- any dashboard code change is required outside an approved implementation packet
- any validator, test, or script change is required outside an approved implementation packet
- any live-trading, broker-call, or order behavior is requested
- secret persistence would proceed without Human Owner approval and a reviewed storage boundary

