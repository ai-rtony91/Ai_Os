# Night Supervisor Hands Checklist

## Purpose

This checklist converts the historical autonomy architecture direction into current repo-grounded execution status for Night Supervisor readiness.

Repo evidence wins over old architecture assumptions. Completed preview commits now prove that several previously missing glue layers exist as read-only or preview-only artifacts.

## Current Implemented Chain

1. Canonical Queue Projection - `services/dispatcher/canonicalQueueProjection.ts`
2. Scheduler Preview - `services/dispatcher/schedulerPreview.ts`
3. Worker Resolver Preview - `services/dispatcher/workerResolverPreview.ts`
4. Assignment Preview Persistence - `services/dispatcher/assignmentPreviewPersistence.ts`
5. Validator Evidence Attachment - `services/dispatcher/validatorEvidenceAttachment.ts`
6. Approval Package Preview - `services/dispatcher/approvalPackagePreview.ts`
7. Commit Package Preview - `services/dispatcher/commitPackagePreview.ts`

All seven layers are preview/read-only glue. They reduce operator translation work but do not dispatch workers, mutate runtime state, mutate packets, mutate queues, mutate telemetry, approve work, commit, push, merge, deploy, trade, or access secrets.

## Checklist

### A. Authority / Source of Truth

- Status: PARTIAL
- Evidence path: `AGENTS.md`, `README.md`, `WHITEPAPER.md`, `docs/governance/source-of-truth-map.md`, `docs/audits/active-system-map.md`
- What it does: Defines active repo identity, protected boundaries, source-of-truth precedence, active system map, and no-live-trading posture.
- What it deliberately does not do: It does not execute work, route packets, mutate runtime, or replace human judgment.
- Human step removed by current layer: Reduces repeated orientation and stale-path interpretation.
- Human gate preserved: Human remains authority for approval, commit, push, merge, protected files, runtime mutation, and trading boundaries.
- Current limitation: Authority is still split across several documents and not loaded as one machine-readable runtime model.
- Remaining gap after layer: Build repo memory/knowledge graph read model.
- Original architecture-doc claim: AI_OS needed a canonical map before autonomy.
- Current repo reality: Authority documents exist and are actively used, but not yet a queryable graph.
- Corrected priority: High, but implement as read model, not another broad report.
- Next APPLY lane if any: `AIOS-KNOWLEDGE-GRAPH-READMODEL-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor must know which rules and paths are authoritative before acting.

### B. Knowledge Graph / Repo Memory

- Status: PARTIAL
- Evidence path: `docs/governance/source-of-truth-map.md`, `docs/audits/active-system-map.md`, `docs/reports/MASTER_RECONCILIATION_ROADMAP.md`
- What it does: Human-readable maps identify active systems, dangerous zones, and duplicate authority.
- What it deliberately does not do: It does not provide a single queryable runtime artifact.
- Human step removed by current layer: Reduces manual source-of-truth discovery.
- Human gate preserved: Human approves promotion, cleanup, archive, and protected-path decisions.
- Current limitation: No canonical JSON/read-model graph for Codex or Night Supervisor startup.
- Remaining gap after layer: Machine-readable repo memory with systems, owners, dependencies, protected assets, and decision records.
- Original architecture-doc claim: Knowledge graph was the first foundation.
- Current repo reality: Strong evidence exists, but it is document-shaped rather than runtime-loadable.
- Corrected priority: High after current dispatcher preview chain is consolidated.
- Next APPLY lane if any: `AIOS-KNOWLEDGE-GRAPH-READMODEL-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor cannot safely choose next actions if it must rediscover ownership each run.

### C. Event System

