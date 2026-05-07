# AIOS_REPO_SOURCE_OF_TRUTH_MAP

## PURPOSE
Maps AI_OS document authority to reduce ambiguity.

## ROOT DOCUMENT AUTHORITY
- README.md = project mission and entry overview
- WHITEPAPER.md = high-level system concept and vision
- ARCHITECTURE.md = system architecture
- AGENTS.md = AI/Codex behavior rules
- RISK_POLICY.md = safety, DevOps, and trading-risk constraints
- SOURCE_LOG.md = source traceability
- ERROR_LOG.md = failures and errors
- HALLUCINATION_LOG.md = suspected incorrect AI claims
- AAR.md = after-action reviews
- DAILY_REPORT.md = daily reporting pointer

## DOCS/AI_OS AUTHORITY
- docs/AI_OS/operator = operator workflow rules
- docs/AI_OS/codex = Codex orchestration rules
- docs/AI_OS/context = recovery context and assistant memory externalization
- docs/AI_OS/reporting = reporting and checkpoint standards
- docs/AI_OS/trading = trading-system boundaries
- docs/AI_OS/checkpoints = stage checkpoint records
- docs/AI_OS/audits = audit and review artifacts
- docs/AI_OS/backfill = controlled backfill plans

## RULE
When documents conflict, stop and request human review. Do not silently choose one.
