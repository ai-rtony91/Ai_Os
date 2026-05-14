# AI_OS Runtime Packet Queue Scaffold

Purpose:
Define the future local packet queue automation area for AI_OS dispatcher runtime work.

This folder is documentation and scaffold only. It does not assign packets, approve APPLY work, edit files, stage files, commit, push, or run background automation.

Packet queue rules:

- One packet per worker.
- Packet queue intake stays separate from packet runtime truth.
- Workers must confirm `allowed_paths` and `blocked_paths` before work.
- DRY_RUN may inspect, report, and validate.
- APPLY requires explicit human approval.
- Unknown packet, worker, lock, or repo state becomes `REVIEW_REQUIRED`.
- No broker, OANDA, API key, webhook, or live trading execution is allowed.

Recommended future files:

- `packet_queue.json` for queued packet intake.
- `packet_assignment.json` for current assignment decisions.
- `packet_completion_report.json` for worker completion summaries.

Current status:
Scaffold only. No executable queue assignment exists yet.

Next safe action:
Review the packet queue examples before approving any future packet automation script.