- Status: PARTIAL
- Evidence path: `schemas/aios/orchestration/EVENT_SCHEMA.md`, `services/runtime/`, `telemetry/`
- What it does: Existing runtime and telemetry surfaces imply event-like activity and state records.
- What it deliberately does not do: Current dispatcher preview chain does not emit or consume events.
- Human step removed by current layer: None yet for closed-loop Night Supervisor handoff.
- Human gate preserved: Human controls any runtime/event integration.
- Current limitation: No active append-only event bus connecting packet, scheduler, resolver, validation, approval, commit preview, recovery, and scorecard.
- Remaining gap after layer: Event read model and event contracts for preview output consumption.
- Original architecture-doc claim: Event system is the nervous system for autonomy.
- Current repo reality: Event schema material exists, but the current chain is pure function output and not event-driven.
- Corrected priority: Medium-high after Night Supervisor can consume preview artifacts.
- Next APPLY lane if any: `AIOS-EVENT-READMODEL-PREVIEW-APPLY-001`
- Why it matters to supervised overnight development: Overnight work needs facts to trigger downstream preview generation without a human relay.

### D. Packet / Work Packet System

- Status: PARTIAL
- Evidence path: `automation/orchestration/work_packets/`, `schemas/aios/orchestration/AIOS_CLOSED_LOOP_STATE_CONTRACT_V1.schema.json`
- What it does: Work packet folders and state contract define packet lifecycle concepts.
- What it deliberately does not do: Current checklist lane does not mutate packet files.
- Human step removed by current layer: Canonical Queue Projection reduces manual packet state normalization.
- Human gate preserved: Human approves packet mutation and lifecycle transitions.
- Current limitation: Packet state remains operational state outside the preview-only dispatcher chain.
- Remaining gap after layer: Safe preview consumption and later approved persistence writers.
- Original architecture-doc claim: One durable queue/work packet unit is needed.
- Current repo reality: Packet system exists, but closed-loop preview layers deliberately do not write to it.
- Corrected priority: Keep packet mutation blocked until preview consumption and evidence gates are stable.
- Next APPLY lane if any: `AIOS-NIGHT-SUPERVISOR-CONSUMES-DISPATCHER-PREVIEWS-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor needs packet facts without altering packet state.

### E. Canonical Queue Projection

- Status: DONE
- Evidence path: `services/dispatcher/canonicalQueueProjection.ts`, `schemas/aios/orchestration/canonical_queue_projection.schema.json`, `tests/dispatcher/canonicalQueueProjection.test.ts`
- What it does: Reads packet JSON from a provided root and projects normalized queue state, risk, path, dependency, scheduler eligibility, resolver eligibility, warnings, and summary.
- What it deliberately does not do: Does not mutate packets, queues, telemetry, runtime, workers, approvals, commits, pushes, merges, or trading paths.
- Human step removed by current layer: Operator no longer manually normalizes packet state into scheduler-ready queue facts.
- Human gate preserved: Human still approves packet and queue mutation.
- Current limitation: It is a projection function, not a durable queue writer.
- Remaining gap after layer: Night Supervisor must consume projection output without treating it as mutation authority.
- Original architecture-doc claim: Queue/scheduler substrate was missing.
- Current repo reality: Read-only queue projection is implemented.
- Corrected priority: Done as preview layer; do not rebuild.
- Next APPLY lane if any: None for projection itself.
- Why it matters to supervised overnight development: Night Supervisor needs a safe, normalized packet view before recommending work.

### F. Scheduler Preview

- Status: DONE
- Evidence path: `services/dispatcher/schedulerPreview.ts`, `tests/dispatcher/schedulerPreview.test.ts`
- What it does: Consumes canonical queue projection and produces ready packet order plus worker capability requirements.
- What it deliberately does not do: Does not execute schedules, mutate queues, dispatch workers, or persist actions.
- Human step removed by current layer: Operator no longer manually ranks scheduler-ready packets.
- Human gate preserved: Human still controls execution and any queue state transition.
- Current limitation: No runtime scheduler hookup or event trigger.
- Remaining gap after layer: Night Supervisor must read scheduler preview results as recommendations only.
- Original architecture-doc claim: Task queue and scheduler were foundational and mostly missing.
- Current repo reality: Scheduler preview exists as pure read-only planning output.
- Corrected priority: Done as preview layer; next work is consumption, not scheduler rewrite.
- Next APPLY lane if any: None for scheduler preview itself.
- Why it matters to supervised overnight development: It orders safe candidate work without launching it.

### G. Worker Resolver Preview

- Status: DONE
- Evidence path: `services/dispatcher/workerResolverPreview.ts`, `schemas/aios/orchestration/worker_resolver_preview.schema.json`, `tests/dispatcher/workerResolverPreview.test.ts`
- What it does: Consumes scheduler preview actions and provided worker capability data, scores active workers, and recommends preview-only assignments.
- What it deliberately does not do: Does not read registries directly, write inboxes, dispatch workers, launch Codex, or persist assignment.
- Human step removed by current layer: Operator no longer manually translates scheduler actions into worker match recommendations.
- Human gate preserved: Human still approves assignment persistence, worker dispatch, and protected actions.
- Current limitation: Worker registry duplication remains an operational concern outside this pure resolver.
- Remaining gap after layer: Approved consumer must pass worker data and preserve preview-only status.
- Original architecture-doc claim: Duplicate worker registries blocked trustworthy routing.
- Current repo reality: Resolver now avoids direct registry reads, so registry consolidation is no longer a prerequisite for this preview layer; registry ownership still needs future cleanup.
- Corrected priority: Done for preview; registry consolidation remains separate.
- Next APPLY lane if any: `AIOS-WORKER-REGISTRY-READMODEL-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor can recommend who could take work without dispatching anyone.

