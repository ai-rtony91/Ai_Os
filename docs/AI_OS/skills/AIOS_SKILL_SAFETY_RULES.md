# AI_OS Skill Safety Rules

Purpose:
Define safety rules for local and future hosted AI_OS skills.

## Required Rules

- Skills must be reviewed before use.
- Skills must be versioned.
- Skills must map to a specific workflow.
- Skills must not bypass AGENTS.md.
- Skills must not bypass approval gates.
- Skills must not bypass validators.
- Skills must not touch secrets.
- Skills must not create `.env`.
- Skills must not print API keys.
- Skills must not perform broker/OANDA/live trading.
- Skills must not place real orders.
- Skills must not control Pi GPIO/motor.
- Skills must not modify Night Supervisor runtime without a separate approved packet.
- Skills must not write telemetry, control, approval inbox, memory, or lock runtime state unless a later packet explicitly allows it.

## Risk Classes

- `LOW`: docs-only or read-only guidance.
- `MEDIUM`: local fixture/schema generation with no runtime writes.
- `HIGH`: shell, write, network, hosted, or automation-adjacent access.
- `BLOCKED`: secrets, broker, live trading, motor control, Night Supervisor runtime modification, uncontrolled shell, or arbitrary hosted execution.

## High-Risk Skill Rule

Skills with network, shell, write, package install, secret, hosted execution, runtime, broker, trading, or Pi motor/GPIO access require explicit human approval and a separate validator chain before any use.

## Approval Rule

Sensitive or high-impact actions require explicit approval. A reviewed skill may reduce repeated instructions, but it does not grant protected action authority.
