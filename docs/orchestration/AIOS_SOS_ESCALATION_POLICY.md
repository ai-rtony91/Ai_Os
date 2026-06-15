# AIOS SOS Escalation Policy

Schema: `AIOS_SOS_ESCALATION_POLICY.v1`

`automation/orchestration/aios_sos_escalation_policy.py` classifies AIOS status dictionaries and decides whether continuation must stop for SOS escalation.

SOS triggers include:

- tests failed after repair
- unknown action or unsupported mode
- unbounded path
- credential, broker, live trading, real order, or webhook flags
- scheduler, daemon, or worker dispatch requests
- queue or approval mutation requests
- destructive action requests
- merge conflict
- failed required GitHub check
- repeated CI failure
- command execution or runtime launch requested without approval

Non-SOS cases include normal `REVIEW_REQUIRED`, one-time no-checks-reported states, waiting for human PR merge approval, and sandbox launcher `CreateProcessAsUserW failed: 1312` when pytest already passed.

The policy is read-only and performs no command execution, network calls, or file writes.
