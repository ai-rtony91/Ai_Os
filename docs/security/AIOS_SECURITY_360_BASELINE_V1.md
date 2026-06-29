# AIOS Security 360 Baseline V1

## Purpose

AIOS Security 360 Baseline V1 establishes an internal high-security engineering baseline before any remote dashboard, broker, real-money, Bitwarden, credential, demo, live, scheduler, daemon, webhook, tunnel, deployment, or autonomous execution work proceeds.

This is a bank-style defense-in-depth target for engineering discipline. It is not a legal bank certification, compliance certification, audit certification, or external assurance claim.

## Baseline Status

- Security baseline status: `BASELINE_CREATED_REVIEW_REQUIRED`
- Overall security posture: `REVIEW_REQUIRED`
- Bank-style security target: `DEFENSE_IN_DEPTH_HIGH_ASSURANCE_INTERNAL_TARGET`
- Certification claim: `NO_EXTERNAL_BANK_CERTIFICATION_CLAIM`

## Current Allowed State

Allowed now:

- Read-only repo inspection.
- DRY_RUN planning.
- Local static dashboard preview.
- Sanitized report generation.
- Owner review.

## Current Blocked State

Blocked unless future explicit owner approval and required gates exist:

- `broker_contact`
- `broker_api_use`
- `credential_use`
- `env_read`
- `account_identifier_use`
- `order_execution`
- `demo_authorization`
- `live_authorization`
- `scheduler_start`
- `daemon_start`
- `webhook_start`
- `watcher_start`
- `listener_start`
- `background_loop_start`
- `remote_public_exposure`
- `tunnel_start`
- `bitwarden_start`
- `vaultwarden_start`
- `secrets_migration`
- `token_storage`
- `dashboard_execution_controls`

## Security Domains

The baseline classifies AIOS across these domains:

1. Identity and access control.
2. Repo permissions and branch protection.
3. Secret prevention and secret scanning.
4. Credential handling and runtime-only secrets.
5. Broker/API boundary protection.
6. Dashboard remote-access protection.
7. Mobile access protection.
8. Network exposure and tunnel control.
9. Scheduler/daemon/webhook/background-loop control.
10. Bitwarden/Vaultwarden readiness boundary.
11. Logging, audit trail, and evidence integrity.
12. Telemetry and runtime state protection.
13. File-system and generated-artifact hygiene.
14. Worker/Codex/ChatGPT/automation lane separation.
15. CI security gates.
16. Dependency and package risk.
17. Data privacy and account-identifier exclusion.
18. Trading kill switch, one-order-only, max-loss, daily stop, SL/TP gate.
19. Incident response and rollback.
20. Owner approval gates.

## Required Gates

### A. Remote Dashboard Gate

Must require:

- Authenticated access.
- Private route or HTTPS.
- Read-only dashboard API.
- No secrets in frontend.
- No broker account identifiers.
- No execution controls.
- Source freshness labels.
- Access logging.
- Owner approval.

### B. Broker Read-Only Gate

Must require:

- Sanitized evidence format.
- No credentials in repo.
- No account identifiers in repo.
- No raw broker payloads in repo.
- Runtime-only credentials if ever approved.
- No order endpoints.
- Owner approval.

### C. Bitwarden Gate

Must require:

- Forex 110 merged.
- Owner confirmation.
- Threat model.
- Backup/export plan.
- Recovery plan.
- YubiKey/MFA option review.
- No token storage before approval.

### D. Demo/Live Gate

Must require:

- Profitability proof.
- Broker-readonly evidence.
- Latency/canonical audit.
- Kill switch.
- One-order-only enforcement.
- Micro-size enforcement.
- Stop loss.
- Take profit.
- Max loss.
- Daily stop.
- Owner approval.
- Runtime-only credentials.
- Post-trade evidence capture.

### E. Scheduler/Daemon/Webhook Gate

Must require:

- Explicit owner approval.
- Bounded runtime.
- Kill switch.
- Logs.
- Alerting.
- No broker execution by default.
- Safe shutdown.
- Rollback path.

## Priority Findings

Critical:

- Remote dashboard, broker/API, demo/live, Bitwarden, scheduler, daemon, webhook, tunnel, deployment, and autonomous execution work must remain blocked until gates are implemented and owner-approved.

High:

- Branch protection and required-check enforcement cannot be proven from local repo files.
- A workflow-dispatch Azure dashboard deployment workflow exists and must remain blocked until reviewed.
- Remote dashboard architecture is defined, but authenticated read-only server, access logging, and mobile/private-route proof are not implemented.
- Credential use, account identifiers, raw broker payloads, order endpoints, and broker contact remain blocked by policy.

Medium:

- Current security docs are marked baseline scaffold or pending human review.
- Dependabot exists, but deeper dependency audit gates are not proven in this baseline.
- Telemetry, Reports, runtime state, and generated evidence remain protected until retention and sanitization are approved.

Low:

- Security guidance is split across root, docs/security, governance, workflows, and generated reports. Future changes should update existing authority only and avoid duplicate security authority.

## Tool Behavior

The baseline tool must:

- Perform static repo checks only.
- Never read `.env`.
- Never read secrets.
- Never call network.
- Never call broker.
- Never mutate files.
- Return deterministic JSON-safe output.
- Classify findings by severity.
- Mark missing controls as review/blocker, not pass.
- Fail closed when unknown.

## Safe Next Actions

1. Owner reviews Security 360 Baseline V1.
2. Verify GitHub branch protection and required checks.
3. Run repo hygiene and account-identifier exclusion review before any remote exposure.
4. Implement Remote Dashboard Gate before LAN, private mesh, tunnel, host, or production dashboard access.
5. Keep broker, credential, Bitwarden, demo/live, scheduler, daemon, webhook, tunnel, and deployment work blocked until separate approved gates pass.

Status: `BASELINE_CREATED_REVIEW_REQUIRED`
