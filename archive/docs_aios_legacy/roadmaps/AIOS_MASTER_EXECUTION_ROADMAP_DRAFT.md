# AI_OS Master Execution Roadmap Draft

Status: DRAFT
Mode: DRY_RUN-derived roadmap
Current repository state: scaffold-heavy, governance-first, local-first, not production deployed
Source basis: current repository structure, AI_OS governance files, dashboard drafts, telemetry drafts, Azure boundary drafts, trading boundary drafts, tool registry files, autonomous/bootstrap drafts, and reporting/checkpoint history.

## Current Readiness Assessment

AI_OS is currently a documentation-rich and safety-first scaffold. The strongest areas are governance policy, DRY_RUN/APPLY workflow discipline, reporting conventions, dashboard fixture planning, tool registry detection readiness, and trading execution blocking. The weakest areas are production runtime implementation, authenticated cloud deployment, secure runtime secrets handling, CI/CD, live telemetry collectors, broker abstraction, AI validation runtime, and execution engine controls.

Estimated overall production-grade readiness: 34%.

## Global Sequencing Rules

- Governance hardening must precede automation expansion.
- Source-of-truth validation must precede scaffold normalization.
- Dashboard visibility must remain read-only before execution features.
- Telemetry must be fixture-first before persistent collectors.
- Tool and agent control must be approved before multi-agent execution.
- Signal intelligence and backtesting must precede any paper-trading pipeline.
- Paper-trading evidence must precede broker integration readiness.
- Broker integration readiness must precede any execution engine.
- AI validation must block trades before any semi-autonomous execution is considered.
- Azure production hardening must not deploy until secrets, auth, observability, rollback, CI/CD, and approval gates are complete.

## PHASE 01 - FOUNDATION GOVERNANCE HARDENING

Estimated maturity: 60%.

### STAGE

Harden protected files, repository ownership, source-of-truth validation, migration controls, duplicate prevention, operational policy enforcement, and AI safety boundaries.

### STEPS

