# AI_OS OpenAI Packet Dispatch Flow

Purpose:
Define the local-only route from a future OpenAI-produced packet draft into AI_OS dispatch preview.

## Flow

goal input -> future OpenAI Responses API output -> structured packet draft -> AI_OS dispatch decision -> Night Supervisor preview route -> validator chain -> approval requirement -> final route report

Future OpenAI output must be structured before dispatch. The dispatcher owns the route decision. AI_OS Manager stays in control of the final answer, route safety, approval gate, validator chain, and profitability priority.

Specialists are tools by default. Handoff is allowed only when branch ownership transfer is explicitly justified and approved by a separate packet.

## Night Supervisor Route

The Night Supervisor route is preview-only at first. It may receive packet previews, classify runtime risk, and produce recommendation reports. It cannot start runtime automatically.

Human approval is required before any Night Supervisor runtime start.

## Blocked

This flow does not call OpenAI, read API keys, create `.env`, install packages, make network calls, write telemetry, write control state, write approval inbox state, start Night Supervisor, touch broker/OANDA/live trading, touch Pi GPIO/motor, commit, push, or merge.
