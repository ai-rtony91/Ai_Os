# AI_OS OpenAI to Packet Generator Path

Purpose:
Define the future path from user goal to Codex-ready packet through a gated Responses API adapter.

## Target Flow

User goal -> OpenAI Responses API -> structured packet draft -> AI_OS dispatcher -> validator chain -> human approval -> Codex execution.

## Adapter Requirements

The future real adapter must:

- read approved repo context only
- read `AGENTS.md`
- read source-of-truth docs
- read packet schemas
- read validator schemas
- read allowed and forbidden paths
- produce packet drafts only at first
- avoid live repo mutation in smoke-test mode
- use environment-variable API keys only
- never store or print API keys
- redact sensitive values
- set timeouts
- support validate-only mode
- support no-write mode
- fail closed on uncertainty

## Execution Boundary

OpenAI may draft. Codex executes only after a complete tokenized packet, validator evidence, and human approval where required.

Trusted/proven profitability remains above feature expansion. OpenAI integration must reduce manual relay work and improve packet quality without weakening paper-only trading safety.

