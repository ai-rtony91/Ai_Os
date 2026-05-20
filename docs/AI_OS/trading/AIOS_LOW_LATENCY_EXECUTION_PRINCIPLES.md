> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS_V2 authority. Current operating authority is `AGENTS.md`; current V2 front-door/context authority is `README.md`; current source-of-truth mapping lives under `docs/governance/`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved V2 canonical document explicitly promotes them.

# AIOS_LOW_LATENCY_EXECUTION_PRINCIPLES

## PURPOSE
Defines trading-engine execution separation and low-latency design principles.

## CORE PRINCIPLE
LLMs must not exist in the live order execution pathway.

## LIVE EXECUTION PATH
- Deterministic code only
- Low-latency validation
- Fast risk checks
- Broker/API routing
- Kill-switch logic
- Execution confirmation handling

## LLM RESPONSIBILITIES
- Analytics
- Reporting
- Documentation
- Research
- Review
- Architecture planning
- Signal analysis support

## SEPARATION MODEL
Dashboard and orchestration layers must remain logically separated from live execution pathways.

## EXECUTION PRIORITIES
- Low latency
- Deterministic behavior
- Reliability
- Recoverability
- Minimal dependencies
- Fail-safe operation

## FORBIDDEN DESIGN PATTERNS
- LLM-confirmed live trades
- Chat-based execution approval loops
- High-latency execution chains
- Non-deterministic live execution logic

## TARGET ARCHITECTURE
TradingView/Webhook
? Validation Engine
? Risk Engine
? Execution Engine
? Broker/API

LLMs remain outside direct execution routing.
