# Agent Workflow Implementation Plan

## Purpose

Phase 15.5 turns the Phase 15.1 runtime scaffold into a clearer local workflow architecture.

The workflow is:

user goal
-> intake packet
-> task classification
-> ownership check
-> blocked path check
-> task queue
-> runner preview
-> validator selection
-> output summary
-> next action
-> human approval

## What This Phase Creates

This phase creates:

- workflow state machine
- task lifecycle JSON
- handoff packet schema
- runner DRY_RUN spec
- validator chain
- blocked actions matrix
- next-action router
- implementation plan
- Codex summary
- read-only workflow readiness validator
- read-only workflow snapshot script
- dashboard mock-data fixture
- health report
- checkpoint report

## What This Phase Does Not Do

This phase does not create autonomous agents. It does not install external LLM frameworks. It does not start background work. It does not create scheduled tasks. It does not add startup persistence. It does not connect accounts. It does not enable live trading, brokers, OANDA, API keys, secrets, real webhooks, real orders, live market data, payments, financial claims, or profitability guarantees.

## Agent Roles

Major agents own the main lane:

- architecture_agent
- automation_agent
- ui_agent
- integration_agent
- reporting_agent
- risk_gate_agent
- backtest_agent
- trading_research_agent

Minor agents fill gaps only inside the assigned major agent scope:

- scaffold_gap_agent
- schema_gap_agent
- validator_gap_agent
- mock_data_agent
- naming_agent
- docs_patch_agent
- cleanup_agent
- dependency_notes_agent

## Trading Lab Compatibility

The workflow supports future paper-only Trading Lab tasks:

- paper signal intake
- paper bot runner
- latency tracker
- candle fixture loader
- regime checker
- risk gate
- paper result ledger
- scorecard
- replay review
- strategy ranking
- next action

Trading Lab live orders, broker execution, OANDA execution, API key usage, real webhook execution, account connection, real market dependency, trade execution claims, and profit guarantee claims remain blocked.

## Next Safe Action

Run:

`powershell -ExecutionPolicy Bypass -File automation/agent_runtime/Test-AiOsAgentWorkflowReadiness.DRY_RUN.ps1`

