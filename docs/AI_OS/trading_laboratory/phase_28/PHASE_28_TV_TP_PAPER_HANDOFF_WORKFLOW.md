# Phase 28 TV/TP Paper Handoff Workflow

## Purpose

Phase 28 defines a paper-only TradingView-style -> AI_OS -> TradersPost-style handoff scaffold.

AI_OS is the validation and workflow layer. It reviews a local mock signal, records latency fields, validates payload shape, checks the risk gate, previews a paper route, requires operator decision, and sends the result into journal/replay and scorecard planning.

## Workflow

1. TradingView-style signal
2. AI_OS paper intake preview
3. Latency timestamp
4. Payload validation
5. Risk gate
6. TradersPost-style paper route preview
7. Operator decision required
8. Journal/replay
9. Scorecard update

## Reuse From Phase 20

Phase 28 reuses the Phase 20 reference-only concept:

- External platform names are labels only.
- Route preview is paper-only.
- AI_OS owns validation and safety gates.
- No real webhook, credential, broker, or order path is active.

Phase 28 does not duplicate Phase 20 panels. Dashboard placement should use the existing Trading Lab Advanced handoff surface and prefer the Phase 28 fixture when available.

## Safety Boundary

Required blocked states:

- live_execution: BLOCKED
- broker: BLOCKED
- real_order: BLOCKED
- api_key_required: false

Also blocked:

- OANDA
- live trading
- account connection
- real webhooks
- autonomous execution
- broker credentials
- secrets

## Latency Boundary

Phase 28 stores latency fields as local mock data only. If no measured source exists, values must remain null, Pending validation, or Not measured.

Required latency fields:

- alert_created_time
- alert_received_time
- validation_start_time
- validation_end_time
- route_preview_time
- total_delay_seconds
- stale_status

## Dashboard Placement

Trading Lab only. Secondary, Advanced, or workstation support area only.

Do not show Phase 28 on the AI_OS first screen. Do not create a duplicate external handoff surface.

## Next Safe Action

Run the Phase 28 dry-run validator and keep the workflow paper-only.
