# AIOS Bridge Hardening Next Lane Decision 2026-06-08

Status: DRY_RUN evidence, not authority.

## Source Evidence

- Repo root: `C:\Dev\Ai.Os`
- Branch observed: `main`
- Bridge command run: `python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .`
- Bridge result folder: `Reports/phase_0_to_4_bridge/`
- Bridge recommendation source: `Reports/phase_0_to_4_bridge/phase4_self_build_inspection.json`
- Approval authority source: `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- Apply gate source: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- Worker inbox source: `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- Night Supervisor source: `automation/orchestration/night_supervisor/README.md`

## Bridge Health Result

The documented bridge DRY_RUN command completed with `COMPLETE_NO_COMMIT_NO_PUSH`.
It refreshed generated evidence under `Reports/phase_0_to_4_bridge/` and validator projection evidence under `telemetry/validator_results/`.

Safe for daily start: yes as an explicit DRY_RUN health command, but not yet as a mandatory hook or automatic startup mutation.
Reason: the command refreshes timestamped/generated report content, which is useful evidence but creates working tree churn while those outputs remain tracked.

## Three Recommendations Reviewed

1. `AIOS-SB-001` - Add approval inbox schema validator.
   Decision: `BUILD_NOW`.
   Reason: highest coordination value with low operator burden. It validates the canonical approval inbox before any promotion, worker routing, or Night Supervisor display depends on it.

2. `AIOS-SB-002` - Wire validator registry into bridge status.
   Decision: `DEFER`.
   Reason: useful, but it depends on trustworthy approval and status summaries. It also touches bridge status behavior more directly.

3. `AIOS-SB-003` - Keep live broker execution blocked.
   Decision: `REJECT` as a build lane; keep as standing safety boundary.
   Reason: it is already blocked by root authority and is not an APPLY build candidate.

## Selected Lane

Selected lane: `APPROVAL_INBOX_SCHEMA_VALIDATOR_ONLY`.

This lane is derived from bridge recommendation `AIOS-SB-001`. It should build a local validator that reads canonical approval inbox files and reports schema/status issues without mutating approvals. The validator output can later feed the daily bridge summary, Night Supervisor preview, and Codex startup status.

Likely affected files for the next APPLY packet:

- `automation/validators/aios_approval_inbox_schema_validator.py`
- `tests/governance/test_approval_inbox_schema_validator.py`
- `Reports/phase_0_to_4_bridge/approval_inbox_schema_validator_dry_run.example.json`

Validation plan:

- `python -m py_compile automation/validators/aios_approval_inbox_schema_validator.py`
- `python -m pytest tests/governance`
- `python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .`
- `git diff --check`

APPLY approval requirements:

- Human Owner approval before APPLY.
- Exact allowed paths limited to `automation/validators/`, `tests/governance/`, and `Reports/phase_0_to_4_bridge/`.
- No approval inbox mutation.
- No worker queue mutation.
- No Night Supervisor runtime mutation.
- No hook installation.
- No commit or push.

Rollback plan:

- Revert only the newly created validator, test, and generated example report from the packet scope.
- Do not edit or roll back `automation/orchestration/approval_inbox/` state unless separately approved.

## Local Hook Decision

Install now: no.

Useful hook: `.githooks/pre-commit` running `python automation/validators/aios_governance_validator.py --sample-check`.

DRY_RUN installer result: `scripts/hooks/Install-AiOsGitHooks.ps1 -Mode DRY_RUN` printed source and target only and installed nothing.

Annoyance assessment:

- Blocking normal note-taking: low if opt-in, medium if mandatory.
- Blocking Reports generation: possible if generated reports are tracked and timestamp churn is common.
- Noise risk: medium until Reports/telemetry tracking policy is split.
- Runtime cost: low for sample governance check, unknown for broader validator chains.
- Bypass: possible by not installing the hook; mandatory bypass policy should require Human Owner approval.

Recommendation: keep hooks opt-in. Do not make them mandatory until generated output tracking is settled.

## Reports And Telemetry Tracking Decision

Current state:

- `.gitignore` already ignores many generated daily, dispatcher, work intelligence, relay, morning digest, and Night Supervisor telemetry paths.
- `Reports/phase_0_to_4_bridge/*.json` and `Reports/phase_0_to_4_bridge/*.md` are currently tracked or trackable and are refreshed by the bridge.
- `telemetry/night_supervisor/` is ignored.
- `telemetry/validator_results/AIOS_VALIDATOR_REGISTRY.current.json` is tracked and refreshed by the bridge.

Recommended policy: split policy.

- Track templates, schemas, validators, README policies, and stable example fixtures.
- Ignore run logs, daily generated telemetry, bridge health outputs, timestamp-refreshed current projections, bulky snapshots, and local machine outputs.

Change needed: yes, but not in this DRY_RUN lane.

Proposed future migration:

