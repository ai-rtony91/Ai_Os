# AIOS SOS Local Notifier

Status: v1 local-only planner. Subordinate to `AGENTS.md`, README, and active
AI_OS safety governance.

## Purpose

`AIOS_SOS_LOCAL_NOTIFIER.v1` converts existing SOS policy and status evidence
into safe local alert instructions. It prepares preview text for a Windows
toast, terminal banner, and beep plan, but it does not execute any of them.

The planner is for local evidence and operator review only. It is not a live
notification bridge, scheduler, daemon, worker launcher, webhook sender, broker
adapter, or approval authority.

## Inputs

The Python planner consumes four dictionaries:

- `sos_policy`
- `stop_report`
- `core_status`
- `notifier_options`

Supported SOS trigger evidence includes:

- `sos_policy.sos_required: true`
- `sos_policy.wake_anthony: true`
- warning or critical severity
- protected-action attempts
- broker or live-trading risk
- credential, secret, or API-key risk
- real order or real webhook risk
- destructive-action risk
- validator failure after repair budget
- stuck loop, no progress, or repeated failure
- existing `AIOS_SOS_ESCALATION_POLICY.v1` output such as
  `escalation_status: SOS_ESCALATION`, `anthony_required: true`, or matched SOS
  categories

## Output

The planner returns:

- `schema: AIOS_SOS_LOCAL_NOTIFIER.v1`
- `notifier_status: no_alert | alert_ready | blocked | rejected`
- `alert_level: none | info | warning | critical`
- `should_alert`
- `alert_reason`
- `alert_title`
- `alert_message`
- `windows_toast_preview`
- `terminal_banner_preview`
- `beep_plan_preview`
- `repeat_policy`
- `external_notifications_requested`
- `external_notifications_blocked`
- `files_written`
- `commands_executed`
- `rejection_reasons`
- `next_safe_action`
- `safety`

## Safety Contract

v1 is preview-only by construction:

- no Windows toast is shown
- no sound or beep is played
- no Reports files are written
- no PowerShell notification command is called
- no email, SMS, Discord, Telegram, Slack, webhook, or API call is made
- no network access is requested or used
- no broker, credential, live-trading, real-order, or real-webhook path is used
- no scheduler, daemon, worker dispatch, queue mutation, or approval mutation is
  performed
- no Git staging, commit, push, merge, or destructive cleanup is performed

External notification requests are recorded and blocked. A future live channel
requires a separate scoped packet, explicit Human Owner approval, validator
evidence, and a stop point.

## Example

```python
from automation.orchestration.aios_sos_local_notifier import build_sos_local_notifier_plan

plan = build_sos_local_notifier_plan(
    sos_policy={"sos_required": True, "severity": "critical"},
    stop_report={},
    core_status={},
    notifier_options={"channels": ["telegram"]},
)

assert plan["notifier_status"] == "alert_ready"
assert plan["alert_level"] == "critical"
assert plan["external_notifications_blocked"] is True
assert plan["files_written"] == []
assert plan["commands_executed"] == []
```

## Validation

Run the focused validator:

```powershell
python -m pytest -p no:cacheprovider tests/orchestration/test_aios_sos_local_notifier.py
```

