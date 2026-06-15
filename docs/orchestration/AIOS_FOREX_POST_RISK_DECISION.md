# AIOS Forex Post-Risk Decision

`aios_forex_post_risk_decision.py` is a read-only selector for the next
paper-only Forex component after `forex_risk_controls` has been built and
validated.

Current routing:

- If risk controls are missing, select `forex_risk_controls`.
- If risk controls exist and `forex_paper_execution_simulator` is missing,
  select `forex_paper_execution_simulator`.
- If the execution simulator already exists, stop for human review because the
  currently defined post-risk scope is complete.

This contract performs no file writes, command execution, network calls, broker
activity, credential use, real orders, real webhooks, scheduler activation,
daemon activation, worker dispatch, queue mutation, approval mutation, staging,
commit, push, or merge.
