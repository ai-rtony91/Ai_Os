# Security Policy

## Supported Scope

AI_OS is safety-scaffolded for local development, validation, orchestration, and reviewed automation.

Unauthorized, uncontrolled, unattended, or permission-free live broker execution is blocked. Governed broker-capable architecture may exist only behind explicit reviewed approval, safety gates, runtime-only credential handling, sanitized evidence, and operator control. Credential handling and production deployment require explicit reviewed approval and must follow `RISK_POLICY.md`.

## Vulnerability Reporting

Report vulnerabilities privately to the repository owner/maintainer.

Do not open public issues containing:
- secrets
- API keys
- broker credentials
- exploit details
- sensitive logs
- account identifiers

## Secret Handling

Never commit:
- .env files
- API keys
- broker tokens
- private keys
- passwords
- session files
- sensitive logs
- account credentials

Use environment variables or an approved secret manager.

## Single Live Micro-Trade Exception Security Boundary

`RISK_POLICY.md` owns any future Single Live Micro-Trade Exception. This file does not independently authorize live trading, broker execution, real orders, credential handling, or production deployment.

The security default remains blocked. Any future exception must be one-shot, explicitly approved by Anthony for the exact scope named in `RISK_POLICY.md`, non-transferable, and evidence-bound.

Credentials, tokens, account identifiers, broker order IDs, live payloads, private account data, and secret values must never be printed, committed, logged, stored in the repo, included in prompts, included in reports, captured in screenshots, written to telemetry, or placed in fixtures.

Secure login, dashboard access, terminal launchers, validators, reports, telemetry, queues, routers, and generated evidence do not grant trade authority. They cannot approve, arm, extend, retry, re-enter, or execute a live trade exception.

## Execution Safety

Default mode is DRY_RUN.

APPLY mode requires explicit human approval.

No script, workflow, agent, or automation may perform live trading or broker execution unless the canonical `RISK_POLICY.md` Single Live Micro-Trade Exception is active and every required exception gate is satisfied.

## Disclosure

Security fixes should be reviewed, validated, and documented before release.
