# Forex Paper Execution Engine 001

## Purpose

This file defines the first paper-only simulated execution loop for the AI_OS Forex Money Bot.

It does not place live trades. It does not connect to broker APIs. It does not call webhooks. It does not make internet calls. It does not use secrets.

## Required Simulation Flow

1. Signal generated
2. Confluence score calculated
3. Decision engine evaluates signal
4. Risk gate check
5. Simulated entry created
6. Simulated stop loss assigned
7. Simulated take profit assigned
8. Trade lifecycle tracked
9. Simulated close condition reached
10. Result written to scorecard
11. Telemetry updated

## Safety State

- paper_only_status: PAPER_ONLY
- live_execution_status: BLOCKED
- broker_api_status: BLOCKED
- webhook_status: BLOCKED
- internet_call_status: BLOCKED
- real_order_status: BLOCKED

The engine is a local simulation spine only.
