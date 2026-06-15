# AIOS RustDesk Operator Runbook

## Purpose

RustDesk is the current primary remote-control lane for Anthony to observe or guide the local AIOS workstation.

This runbook is operational guidance only. It does not grant repo mutation, protected Git actions, runtime activation, broker access, credential access, or live trading authority.

## Current Lane

- Primary: RustDesk remote control.
- Optional fallback: Tailscale private mesh, if already available.
- Not core right now: Mullvad or VPN setup.

## Operator Use

1. Connect with RustDesk.
2. Confirm the visible workstation is the active AIOS machine.
3. Confirm the repo path is `C:\Dev\Ai.Os` before approving any repo action.
4. Approve only the exact scoped action shown by the active packet.
5. Stop if the command mentions secrets, broker, live trading, orders, webhooks, scheduler, daemon, delete, reset, clean, commit, push, merge, or branch deletion without exact approval.

## Non-Blocker

Forex-builder and self-build work must not be blocked on VPN setup. Remote-control tooling is an operator access lane, not a forex-builder dependency.
