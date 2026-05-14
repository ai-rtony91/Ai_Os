# AI_OS Worker Runtime

This folder is reserved for future worker-session runtime helpers.

Current phase:

- docs and examples only
- no executable worker control
- no startup task logic
- no APPLY automation
- no commit or push automation

Worker runtime rules:

- one active worker table owns current worker state
- one heartbeat table owns current heartbeat state
- one registration status file records launch and duplicate identity checks
- stale workers are not safe to replace automatically
- human approval is required before worker reassignment
- unknown worker state becomes `REVIEW_REQUIRED`

