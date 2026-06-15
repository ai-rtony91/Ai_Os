# AIOS Codex Packet Builder

Schema: `AIOS_CODEX_PACKET_BUILDER.v1`

`automation/orchestration/aios_codex_packet_builder.py` builds a packet preview contract for the next approved Codex continuation. It creates text only; it does not launch Codex or call any API.

Current packet support:

- action: `build_forex_paper_execution_simulator`
- packet: `PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY`

The packet preview includes:

- identity header
- validator chain
- write scope
- safety blocks
- complete Codex prompt text

By default the builder writes nothing. Its explicit writer is constrained to `Reports/aios_relay/`.
