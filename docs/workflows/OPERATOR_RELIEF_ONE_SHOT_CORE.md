# AI_OS Operator Relief One-Shot Core

Status: workflow documentation for a local-only operator relief helper.

The one-shot core in `automation/operator_relief/run_operator_relief_loop.py` reduces routine copy/paste burden by collecting repo state, classifying blockers, writing local evidence, and drafting a non-executable follow-up packet for human review.

Safety boundaries:

- one-shot only; no persistent watcher or background loop
- no scheduler registration
- no Night Supervisor activation
- no live SOS delivery
- no ADB wake execution
- no Telegram or webhook send
- no credential loading
- no staging, commit, push, merge, stash, delete, or cleanup action
- no broker, live trading, cloud, or provider runtime behavior

Runtime evidence is written under `telemetry/generated/operator_relief/`, which is covered by the generated-output policy and ignored by Git. Clean routine success records evidence and requests no wake. Blocked and SOS-worthy states remain local evidence only until a separate operator-approved live-SOS lane arms a delivery channel.

PR #437 remains draft input. This core is the narrow extracted subset and does not carry over scheduler, ADB apply rail, auto-commit/push executor, forex changes, broad CLI expansion, duplicate Tier 0 docs, or generated evidence dumps.

