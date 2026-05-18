# Security Policy

## Supported Scope

AI_OS is safety-scaffolded for local development, validation, orchestration, and reviewed automation.

AI_OS must not be used for live broker execution, unattended trading, credential handling, or production deployment without explicit reviewed approval.

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

## Execution Safety

Default mode is DRY_RUN.

APPLY mode requires explicit human approval.

No script, workflow, agent, or automation may perform live trading or broker execution unless a separate reviewed production policy explicitly allows it.

## Disclosure

Security fixes should be reviewed, validated, and documented before release.
