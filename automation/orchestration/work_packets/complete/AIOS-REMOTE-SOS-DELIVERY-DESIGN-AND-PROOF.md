# Proposed Review Packet: Remote SOS Delivery Design And Proof

Status: PROPOSED / REVIEW-ONLY
This file is not an executable Codex packet and does not authorize APPLY, SOS send by Codex, runtime launch, runtime execution, queue mutation, scheduler registration, approval mutation, worker inbox mutation, command queue mutation, broker action, live trading, credential access, deletion, push to main, merge, or PR closure.

## Purpose

Design and prove a remote SOS delivery path that can reach Anthony without relying on a permanent USB direct-line ADB connection from the Omen desktop.

## Background

Local USB ADB SOS delivery was manually confirmed by Anthony at `2026-06-11 13:15`. Remote SOS delivery remains `NOT_PROVEN`.

## Scope

Compare these candidate delivery paths:

- wireless ADB on the same LAN
- VPN or Tailscale-style private network path
- Tasker or phone-side receiver
- Telegram or webhook alternative
- RustDesk or manual remote-control fallback

For each option, evaluate:

- security risk
- reliability
- setup burden
- whether secrets or credentials are required
- whether it works away from the local LAN
- whether it can be tested without Codex sending SOS

## Allowed Paths

- `Reports/human_gate/`
- `Reports/autonomy_loop_closure/`
- `automation/orchestration/work_packets/proposed/`

## Forbidden Paths

- `automation/orchestration/work_packets/active/`
- `automation/orchestration/work_packets/blocked/`
- `automation/orchestration/work_packets/complete/`
- `automation/orchestration/workers/inbox/`
- `automation/orchestration/command_queue/`
- `automation/orchestration/approval_inbox/`
- `telemetry/runtime/`
- `services/runtime/`
- `services/dispatcher/`
- `services/orchestrator/`
- `services/policy/`
- `scripts/control/`
- `tools/android/`
- `apps/trading_lab/`
- `aios/modules/trader/`
- `.github/`
- `.git/`
- `secrets`
- `credentials`
- `.env`
- `broker files`
- `live trading paths`

## Blocked Actions

Do not send SOS from Codex. Do not edit `tools/android/Send-AiosAdbSosWake.ps1`. Do not store secrets. Do not register scheduler. Do not launch runtime. Do not execute runtime. Do not mutate queue, approval inbox, worker inbox, command queue, broker, or trading paths.

## Validator Chain

- `git diff --check`
- `git status --short --branch`

## Stop Point

Stop after producing a comparison matrix, a recommended remote SOS proof path, and the exact human-confirmation evidence needed for a later proof-consuming packet.

## Safe Next Action

Review the remote delivery options and choose one exact proof lane. Scheduler registration remains blocked until remote SOS delivery is proven and human-confirmed.
