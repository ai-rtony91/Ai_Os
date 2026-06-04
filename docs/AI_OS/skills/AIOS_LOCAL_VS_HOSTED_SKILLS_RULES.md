# AI_OS Local vs Hosted Skills Rules

Purpose:
Define when AI_OS should use local skill-style bundles and when hosted skills remain blocked.

## Local Skills

Local skills are preferred first because they are:

- inspectable in the repo
- versioned through Git
- reviewable through PRs
- bounded by AGENTS.md
- compatible with DRY_RUN-first validation
- easier to audit and roll back

Local skills may document workflows, validate fixtures, generate reviewed packet drafts, or run read-only checks only when separately approved.

## Hosted Skills

Hosted skills are future-only and separately gated. They may add account, upload, network, execution, and supply-chain risk.

Before any hosted skill is allowed, AI_OS must define:

- upload boundary
- allowed files
- forbidden files
- secret redaction
- version pinning
- review process
- audit trail
- rollback plan
- human approval flow
- no-bypass guarantees

## Shell and Network Boundary

Any skill with shell, write, network, package install, secret, runtime, broker, trading, Pi GPIO/motor, or hosted execution behavior is high-risk. AI_OS must treat it as blocked until a separate human-approved packet enables a narrow, validated use case.
