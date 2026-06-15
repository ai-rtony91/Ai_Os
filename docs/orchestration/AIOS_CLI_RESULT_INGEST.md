# AIOS CLI Result Ingest

`aios_cli_result_ingest.py` converts Codex, terminal, or validator report text
into `AIOS_CLI_RESULT_INGEST.v1`.

The contract extracts status, changed files, validation pass/fail state, pytest
counts, protected-action status, blockers, and next safe action. The known
`CreateProcessAsUserW failed: 1312` launcher failure is classified as a sandbox
blocker, not an implementation failure.

The module is parser-only. It does not execute commands, launch Codex, call
network services, mutate queues or approvals, or write files by default.