- Keep bridge code and example fixtures tracked.
- Move or ignore timestamp-refreshed bridge run outputs after a separate retention decision.
- Preserve one stable example bridge output fixture if tests need it.

Risks:

- If left tracked, bridge daily health creates recurring dirty files.
- If ignored too broadly, useful evidence history can disappear from review.

## Approval Inbox And Worker Queue Wiring

Current state:

- Canonical approval inbox exists at `automation/orchestration/approval_inbox/`.
- `APPROVAL_INBOX_001.json` records active approval authority and completed authority repair.
- `APPLY_APPROVAL_GATE_001.json` is `pending_review` with `approved_mode` set to `DRY_RUN_ONLY`.
- Approval inbox summary command reports pending review and no approved actions.
- Worker registry and worker inbox exist under `automation/orchestration/workers/`.
- Worker inbox currently contains completed items only.
- Night Supervisor can classify approval inbox and write sandbox resume evidence, but active state mutation still requires separate approval.

Proposed wiring:

- Add the approval inbox schema validator first.
- Feed validator status into the bridge summary as evidence only.
- Later update the daily/start summary to show current branch, dirty state, pending approvals, worker inbox count, lock status, last bridge health result, and one next safe command.
- Keep Night Supervisor writes sandboxed under `telemetry/night_supervisor/`.

Files drafted:

- `automation/orchestration/work_packets/proposed/AIOS-SB-001-APPROVAL-INBOX-SCHEMA-VALIDATOR-DRY-RUN-FIRST.md`

## Addendum: App Service Bridge Inspection

Question inspected: whether AI_OS already has an app-service/control-plane layer between ChatGPT/OpenAI/Codex and the repo worker system.

Current state:

- `services/orchestrator/index.js` is an existing local Express control-plane reader with `/api/health`, `/api/runtime/status`, `/api/runtime/queue`, `/api/runtime/audit`, `/api/runtime/health`, `/api/runtime/visibility`, and `/api/runtime/control`.
- `services/dispatcher/` contains TypeScript queue, dispatcher, approval, lease, and runtime modules, but it is not exposed as the unified ChatGPT/OpenAI/Codex bridge.
- `services/python_supervisor/autonomy_bridge.py` reads local evidence and writes sandbox projections, but it is not an HTTP app-service intake layer.
- `automation/orchestration/openai_api_bridge/` and `docs/AI_OS/dispatch/AIOS_OPENAI_PACKET_DISPATCH_FLOW.md` define fixture/preview OpenAI packet routing, not a live app service.
- `docs/roadmap/AIOS_FULL_AUTONOMY_BRIDGE_MAP.md` identifies cross-system gaps between TypeScript services, Python supervisor, approval inbox, worker queue, Night Supervisor outputs, and telemetry.

Gap:

AI_OS has partial local control-plane pieces, but no single local-first app-service bridge that accepts inert packet drafts, exposes canonical queue/approval/worker/lock/report status, records DRY_RUN-only local state, and emits SOS-only notification previews.

Candidate lane:

`AI_OS_APP_SERVICE_BRIDGE_V0`

Decision:

`BUILD_NOW`, as a proposed packet only. This supersedes hooks as the higher-value next bridge-hardening lane, while keeping `AIOS-SB-001` as a prerequisite validator inside the app-service lane.

Reason:

The app-service bridge is the missing coordination layer between ChatGPT/OpenAI/Codex inputs and the repo worker system. Hooks only protect Git edges after work is already happening. The app-service bridge can reduce copy/paste burden, centralize DRY_RUN validation, and make Night Supervisor/Codex startup status useful without enabling APPLY.

Recommended implementation direction:

- Extend existing repo-native `services/orchestrator` Express service first.
- Do not create a competing FastAPI service unless the existing service is rejected in a later design review.
- Use local JSONL state under a generated-output telemetry root for DRY_RUN receipts.
- Keep POST endpoints preview-only until Human Owner separately approves any APPLY mutation.

Minimal endpoint proposal:

- `GET /health`
- `POST /packets`
- `GET /queue`
- `POST /approvals`
- `GET /workers`
- `GET /reports/latest`
- `POST /sos`

Boundary:

- No cloud hosting.
- No Azure deployment.
- No tunnels.
- No live model provider calls in v0.
- No secret storage.
- No approval inbox mutation.
- No worker queue mutation.
- No automatic APPLY.
- No live trading or broker runtime work.

Build order answer:

- A. built before hooks: yes.
- B. built after hooks: no.
- C. built before Azure/cloud deployment: yes.
- D. blocked by existing repo rules: no, if local-first, DRY_RUN-first, no secrets, no cloud, no protected mutations, and Human Owner approval is required before APPLY.

Packet drafted:

- `automation/orchestration/work_packets/proposed/AIOS-APP-SERVICE-BRIDGE-V0-DRY-RUN-FIRST.md`