### H. Assignment Preview Persistence

- Status: DONE
- Evidence path: `services/dispatcher/assignmentPreviewPersistence.ts`, `schemas/aios/orchestration/assignment_preview_persistence.schema.json`, `tests/dispatcher/assignmentPreviewPersistence.test.ts`
- What it does: Converts worker resolver preview output into a durable, schema-shaped preview assignment record.
- What it deliberately does not do: Does not persist to worker inbox, dispatch, approve, commit, push, or mutate runtime.
- Human step removed by current layer: Operator no longer manually translates worker resolver preview output into durable preview-record shape.
- Human gate preserved: Human still approves assignment persistence into operational inbox/state in a future lane.
- Current limitation: Record is returned by pure function and not written to an operational store.
- Remaining gap after layer: Night Supervisor needs a safe reader/consumer path for this record.
- Original architecture-doc claim: Assignment persistence was missing.
- Current repo reality: Preview persistence exists and is explicitly non-operational.
- Corrected priority: Done for preview; do not add inbox writing until later gated lane.
- Next APPLY lane if any: None for preview persistence itself.
- Why it matters to supervised overnight development: It stabilizes assignment recommendations for review without creating real assignments.

### I. Validator Evidence Attachment

- Status: DONE
- Evidence path: `services/dispatcher/validatorEvidenceAttachment.ts`, `schemas/aios/orchestration/validator_evidence_attachment.schema.json`, `tests/dispatcher/validatorEvidenceAttachment.test.ts`
- What it does: Consumes assignment preview persistence and provided validator results, groups packet evidence, and computes approval readiness.
- What it deliberately does not do: Does not run validators, write telemetry, mutate packets, mutate queues, approve, commit, push, or dispatch.
- Human step removed by current layer: Operator no longer manually gathers validator results and maps them to assignment preview packet evidence.
- Human gate preserved: Human still approves approval packages, commit packages, commits, pushes, merges, runtime mutation, worker dispatch, and protected actions.
- Current limitation: Requires caller-provided validator results.
- Remaining gap after layer: Validator routing/execution and evidence persistence remain future lanes.
- Original architecture-doc claim: Validator routing and evidence were missing.
- Current repo reality: Evidence attachment is implemented; validator execution routing is still missing.
- Corrected priority: Done for evidence normalization; validator routing is separate.
- Next APPLY lane if any: `AIOS-VALIDATOR-ROUTING-PREVIEW-APPLY-001`
- Why it matters to supervised overnight development: Approval and commit previews need packet-scoped evidence instead of terminal text.