- Confirm root governance files remain protected: `README.md`, `AGENTS.md`, `RISK_POLICY.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `HALLUCINATION_LOG.md`, `AAR.md`, `DAILY_REPORT.md`, and white paper files.
- Convert root scaffold warnings in `RISK_POLICY.md` and `ARCHITECTURE.md` into reviewed governance references without overwriting existing content.
- Build a source-of-truth map across `docs/AI_OS`, `Reports`, `automation`, `apps`, `services`, and `agent`.
- Define duplicate prevention rules for docs, reports, fixtures, and validators.
- Require every folder-role change to pass DRY_RUN review before APPLY.
- Enforce separation between AI_OS workshop files and trading execution files.
- Maintain blocked-action policies for secrets, broker execution, live trading, destructive filesystem operations, and Windows security settings.

### EXPECTED OUTPUTS

- Protected-file policy map.
- Source-of-truth inventory.
- Duplicate detection report.
- Governance validation checklist.
- Root policy review packet.
- DRY_RUN-to-APPLY workflow standard.

### RISKS

- Root files currently include scaffold placeholders and may be over-trusted.
- Duplicate drafts may create conflicting guidance.
- AI agents may infer readiness from documentation volume rather than verified implementation.
- Trading work may leak into AI_OS governance scope.

### VALIDATION RULES

- No root protected file edit without backup and explicit approval.
- Every source-of-truth claim must reference an existing file or be labeled UNKNOWN.
- Any conflict between repo evidence and notes must be marked MISMATCH.
- No destructive operation may be proposed as a default cleanup action.

### DRY_RUN SAFETY CHECKS

- Run repo status check.
- List candidate governance files.
- List duplicate candidates.
- List protected files touched: expected none unless approved.
- Confirm no secrets, broker tokens, or credentials are read or modified.

### FUTURE APPLY CONDITIONS

- Human approval for each protected-file edit.
- Backups created before protected edits.
- Final report written after APPLY.
- Git commit only after clean validation and explicit approval.

## PHASE 02 - CONTEXT PERSISTENCE + MEMORY SYSTEMS

Estimated maturity: 45%.

### STAGE

Formalize checkpoint architecture, recovery packets, bootstrap systems, telemetry continuity, operator continuity, AI handoff systems, and session restoration systems.

### STEPS

- Normalize checkpoint naming across `Reports/checkpoints`.
- Define recovery packet schema using existing operator, bootstrap, and session docs.
- Connect daily report, checkpoint, progress ledger, and telemetry preview contracts.
- Create session restoration packets for new Codex chats.
- Define operator continuity rules for phase, stage, workload pack, task ID, DRY_RUN/APPLY mode, checkpoint, and commit state.
- Validate that memory artifacts never include secrets, credentials, private keys, broker tokens, or account sessions.

### EXPECTED OUTPUTS

- Checkpoint schema.
- Recovery packet template.
- Session handoff template.
- Bootstrap context pack.
- Telemetry continuity map.
- Operator continuity checklist.

### RISKS

- Session state may become stale if not tied to git status and evidence files.
- Recovery packets may overstate readiness.
- Telemetry continuity may imply persistence that does not exist yet.

### VALIDATION RULES

- Every session restoration packet must include git branch, git cleanliness, phase, stage, last checkpoint, next safe action, and unknowns.
- All unverified facts must remain UNKNOWN.
- Recovery packets must not include secrets or account state.

### DRY_RUN SAFETY CHECKS

- Read checkpoint index and latest checkpoint reports.
- Read progress ledger files.
- Confirm no credential paths are scanned.
- Confirm no background service, scheduled task, or persistence collector is created.

### FUTURE APPLY CONDITIONS

- Human approval to create or update session templates.
- File changes limited to docs, Reports, or approved automation preview scripts.
- No autonomous session writer until retention and privacy rules are approved.

## PHASE 03 - SCAFFOLD NORMALIZATION

Estimated maturity: 50%.

### STAGE

Normalize repository structure, folder standards, architecture references, inventory systems, schema enforcement, and registry systems.

### STEPS

- Inventory all AI_OS folders and confirm `README_FOLDER_PURPOSE.txt` coverage.
- Identify stale, empty, conflicting, or duplicate draft files.
- Define canonical folder ownership for docs, reports, automation, apps, services, agent, internal, and inputs.
- Create schema registry for dashboard fixtures, telemetry previews, trading lab records, signal records, and tool registry data.
- Align architecture references with current local-first scaffold and future Azure boundary.
- Keep archive, hold, wrong-remote, and trading engine boundaries separate.

### EXPECTED OUTPUTS

- Folder ownership map.
- Scaffold normalization report.
- Schema registry index.
- Duplicate prevention report.
- Architecture normalization checklist.

### RISKS

- Cleanup pressure may lead to deletion, movement, or rename actions that are currently prohibited.
- Multiple draft files may remain intentionally redundant until reviewed.
- Schema enforcement may be premature if contracts are still evolving.

### VALIDATION RULES

- No delete, move, or rename.
- No overwrite without backup and approval.
- No folder merge recommendation unless human approval is requested separately.
- Schema validation must be read-only until APPLY is approved.

### DRY_RUN SAFETY CHECKS

- Run file inventory.
- List duplicates only as candidates.
- Mark conflicts MISMATCH.
- Mark unverifiable readiness claims INVALID DATA.

### FUTURE APPLY CONDITIONS

- Create missing purpose notes only after successful DRY_RUN and approval.
- Add schema indexes without altering existing schema files unless separately approved.

## PHASE 04 - DASHBOARD + HUMAN CONTROL LAYER

Estimated maturity: 40%.

### STAGE

Advance the mobile responsive AI_OS dashboard, collapsible sidebars, telemetry panels, orchestration visibility, AI activity feeds, task queue visualization, health monitoring, and approval systems.

### STEPS

- Complete Stage 13.4 fixture-only Tool Registry Dashboard UI wire-up.
- Keep dashboard read-only and fixture-driven.
- Establish parity between static preview and React dashboard before real data adapters.
- Add mobile responsive behavior validation for critical panels.
- Add approval-state visibility before any action buttons become executable.
- Add orchestration and AI activity feeds using approved fixtures only.
- Add task queue visualization as display-only.
- Add health monitoring panels sourced from local fixtures and DRY_RUN validators.

### EXPECTED OUTPUTS

- Fixture-driven Tool Registry panel.
- Dashboard parity report.
- Mobile validation checklist.
- Approval gate panel.
- AI activity fixture panel.
- Task queue fixture panel.
- Health overview panel.

### RISKS

- UI controls may look executable before execution is approved.
- Dashboard may accidentally call real APIs.
- Static preview and React app may diverge.
- Visual polish may outpace safety clarity.

### VALIDATION RULES

- No real APIs.
- No backend action unless explicitly approved.
- No secrets or credentials in fixtures.
- Blocked states must be visible.
- FAIL, BLOCKED, protected-file risk, validator state, trading readiness, and next safe action must be prioritized.

### DRY_RUN SAFETY CHECKS

- Confirm mock fixture exists.
- Confirm edited files list before APPLY.
- Confirm no dashboard code calls broker, credential, account, install, or deployment paths.
- Confirm static preview remains local/offline-first.

### FUTURE APPLY CONDITIONS

- Human approval for each UI wiring packet.
- Visual validation before commit.
- No deployment until Azure and auth phases are approved.

## PHASE 05 - REPORTING + TELEMETRY ENGINE

Estimated maturity: 35%.

### STAGE

Build automated checkpoint generation, session metrics, audit pipelines, operational scoring, AI execution telemetry, dashboard metrics, and historical indexing.

### STEPS

- Normalize `Reports/daily`, `Reports/checkpoints`, `Reports/health`, and `Reports/progress` outputs.
- Define telemetry preview-to-production migration gates.
- Add read-only validators for report completeness.
- Define operational scoring model from validator results, git status, checkpoint freshness, and approval state.
- Add AI execution telemetry fields without recording prompts containing secrets or private data.
- Add dashboard metric fixtures before persistent telemetry.
- Build historical indexing as append-only report metadata.

### EXPECTED OUTPUTS

- Report index standard.
- Telemetry schema validator.
- Operational scoring draft.
- Historical index draft.
- Dashboard metrics fixture.
- AI execution telemetry privacy boundary.

### RISKS

- Telemetry may collect sensitive data if boundaries are unclear.
- Persistent collectors may run without approval.
- Report writers may overwrite protected files.

### VALIDATION RULES

- No background collectors until approved.
- No scheduled tasks.
- No secrets, credentials, broker tokens, private keys, recovery keys, live trade data, uncontrolled screenshots, or private material.
- Report writers must use allowlisted paths only.

### DRY_RUN SAFETY CHECKS

- Validate report paths.
- Validate fixture data only.
- Confirm writer status is inactive unless approved.
- Confirm no protected root files will be modified.

### FUTURE APPLY CONDITIONS

- Human approval for report writers.
- Retention policy approved before telemetry persistence.
- Rollback plan approved before production telemetry.

## PHASE 06 - TOOL REGISTRY + AGENT CONTROL

Estimated maturity: 45%.

### STAGE

Formalize Codex role orchestration, Claude support roles, agent boundaries, execution permissions, registry health systems, approval routing, and multi-agent coordination.

### STEPS

- Complete fixture-only tool registry dashboard display.
- Keep tool detection read-only.
- Maintain status values: READY, INSTALLED, MISSING, NEEDS_LOGIN, NEEDS_CONFIG, BLOCKED, INTERNAL_MODULE, NOT_APPLICABLE, UNKNOWN.
- Define Codex as implementation agent under DRY_RUN/APPLY and human approval gates.
- Define Claude and other assistants as support/review/planning lanes only until approved.
- Add agent task ID, files touched log, decision log, and approval-required flag usage.
- Add registry health checks for missing tools, login-needed tools, config-needed tools, and blocked tools.

### EXPECTED OUTPUTS

- Tool registry dashboard panel.
- Agent permission matrix.
- Agent audit log plan.
- Approval routing model.
- Registry health report.

### RISKS

- Multi-agent work may create conflicting edits.
- Tool readiness may be confused with permission to use a tool.
- Login-needed status may tempt account connection automation.

### VALIDATION RULES

- Tool detection must not install software.
- Tool detection must not connect accounts.
- Tool detection must not store credentials.
- Agent delegation must define bounded tasks and files.
- Protected actions remain human-gated.

### DRY_RUN SAFETY CHECKS

- Run tool registry readiness validator.
- Confirm no install commands.
- Confirm no account/auth commands.
- Confirm no secret scan outside approved paths.

### FUTURE APPLY CONDITIONS

- Approval before multi-agent APPLY.
- Approval before commits.
- Approval before any external account interaction.

## PHASE 07 - SIGNAL INTELLIGENCE SYSTEMS

Estimated maturity: 30%.

### STAGE

Develop screener architecture, confluence scoring, strategy registry, regime analysis, backtesting ingestion, Pine integration strategy, data pipelines, and historical replay systems.

### STEPS

- Treat existing signal intelligence and trading lab files as research and validation scaffolds.
- Finalize signal input schema, lifecycle states, rejection reasons, confidence scoring, and paper-trading signal queue.
- Expand strategy registry with versioning, evidence requirements, approval state, invalid strategy handling, and backtest attachment rules.
- Define screener dashboard contract as read-only.
- Define Pine integration as documentation and import/export planning only.
- Build historical replay fixture format and validation rules.
- Build backtesting ingestion readiness without live broker or market data connection.

### EXPECTED OUTPUTS

- Signal schema validation report.
- Strategy registry readiness report.
- Confluence scoring model review.
- Regime analysis validation packet.
- Backtest ingestion fixture.
- Replay schema and sample fixture.

### RISKS

- Strategy confidence may be overstated without statistically valid backtests.
- Pine integration may accidentally imply live trading alerts or webhooks.
- Historical data quality may be UNKNOWN.

### VALIDATION RULES

- No live market data connection unless separately approved.
- No webhook firing.
- No broker routing.
- No strategy activation.
- Backtests must attach evidence and assumptions.
- Data quality issues must be labeled UNKNOWN or INVALID DATA.

### DRY_RUN SAFETY CHECKS

- Validate schemas only.
- Validate fixture data only.
- Confirm execution_allowed remains false.
- Confirm no broker credentials are present or requested.

### FUTURE APPLY CONDITIONS

- Approval for backtest ingestion scripts.
- Approval for any data provider adapter.
- Separate trading governance review before paper-trading automation.

## PHASE 08 - EXECUTION ENGINE

Estimated maturity: 10%.

### STAGE

Plan OANDA integration readiness, webhook validation, risk controls, execution pipeline, trade journaling, fail-safe systems, order routing protections, and broker abstraction layer.

### STEPS

- Keep execution engine as blocked planning until Phases 01-07 pass validation.
- Define broker abstraction layer without credentials or live calls.
- Define OANDA readiness as boundary and contract only.
- Define webhook validation using offline fixtures and signed payload simulation only.
- Define risk controls: max loss, exposure, position size, session lock, news lock, drawdown lock, and kill switch.
- Define trade journaling as paper-trade first.
- Define fail-safe behavior for stale signals, missing approvals, invalid telemetry, invalid risk state, and broker unavailability.

### EXPECTED OUTPUTS

- Execution blocking contract.
- Broker abstraction draft.
- OANDA readiness checklist.
- Webhook validation fixture.
- Risk control design.
- Paper-trade journal schema.
- Fail-safe matrix.

### RISKS

- Any live execution path creates financial and compliance risk.
- Webhooks can become real order triggers if not isolated.
- Credentials may be mishandled.
- Latency optimization may bypass safety controls.

### VALIDATION RULES

- `execution_allowed` remains false until explicit separate approval.
- No broker orders.
- No live trading.
- No credential access.
- No broker routing.
- No webhook firing.
- No auto-routing.

### DRY_RUN SAFETY CHECKS

- Verify trading boundary docs.
- Verify risk controls are design-only.
- Verify no broker tokens or account IDs are used.
- Verify all execution code is absent or disabled.

### FUTURE APPLY CONDITIONS

- Separate human approval after paper-trading evidence.
- Secrets policy approved.
- Broker sandbox only.
- Kill switch tested.
- Risk policy reviewed.
- Audit trail active.

## PHASE 09 - AI VALIDATION LAYER

Estimated maturity: 15%.

### STAGE

Design AI trading bot review engine, signal verification, disagreement handling, confidence scoring, trade blocking logic, and portfolio protection systems.

### STEPS

- Define AI role as reviewer, not executor.
- Require deterministic validators before LLM review.
- Implement signal verification against schema, strategy rules, regime state, backtest evidence, and risk envelope.
- Define disagreement handling between strategy, validator, AI reviewer, and operator.
- Define confidence scoring with explicit uncertainty and rejection reasons.
- Define trade blocking logic when telemetry, approval, risk, or evidence is invalid.
- Define portfolio protection rules before any execution engine is allowed.

### EXPECTED OUTPUTS

- AI validation contract.
- Disagreement handling matrix.
- Confidence scoring rules.
- Trade blocking rules.
- Portfolio protection checklist.
- Review audit fixture.

### RISKS

- LLM output may be treated as trading authority.
- Confidence scores may be poorly calibrated.
- AI validation may hallucinate evidence.
- Portfolio risk may be hidden by single-trade analysis.

### VALIDATION RULES

- AI cannot place trades.
- AI cannot override risk blocks.
- AI cannot access credentials.
- AI claims require source evidence.
- Unknown or conflicting facts block execution.

### DRY_RUN SAFETY CHECKS

- Validate AI review outputs against fixture data only.
- Confirm no broker calls.
- Confirm no live market data requirement.
- Confirm all recommendations are non-executable.

### FUTURE APPLY CONDITIONS

- Approval for AI review prototype.
- Human-reviewed scoring model.
- Negative-case tests for hallucinated signals.
- Audit log before any paper-trade recommendation routing.

## PHASE 10 - AZURE PRODUCTION HARDENING

Estimated maturity: 15%.

### STAGE

Prepare App Services, Key Vault, CI/CD, observability, monitoring, auth systems, scaling, backups, rollback systems, and deployment pipelines.

### STEPS

- Keep Azure work in boundary/readiness mode until approved.
- Define target Azure services: App Service, Key Vault, Application Insights, Log Analytics, Storage, managed identity, and deployment slots.
- Define CI/CD checks before deployment: lint, test, schema validation, safety scan, secret scan, fixture validation, build, package, rollback plan.
- Define auth model with local-first operation and future SSO/OIDC.
- Define observability dashboards and alert routing.
- Define backup and restore policy.
- Define rollback from bad deployment, bad config, bad secret rotation, and bad telemetry collector.

### EXPECTED OUTPUTS

- Azure readiness checklist.
- Key Vault boundary.
- CI/CD pipeline draft.
- Observability plan.
- Auth design draft.
- Backup and rollback plan.
- Deployment runbook.

### RISKS

- Public endpoints may expose unfinished control plane.
- Secrets may enter code or logs.
- CI/CD may deploy unapproved changes.
- Cloud cost and compliance controls may be undefined.

### VALIDATION RULES

- No Azure resource creation until approved.
- No credential storage in repo.
- No deployment.
- No public endpoint.
- No auth bypass.
- No production broker execution.

### DRY_RUN SAFETY CHECKS

- Validate Azure boundary docs.
- Validate no secrets in proposed files.
- Validate deployment scripts are absent or disabled.
- Validate rollback plan exists before any future deployment.

### FUTURE APPLY CONDITIONS

- Human approval for Azure resource plan.
- Key Vault and managed identity design approved.
- CI/CD protected branch rules approved.
- Monitoring, rollback, and backup tested in non-production.

## PHASE 11 - AUTONOMOUS AI_OS OPERATIONS

Estimated maturity: 25%.

### STAGE

Develop self-scaffolding, self-auditing, self-healing systems, autonomous maintenance, AI-generated recovery plans, governance inference systems, and reusable AI_OS bootstrap engine.

### STEPS

- Keep autonomy observe-plan-report first.
- Build self-audit engine around read-only repo scans and validator outputs.
- Build self-healing proposals that never APPLY without approval.
- Build missing-file detection and scaffold proposal generation.
- Build governance inference from approved context packets only.
- Build reusable bootstrap engine for new projects with no self-replication without approval.
- Add stop conditions and escalation rules for conflicts, stale data, protected files, secrets, trading, deployment, and destructive actions.

### EXPECTED OUTPUTS

- Self-audit report.
- Repair proposal draft.
- Missing-file proposal report.
- Bootstrap packet.
- Governance inference report.
- Stop-condition matrix.

### RISKS

- Autonomous repair may damage repo structure.
- Self-scaffolding may create duplicate or conflicting docs.
- Governance inference may hallucinate missing facts.
- Autonomy may bypass human control.

### VALIDATION RULES

- No autonomous APPLY.
- No delete, move, rename, overwrite, reset, clean, push, deploy, secret handling, broker connection, or live trading.
- Every repair proposal must include inspected files, proposed files, risk, validation, unknowns, and approval requirement.

### DRY_RUN SAFETY CHECKS

- Run autonomous readiness validators.
- Confirm proposed changes only.
- Confirm no protected-file mutation.
- Confirm stop conditions are enforced.

### FUTURE APPLY CONDITIONS

- Human approval for each generated scaffold.
- Separate approval for any autonomous maintenance schedule.
- No unattended execution until governance, telemetry, rollback, and audit are production-grade.

## PHASE 12 - COMMERCIALIZATION + PLATFORMIZATION

Estimated maturity: 20%.

### STAGE

Define SaaS considerations, operator onboarding, tenant isolation, licensing concepts, subscription architecture, hosted vs local deployments, customer governance packs, and AI_OS replication templates.

### STEPS

- Keep commercialization as planning until production hardening is complete.
- Define operator onboarding with safety-first training, local-first setup, and approval workflow education.
- Define tenant isolation before any hosted service.
- Define licensing concepts without payment processor integration.
- Define subscription architecture as a future boundary.
- Define hosted vs local deployment tradeoffs.
- Define customer governance packs for non-trading AI_OS use, trading lab use, and broker-execution-prohibited use.
- Define replication templates that preserve local-first governance and human approval gates.

### EXPECTED OUTPUTS

- Commercialization readiness report.
- Operator onboarding plan.
- Tenant isolation draft.
- Licensing boundary draft.
- Hosted/local deployment decision matrix.
- Customer governance pack outline.
- Replication template boundary.

### RISKS

- Selling before production readiness creates trust, compliance, and safety risk.
- Multi-tenant data isolation is not optional for SaaS.
- Trading-related claims can create regulatory risk.
- Hosted AI_OS may require stronger auth, privacy, retention, incident response, and support operations.

### VALIDATION RULES

- No payment integration.
- No customer data collection.
- No hosted deployment.
- No trading performance claims.
- No live trading product promise.
- No tenant sharing of data, logs, prompts, or telemetry.

### DRY_RUN SAFETY CHECKS

- Confirm commercialization docs are planning-only.
- Confirm no payment API, account connection, or customer data path.
- Confirm no production deployment.
- Confirm no trading claims.

### FUTURE APPLY CONDITIONS

- Production hardening complete.
- Legal/compliance review.
- Privacy model approved.
- Support and incident processes defined.
- Tenant isolation tested.

## Critical Blockers

- Root `RISK_POLICY.md` and `ARCHITECTURE.md` remain scaffold-level and need reviewed expansion.
- Azure readiness is boundary-only.
- Dashboard is not production control plane yet.
- Telemetry is preview/fixture-oriented.
- Trading execution is intentionally blocked.
- Secrets handling is policy-first, not production runtime.
- CI/CD and deployment pipelines are not production-ready.
- AI validation is conceptual, not operational.

## Dependency Chains

- Governance -> source-of-truth -> scaffold normalization -> dashboard visibility.
- Dashboard visibility -> telemetry fixtures -> report indexes -> operational scoring.
- Tool registry -> agent boundaries -> approval routing -> multi-agent coordination.
- Signal schemas -> strategy registry -> backtest evidence -> paper-trading readiness.
- Paper-trading evidence -> risk controls -> broker sandbox -> execution engine.
- Secrets/auth/observability/rollback -> Azure deployment -> hosted platform.
- Self-audit -> repair proposals -> bootstrap engine -> controlled autonomy.

## Never Automate

- Broker order placement.
- Live trading enablement.
- Credential, secret, token, private key, or recovery key handling.
- Windows registry, BitLocker, BIOS/UEFI, firewall, VPN, browser policy, or OS security changes.
- Delete, move, rename, reset, clean, or destructive cleanup.
- Public deployment.
- Account connection or OAuth flow.
- Git push, merge, or PR approval.

## Always Human Approval

- APPLY mode.
- Protected file edits.
- Commit, push, merge, PR creation, PR approval.
- Deployment.
- Secrets policy changes.
- Auth changes.
- Broker, trading, webhook, order-routing, or strategy activation work.
- Report writers and telemetry persistence.
- Azure resource creation.
- Multi-agent APPLY.

## Eventually Semi-Autonomous

- Read-only repo scans.
- Fixture validation.
- Schema validation.
- Checkpoint draft generation.
- Daily report draft generation.
- Dashboard stale-data detection.
- Missing-file proposal generation.
- Non-destructive recovery plan generation.
- Source-of-truth index refresh proposals.

## Production-Grade Path Estimate

- Governance and scaffold normalization: near-term.
- Dashboard fixture control plane: near-term.
- Reporting and telemetry preview engine: near-term to mid-term.
- Signal and backtesting systems: mid-term.
- AI validation and paper-trading readiness: mid-term.
- Broker sandbox and execution readiness: late-stage and high-control.
- Azure production deployment: late-stage after auth, secrets, observability, rollback, and CI/CD.
- Commercial platformization: final stage after production, compliance, tenant isolation, and support operations.
