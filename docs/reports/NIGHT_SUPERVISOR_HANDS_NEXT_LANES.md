# Night Supervisor Hands Next Lanes

## Ranking Rule

These lanes are ranked from current repo evidence. Broad investigation lanes are excluded because the implemented dispatcher preview chain now provides concrete next integration points.

`AIOS-COMMIT-PACKAGE-PREVIEW-APPLY-001` is not ranked as next because commit package preview is already implemented at `services/dispatcher/commitPackagePreview.ts` and committed in `107f341 Add commit package preview`.

## 1. AIOS-NIGHT-SUPERVISOR-CONSUMES-DISPATCHER-PREVIEWS-APPLY-001

- Purpose: Add a read-only Night Supervisor consumer/read model that chains existing dispatcher previews into one supervised overnight handoff view.
- Exact human step removed: Operator no longer manually walks queue projection, scheduler preview, worker resolver preview, assignment preview, validator evidence, approval preview, and commit preview outputs one layer at a time.
- Exact human gate preserved: Human still approves runtime mutation, worker dispatch, packet mutation, queue mutation, approvals, commits, pushes, merges, deployments, and protected actions.
- Expected files: `schemas/aios/orchestration/night_supervisor_dispatcher_preview.schema.json`, `services/dispatcher/nightSupervisorDispatcherPreview.ts`, `tests/dispatcher/nightSupervisorDispatcherPreview.test.ts`, `docs/reports/NIGHT_SUPERVISOR_DISPATCHER_PREVIEW_APPLY_SUMMARY.md`
- Forbidden paths: `automation/`, `runtime/`, `telemetry/`, `apps/`, `scripts/`, `trading/`, `broker/`, `OANDA/`, `secrets/`, `credentials/`, `services/runtime/`, `services/supervisor/`, `services/orchestrator/`, packet/queue/worker inbox paths.
- Validators required: JSON parse checks; dispatcher tests; forbidden path check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes; no main push or merge.
- Why this lane is next: The preview layers exist but are still disconnected from Night Supervisor.

## 2. AIOS-AUTONOMY-SCORECARD-FOUNDATION-APPLY-001

- Purpose: Create the first machine-readable scorecard over preview-chain readiness, human coordination removed, human gates preserved, blocked items, and next-lane maturity.
- Exact human step removed: Operator no longer manually estimates whether AI_OS autonomy improved after each preview-lane commit.
- Exact human gate preserved: Human defines safe thresholds and remains authority over approvals, commits, pushes, merges, deployments, and protected actions.
- Expected files: `schemas/aios/orchestration/autonomy_scorecard_foundation.schema.json`, `services/dispatcher/autonomyScorecardFoundation.ts` or docs-only equivalent if code is not authorized, `tests/dispatcher/autonomyScorecardFoundation.test.ts` if code is authorized, `docs/reports/AUTONOMY_SCORECARD_FOUNDATION_APPLY_SUMMARY.md`
- Forbidden paths: Runtime, telemetry mutation, automation state, packet files, queue files, worker inboxes, trading, broker, secrets, credentials.
- Validators required: JSON parse checks; relevant dispatcher tests if code is created; forbidden path check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes.
- Why this lane is next: Night Supervisor needs measurable readiness and operator-load reduction, not another roadmap.

## 3. AIOS-SOS-ESCALATION-POLICY-APPLY-001

- Purpose: Define the canonical SOS escalation policy that separates routine recoverable issues from wake-the-operator conditions.
- Exact human step removed: Operator no longer manually interprets every failure class as either routine, blocked, or emergency.
- Exact human gate preserved: Human defines and approves the SOS policy and remains authority for steel-door actions.
- Expected files: `docs/security/sos-escalation-policy.md` and possibly `schemas/aios/orchestration/sos_escalation_policy.schema.json` if schema scope is authorized.
- Forbidden paths: Runtime code, telemetry mutation, packet mutation, queue mutation, worker dispatch, trading, broker, secrets, credentials.
- Validators required: `git diff --check`; JSON parse if schema is created; forbidden path check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes and security-docs write boundary is explicitly authorized.
- Why this lane is next: Night Supervisor cannot be SOS-only until SOS is explicitly defined.

## 4. AIOS-RECOVERY-SUPERVISOR-EVIDENCE-READMODEL-APPLY-001

- Purpose: Add a read-only recovery evidence model that classifies stale workers, lost packets, failed validations, and blocked preview outputs without mutating runtime.
- Exact human step removed: Operator no longer manually collects recovery-relevant facts before deciding whether a state is recoverable or SOS.
- Exact human gate preserved: Human approves recovery mutation, quarantine, retry, runtime writes, and protected action decisions.
- Expected files: `schemas/aios/orchestration/recovery_supervisor_evidence_readmodel.schema.json`, a read-only service module if authorized, tests if code is authorized, `docs/reports/RECOVERY_SUPERVISOR_EVIDENCE_READMODEL_APPLY_SUMMARY.md`
- Forbidden paths: Runtime mutation, telemetry mutation, packet mutation, queue mutation, worker inbox mutation, trading, broker, secrets, credentials.
- Validators required: JSON parse checks; relevant tests if code is created; forbidden path check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes.
- Why this lane is next: Overnight work must fail into evidence-backed recovery states instead of requiring operator reconstruction.

## 5. AIOS-SELF-AUDIT-DRIFT-READMODEL-APPLY-001

- Purpose: Create a read-only self-audit drift model over authority references, implemented preview chain files, schemas, and known protected zones.
- Exact human step removed: Operator no longer manually checks whether preview-chain docs, schemas, and service files drifted out of sync.
- Exact human gate preserved: Human approves any cleanup, archive, delete, promotion, or protected edit.
- Expected files: `schemas/aios/orchestration/self_audit_drift_readmodel.schema.json`, optional read-only service/test files if authorized, `docs/reports/SELF_AUDIT_DRIFT_READMODEL_APPLY_SUMMARY.md`
- Forbidden paths: Runtime mutation, telemetry mutation, packet mutation, queue mutation, worker mutation, trading, broker, secrets, credentials.
- Validators required: JSON parse checks; relevant tests if code is created; forbidden path check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes.
- Why this lane is next: Night Supervisor needs drift detection before trusting overnight state.

## 6. AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001

- Purpose: Document MCP safe-hands placement, local read-only filesystem on-ramp, and steel-door exclusions after internal state continuity is stable.
- Exact human step removed: Operator no longer explains MCP safety boundaries from memory.
- Exact human gate preserved: Operator manually installs and tests MCP servers; agents do not install, widen access, or touch dangerous tools.
- Expected files: `docs/architecture/toolchain-mcp-safe-hands.md` or an update to the existing canonical architecture doc if it already owns the topic.
- Forbidden paths: MCP server code, package installs, runtime, telemetry mutation, packet mutation, queue mutation, trading, broker, secrets, credentials.
- Validators required: `git diff --check`; duplicate-intent check; scoped status check.
- Commit/push rule: Commit and branch push only after validation passes.
- Why this lane is later: External hands should come after the internal preview and Night Supervisor state chain is stable.