### J. Approval Package Preview

- Status: DONE
- Evidence path: `services/dispatcher/approvalPackagePreview.ts`, `schemas/aios/orchestration/approval_package_preview.schema.json`, `tests/dispatcher/approvalPackagePreview.test.ts`
- What it does: Consumes validator evidence attachment, separates approval-ready and blocked packets, and produces preview-only approval items.
- What it deliberately does not do: Does not approve work, mutate approval inbox, commit, push, merge, deploy, or touch runtime.
- Human step removed by current layer: Operator no longer manually assembles approval-ready evidence from validator results.
- Human gate preserved: Human still performs approval decision, commit approval, push approval, merge approval, and protected actions.
- Current limitation: No approval inbox persistence or human decision record writing.
- Remaining gap after layer: Human approval package remains a preview artifact until a gated approval persistence lane exists.
- Original architecture-doc claim: Approval intelligence was missing.
- Current repo reality: Approval package preview exists, but not approval execution or approval inbox mutation.
- Corrected priority: Done for preview; preserve human decision gate.
- Next APPLY lane if any: None for preview itself.
- Why it matters to supervised overnight development: Morning review receives decision-ready evidence instead of scattered validator facts.

### K. Commit Package Preview

- Status: DONE
- Evidence path: `services/dispatcher/commitPackagePreview.ts`, `schemas/aios/orchestration/commit_package_preview.schema.json`, `tests/dispatcher/commitPackagePreview.test.ts`
- What it does: Consumes approval package preview and generates commit candidate metadata, pull request candidate metadata, and validation summary.
- What it deliberately does not do: Does not stage files, create commits, push, merge, deploy, create PRs, or authorize protected actions.
- Human step removed by current layer: Operator no longer manually assembles commit-ready evidence into a reviewable package.
- Human gate preserved: Human still performs commit approval, push approval, merge approval, deployment approval, trading approval, and protected actions.
- Current limitation: Does not inspect Git diffs or decide exact files to stage.
- Remaining gap after layer: Exact-file commit package integration remains a future gated lane.
- Original architecture-doc claim: Commit package builder was partial and evidence chain was open.
- Current repo reality: Preview metadata layer is implemented; exact file staging remains human-gated.
- Corrected priority: Done for preview; next is Night Supervisor consumption.
- Next APPLY lane if any: `AIOS-NIGHT-SUPERVISOR-CONSUMES-DISPATCHER-PREVIEWS-APPLY-001`
- Why it matters to supervised overnight development: It converts validated approval-ready packets into reviewable commit/PR candidates without taking Git authority.

### L. Night Supervisor Connection

- Status: MISSING
- Evidence path: `services/dispatcher/*Preview.ts`, `docs/reports/*_APPLY_SUMMARY.md`
- What it does: Not implemented yet.
- What it deliberately does not do: Must not mutate runtime, queue, packets, telemetry, worker inboxes, or approvals in first lane.
- Human step removed by current layer: None yet.
- Human gate preserved: Human remains approval/commit/push/merge/deploy authority.
- Current limitation: Preview functions exist but Night Supervisor does not yet consume their outputs as a chain.
- Remaining gap after layer: Build a read-only Night Supervisor consumer/read model over dispatcher preview outputs.
- Original architecture-doc claim: Human remained the integration layer.
- Current repo reality: Glue layers exist, but the supervisor connection is still missing.
- Corrected priority: Highest next lane.
- Next APPLY lane if any: `AIOS-NIGHT-SUPERVISOR-CONSUMES-DISPATCHER-PREVIEWS-APPLY-001`
- Why it matters to supervised overnight development: This is the step that turns separate preview modules into one supervised overnight handoff.

