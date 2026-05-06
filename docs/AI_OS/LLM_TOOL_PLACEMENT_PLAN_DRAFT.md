# AI_OS LLM Tool Placement Plan Draft

## Purpose

This draft defines future LLM/tool placement only. It does not connect LLM APIs, implement agents, edit code, edit services, edit dashboard files, or approve broker/trading integration.

## Placement Model

| Tool / Interface | Future role | Current approval status |
|---|---|---|
| ChatGPT / OpenAI | Architecture, planning, review, policy reasoning, risk framing, and work-order drafting. | Planning only |
| Codex | Repo-local code/file worker under strict human approval. | Existing workflow only |
| Claude or secondary LLM | Optional later reviewer or codebase surgeon if separately approved. | Not approved yet |
| Dashboard | Operator interface for visibility, approval gates, telemetry summaries, and next safe action. It is not the LLM itself. | Planning only |

## ChatGPT / OpenAI Role

ChatGPT/OpenAI may be used as the architecture, planning, review, and policy reasoning layer. It should produce plans, checklists, explanations, and risk reviews. It must not be treated as authorization to bypass local approval rules.

## Codex Role

Codex may act as the repo-local code/file worker only under explicit mode and scope. Codex must follow DRY_RUN-first workflow, collision checks, protected-file rules, and human approval before APPLY.

## Secondary LLM Role

Claude or another secondary LLM may be considered later for review, codebase surgery, or independent critique only if separately approved. No secondary LLM integration is approved by this draft.

## Dashboard Role

The dashboard should be the operator interface, not the LLM itself. It may later show state, approvals, risk, progress, telemetry, and next safe action. It must not autonomously launch tools, edit files, place trades, or handle secrets.

## Blocked Actions

- LLM API connection.
- Agent implementation.
- Dashboard integration.
- Service integration.
- Credential/key/token handling.
- Broker integration.
- Live trading.
- App launch automation.
- Telemetry migration.

## Known Unresolved Items

- Agent runtime implementation design remains UNKNOWN.
- LLM API/provider selection remains UNKNOWN.
- Dashboard-to-agent integration path remains UNKNOWN.
- `operational_aios_progress_percent` formula is not approved yet.
- Trading Mode safety boundaries require later review.
- Credential/key handling policy is not implemented.
- Current directory display mismatch was observed in Codex and was verified by PowerShell before APPLY.
