# AI_OS Operations Note — Raspberry Pi 5 Connectivity and Boundary

Date: 2026-06-06
Status: Source-of-truth connectivity note
Runtime effect: None
Secrets: None
Trading impact: None

## Raspberry Pi 5 Connection Facts

Do not guess the Pi username again.

Validated SSH command:

ssh aiospi5@192.168.1.167

Pi SSH user:

aiospi5

Pi LAN IP:

192.168.1.167

Pi AI_OS sync script:

~/AI_OS/sync_aios_repo.sh

Pi AI_OS repo path:

/home/aiospi5/AI_OS/repo

## Role Boundary

The Raspberry Pi 5 is limited to:

AI_OS progress runner / reporter

Allowed:

- Read-only AI_OS progress/status reporting
- Read-only health checks
- Repo sync/reporting from its limited path
- Local progress visibility
- Log/status evidence collection

Blocked:

- Approval mutation
- Worker launch authority
- Scheduler authority
- Trading execution
- Broker/OANDA/live order actions
- Token storage
- Telegram live sending
- Public remote-control exposure
- Secrets on dashboard

## Next Hardening Target

Harden Pi 5 as a stable, limited, read-only/report-only AI_OS support node.