### M. Recovery Supervisor

- Status: PARTIAL
- Evidence path: `docs/audits/active-system-map.md`, `automation/orchestration/runtime/`, `services/runtime/`
- What it does: Existing runtime supervisor and recovery-related surfaces are identified in active maps.
- What it deliberately does not do: Current checklist does not inspect or modify runtime recovery behavior.
- Human step removed by current layer: None in the dispatcher preview chain.
- Human gate preserved: Human approves recovery mutation, quarantine changes, and runtime writes.
- Current limitation: No read-only recovery evidence model tied to dispatcher preview outputs.
- Remaining gap after layer: Recovery supervisor evidence read model and SOS classification.
- Original architecture-doc claim: Recovery is the heart of SOS-only operation.
- Current repo reality: Runtime/recovery surfaces exist, but closed-loop recovery evidence is not connected to this preview chain.
- Corrected priority: High after Night Supervisor preview consumption and SOS policy.
- Next APPLY lane if any: `AIOS-RECOVERY-SUPERVISOR-EVIDENCE-READMODEL-APPLY-001`
- Why it matters to supervised overnight development: Overnight work must fail into reviewable, recoverable states.

### N. Self-Audit

- Status: PARTIAL
- Evidence path: `docs/audits/active-system-map.md`, `docs/reports/`
- What it does: Manual audit reports identify drift, duplicate authority, stale areas, and dangerous zones.
- What it deliberately does not do: Does not auto-fix or mutate repo state.
- Human step removed by current layer: Reduces manual drift discovery when reports are current.
- Human gate preserved: Human approves cleanup, archive, delete, promote, and protected edits.
- Current limitation: No scheduled self-audit read model tied to source-of-truth expectations.
- Remaining gap after layer: Self-audit should detect drift and emit preview-only findings.
- Original architecture-doc claim: Self-audit is required before humans notice drift.
- Current repo reality: Audit reports exist; automated self-audit is not implemented in this chain.
- Corrected priority: Medium after supervisor consumption and scorecard foundation.
- Next APPLY lane if any: `AIOS-SELF-AUDIT-DRIFT-READMODEL-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor must detect stale or unsafe state before relying on it.

### O. Autonomy Scorecard

- Status: MISSING
- Evidence path: `docs/reports/COMMIT_PACKAGE_PREVIEW_APPLY_SUMMARY.md`, current preview chain summaries
- What it does: Not implemented yet.
- What it deliberately does not do: Must not claim autonomy success from commits alone or blur human approvals with avoidable coordination work.
- Human step removed by current layer: None yet.
- Human gate preserved: Human defines which metrics are acceptable and which actions remain protected.
- Current limitation: No metric model for manual coordination removed, human gates preserved, preview chain readiness, recovery rate, or operator load.
- Remaining gap after layer: Scorecard foundation over implemented preview chain and known gates.
- Original architecture-doc claim: Measurement is needed so autonomy is not guesswork.
- Current repo reality: Preview chain now gives concrete data points for a first scorecard.
- Corrected priority: Second after Night Supervisor preview consumption.
- Next APPLY lane if any: `AIOS-AUTONOMY-SCORECARD-FOUNDATION-APPLY-001`
- Why it matters to supervised overnight development: The operator needs proof that automation reduces coordination while preserving safety.

### P. MCP Safe Hands

- Status: PARTIAL
- Evidence path: `docs/architecture/toolchain-mcp-safe-hands.md` if present; current prompt context; repo authority files
- What it does: Defines the safe-hands concept when documented.
- What it deliberately does not do: Must not install MCP servers, create connections, expose write tools, or touch secrets/trading/runtime in this checklist lane.
- Human step removed by current layer: None in current repo execution chain.
- Human gate preserved: Operator manually installs/tests MCP tools and approves widening.
- Current limitation: MCP safe-hands documentation may exist in architecture docs, but safe connection implementation is not part of this branch evidence.
- Remaining gap after layer: Confirm/update docs only after internal state continuity is stable.
- Original architecture-doc claim: MCP is the hands layer before autonomy can act.
- Current repo reality: Current closed-loop work has focused on internal preview chain first; this is the safer order before adding external hands.
- Corrected priority: Later, after supervisor consumption and scorecard/SOS foundation.
- Next APPLY lane if any: `AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001`
- Why it matters to supervised overnight development: Agents should only get inspected, limited reach after the internal chain proves safe.

### Q. SOS Escalation Policy

- Status: MISSING
- Evidence path: `docs/security/` authority exists, but this lane cannot edit it
- What it does: Not implemented as a current checklist artifact.
- What it deliberately does not do: Must not auto-escalate, alert, page, or mutate runtime in first pass.
- Human step removed by current layer: None yet.
- Human gate preserved: Human defines what wakes the operator and what remains routine.
- Current limitation: No explicit repo-authority SOS policy file was created in this lane because `docs/security/` is forbidden.
- Remaining gap after layer: A scoped security-docs APPLY must define SOS events and escalation thresholds.
- Original architecture-doc claim: SOS policy should be written first.
- Current repo reality: Dispatcher preview chain advanced first; SOS policy remains missing and should be added next as protected docs lane.
- Corrected priority: High, after or alongside scorecard foundation.
- Next APPLY lane if any: `AIOS-SOS-ESCALATION-POLICY-APPLY-001`
- Why it matters to supervised overnight development: Night Supervisor must know what can be logged silently and what requires human wake-up.

### R. Steel Door / Forbidden Authority

- Status: FORBIDDEN
- Evidence path: `AGENTS.md`, `README.md`, `WHITEPAPER.md`, `schemas/aios/orchestration/*preview*.schema.json`
- What it does: Defines actions the system must not take automatically.
- What it deliberately does not do: It does not grant exceptions based on confidence, test pass, or worker capability.
- Human step removed by current layer: None; this is a permanent safety boundary.
- Human gate preserved: Human owns live trading execution, broker execution, OANDA execution, secret access, credential access, push to protected main, production deployment, autonomous merge, and approval.
- Current limitation: Steel-door rules exist across authority files and schemas; a central SOS/steel-door machine-readable policy would improve enforcement.
- Remaining gap after layer: Central protected-action read model/policy can be added only in a scoped governance/security lane.
- Original architecture-doc claim: The steel door never moves.
- Current repo reality: Every implemented preview schema preserves the steel door with explicit non-authority language.
- Corrected priority: Permanent non-negotiable boundary, not a lane to automate through.
- Next APPLY lane if any: `AIOS-SOS-ESCALATION-POLICY-APPLY-001`
- Why it matters to supervised overnight development: It keeps overnight autonomy limited to reversible preparation work.

## Summary

- Done: Canonical Queue Projection, Scheduler Preview, Worker Resolver Preview, Assignment Preview Persistence, Validator Evidence Attachment, Approval Package Preview, Commit Package Preview.
- Partial: Authority/Source of Truth, Knowledge Graph/Repo Memory, Event System, Packet/Work Packet System, Recovery Supervisor, Self-Audit, MCP Safe Hands.
- Missing: Night Supervisor Connection, Autonomy Scorecard, SOS Escalation Policy.
- Forbidden: Steel-door authority remains permanently human-controlled.

## Exact Human Step This Checklist Removes

Operator no longer has to manually reconcile the original autonomy architecture documents against the current implemented dispatcher preview chain to determine what remains before Night Supervisor can safely consume the chain.

## Human Gate Preserved

Human still approves runtime mutation, packet mutation, queue mutation, telemetry mutation, worker dispatch, approval decisions, commit approval, push approval, merge approval, deployment approval, trading approval, broker execution, secret access, credential access, and protected actions.
