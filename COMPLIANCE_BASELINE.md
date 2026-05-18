# AI_OS Compliance Baseline

Status: baseline scaffold, pending human review.

AI_OS is compliance-oriented and safety-scaffolded, but not audit-ready until all controls below are implemented, reviewed, and evidenced.

## Control Map

| Area | Requirement | Status |
|---|---|---|
| Secure SDLC | Security expectations documented and reviewed | Partial |
| CI | Validation runs on push and pull request | Added |
| Dependency Updates | Dependabot configured | Added |
| Secret Handling | Secret prevention documented | Added |
| Threat Model | Agent boundaries and risks documented | Added |
| Approval Model | DRY_RUN/APPLY rules documented | Added |
| Audit Logging | Required events documented | Added |
| Public Repo Hygiene | Sensitive references reviewed | Pending |
| Trading Safety | No live broker execution by default | Added |
| Branch Protection | Required checks enabled in GitHub settings | Pending |
| Test Evidence | Validator/test execution history recorded | Pending |

## Non-Negotiable Rules

- Default to DRY_RUN.
- APPLY requires explicit human approval.
- No commits or pushes unless explicitly requested.
- No secrets, credentials, broker tokens, or API keys.
- No live trading or broker execution.
- Protected root/governance files require review.
- Public repository exposure must be considered before publishing sensitive details.

## Audit-Ready Exit Criteria

Before claiming audit readiness:

- SECURITY.md exists and is reviewed.
- CI workflow exists and passes.
- Dependabot exists.
- Threat model exists and is reviewed.
- Approval model exists and is reviewed.
- Audit logging spec exists and is reviewed.
- Repo hygiene review is complete.
- Placeholder governance docs are expanded or clearly marked.
- Branch protection is enabled.
- Secret scanning is enabled in GitHub settings where available.
- No known secrets are present in tracked files.
