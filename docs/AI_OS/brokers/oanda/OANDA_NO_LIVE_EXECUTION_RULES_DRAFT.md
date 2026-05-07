# OANDA No Live Execution Rules Draft

## Purpose

This draft defines no-live-execution rules for any future OANDA discussion. It is documentation only.

## Core Rule

`execution_allowed` must remain `false`.

No OANDA document, dashboard panel, validator, adapter concept, telemetry field, or future script may imply live execution approval.

## Blocked States

Future OANDA planning must block:

- live account login
- live account identifiers
- live token handling
- live pricing stream use
- live order route design
- live order placement
- automated trade execution
- unattended strategy activation
- broker webhook relay
- LLM placement in the live order path

## Required Labels

Any future OANDA placeholder should label execution state as:

- `BLOCKED`
- `REVIEW_ONLY`
- `NO_CREDENTIAL_ACCESS`
- `NO_ORDER_PATH`
- `NO_LIVE_TRADING`

## Non-Approval Statement

This draft does not approve OANDA sandbox access, OANDA practice trading, live trading, broker API calls, telemetry collection, dashboard controls, or credential handling.
