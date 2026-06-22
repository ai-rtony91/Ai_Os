# AIOS Protected Runtime Credential Injection V1

## Purpose

`AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_V1` defines the local contract and dry-run harness for proving that live credential material is supplied only at runtime and never persisted in AIOS repo artifacts.

It is not a live execution command, not a credential entry script, and not a broker runner.

## Position In The Live Trading Spine

The protected live spine is:

1. `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1`
2. `AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_V1`
3. `OandaLiveRuntimeConnectorV2`
4. `OandaLiveHttpTransportV1`

The final bridge remains the operator arming and safety gate. This injection layer sits after the bridge and before the connector/transport pair. It proves that an injected HTTP client and injected runtime auth provider are present without reading any credential source.

## Runtime-Only Credential Doctrine

The runtime auth provider is built from function arguments only. It returns credential values only when invoked by the runtime caller. The injection summary records only whether a provider is present. It does not return token values, account identifiers, authorization headers, raw request data, or raw broker payloads.

## Avoiding `.env` And Persistence

The harness does not import `os`, does not read environment variables, does not import `dotenv`, does not import `requests`, does not call file IO, and does not write reports or runtime state. All outputs are sanitized dictionaries returned to the caller.

Credential and account persistence flags are always false.

## Connection To OANDA Live HTTP Transport V1

The harness uses `build_oanda_live_http_transport_config` and `build_oanda_live_http_transport_readiness` to prove the transport can be assembled with an injected HTTP client and runtime auth provider.

Dry-run mode does not call `http_client.post`. Non-dry-run mode still blocks unless `protected_live_execution_command` is explicitly true, and this packet does not create a real execution command.

## Connection To Final Live Operator Bridge V1

The harness builds a final bridge state from the sanitized operator request and order intent. The bridge must report `FINAL_LIVE_OPERATOR_BRIDGE_READY` before the harness can report local readiness.

The bridge remains the place where operator approval, live exception intent, risk acknowledgements, stop loss, take profit, one-trade-only, and micro-size gates are proven.

## Samsung/Mobile Operator Boundary

Samsung/mobile approval remains a separate operator surface. Mobile truth fields can show that runtime injection is ready, blocked, or review-required, but mobile display does not enter credentials, store credentials, or authorize live execution.

Credential entry, if ever approved, must happen outside repo files and outside generated reports.

## Remaining Before Live Micro-Trade Execution

Before any live micro-trade execution, AIOS still needs a separate human-approved protected live execution command, runtime-only credential entry outside the repo, a fake-client-free operator session, current risk evidence, explicit stop-after-one-order procedure, and final validation that no credential or account identifier is persisted.
