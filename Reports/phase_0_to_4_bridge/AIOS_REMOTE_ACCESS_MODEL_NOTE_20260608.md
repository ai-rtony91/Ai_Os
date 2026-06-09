# AI_OS Remote Access Model Note - 2026-06-08

Status: DRY_RUN documentation note. This records the current operator-approved remote access model. It does not create runtime authority, service authority, notification authority, approval authority, broker authority, or deployment authority.

## Decision

AI_OS remote access for vacation/operator-away use is local-first over the existing Tailscale private network.

Approved current facts:

- Tailscale private network is active.
- Windows PC name: `The_Lab` / `the-lab`.
- Windows PC Tailscale IPv4: `100.91.1.77`.
- Android phone name: `ai-os`.
- Android phone Tailscale IPv4: `100.99.144.22`.
- Windows unattended Tailscale mode was enabled with `tailscale up --unattended=true`.
- RustDesk is allowed only as an emergency visual-control fallback over Tailscale.
- The canonical approval return path must become command-based later.
- Telegram bot remains future/docs-only.

## Operating Model

The approved operator-away model is:

1. Use Tailscale private addressing for trusted device reachability.
2. Use RustDesk only when emergency visual control is needed and only over the Tailscale path.
3. Keep AI_OS approval, packet, worker queue, worker lock, and Night Supervisor state changes inside the existing approval-gated repo workflow.
4. Treat remote access as operator connectivity, not as automation authority.
5. Keep future phone return-path work command-based, explicit, auditable, and approval-gated.

## Explicit Non-Authority

This note does not approve:

- web endpoints.
- public tunnels.
- firewall rule changes.
- cloud deployment.
- Azure App Service deployment.
- Telegram configuration.
- Telegram live send.
- RustDesk auto-configuration.
- approval inbox mutation.
- worker queue mutation.
- worker lock mutation.
- Night Supervisor runtime mutation.
- auto-approval.
- auto-APPLY.
- provider API calls.
- secret storage.
- live trading.
- broker runtime work.

## Safety Boundary

Tailscale and RustDesk are operator access surfaces only. They must not be treated as execution permission, approval permission, commit permission, push permission, merge permission, broker permission, or live-trading permission.

Any future command-based approval return path must preserve:

- identity checks.
- explicit operator intent.
- allowlisted commands only.
- replay/idempotency controls.
- protected-action gates.
- audit trail.
- SOS-only notification discipline.
- no secret printing or storage in repo artifacts.

## Recommended Next Step

Create a future DRY_RUN packet for a command-based approval return-path design that reads current approval cards and produces preview-only decisions, without mutating the approval inbox or worker queue.
