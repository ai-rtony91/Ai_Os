# AI_OS Replay Engine 001

## Purpose

The AI_OS Replay Engine is the first paper-only replay and scenario stress-testing layer for AI_OS trading intelligence.

It simulates edge deterioration, volatility explosions, fake recoveries, drawdown spirals, regime transitions, unstable strategy behavior, portfolio overload, and confidence freeze reactions.

It does not execute trades, connect to broker APIs, call networks, deploy autonomously, install packages, or store secrets.

## Replay Behaviors

- replay simulated signals
- replay regime transitions
- replay confidence degradation
- replay drawdown pressure
- replay fake edge recovery
- replay portfolio overload
- replay confidence freeze activation

## Stress Reactions

- reduce confidence
- freeze confidence increases
- reduce ranking priority
- reduce simulated size
- move to WATCH state
- block unstable edge promotion
- require recovery evidence

## Scenario States

- NORMAL
- WATCH
- UNSTABLE
- EDGE_COLLAPSE
- DRAWDOWN_CRITICAL
- RECOVERY_REQUIRED
- CONFIDENCE_FROZEN

## Safety State

- paper_only_status: PAPER_ONLY
- live_execution_status: BLOCKED
- broker_api_status: BLOCKED
- real_execution_status: BLOCKED
- network_call_status: BLOCKED
- autonomous_execution_status: BLOCKED
