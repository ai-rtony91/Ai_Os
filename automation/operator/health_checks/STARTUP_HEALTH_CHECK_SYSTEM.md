# AI_OS Startup Health Check System

Purpose:
Validate environment before operator startup.

Checks:
- canonical repo exists
- git installed
- branch readable
- git status readable
- policy files exist
- startup scripts exist
- required operator folders exist
- no missing startup references
- no blocked deployment scripts active

Future:
- cloudflare validation
- azure validation
- codex availability checks
- worker readiness checks
- dashboard boot checks
- telemetry integrity checks
