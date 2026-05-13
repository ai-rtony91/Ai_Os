# Forex Portfolio Engine 001

## Purpose

The Forex Portfolio Engine is the first paper-only portfolio layer for the AI_OS Forex Money Bot.

It compares multiple pair opportunities before a paper entry is allowed into the simulated queue. It does not execute live trades, connect to broker APIs, send webhooks, make internet calls, install packages, store secrets, or run autonomous execution.

## Portfolio Controls

- max pair exposure placeholder
- max simultaneous trades placeholder
- correlation conflict detection
- directional exposure tracking
- session concentration tracking
- pair duplication prevention

## Ranking Intent

The portfolio engine helps AI_OS avoid treating every signal as equal. It ranks stronger paper opportunities first, suppresses weak opportunities, reduces exposure during drawdown pressure, and keeps portfolio awareness before paper simulation.

## Safety State

- paper_only_status: PAPER_ONLY
- live_execution_status: BLOCKED
- broker_api_status: BLOCKED
- webhook_status: BLOCKED
- autonomous_execution_status: BLOCKED
