CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_CODEX_DRY_RUN_PACKET

SUPERVISOR IDENTITY:
ChatGPT Planning Supervisor under Anthony Human Owner

WORKER IDENTITY:
Codex local inspector operating inside C:\Dev\Ai.Os

PACKET ID:
PKT-CREW-CAMPAIGN-BRIDGE-DRYRUN

MODE:
DRY_RUN

ZONE:
ORCHESTRATION_CREW_CAMPAIGN_BRIDGE

LANE:
CREW_CORE_CAMPAIGN_BRIDGE_INSPECTION

WORKTREE:
C:\Dev\Ai.Os

BRANCH:
main

LOCK ID:
AIOS-LOCK-CREW-CAMPAIGN-BRIDGE-DRYRUN-20260612

MISSION CONTEXT:
This packet is part of the AI_OS cleanup and build sequence to reduce repo clutter, clean stale state, organize authority and packet flow, improve validation accuracy, and prepare AI_OS for future web-first dashboard work, Cloudflare privacy/login gates, and later game-style trading visualization layers.

Preserve paper-only Trading Lab safety. Do not implement live trading, broker execution, real orders, real webhooks, credentials, secrets, or UE5 work.

APPROVAL AUTHORITY:
Anthony approves DRY_RUN inspection only.

This approval does not include file edits, file creation, file moves, staging, commit, push, merge, deploy, worker assignment, worker claim, lock claim, lock release, campaign registry mutation, queue mutation, packet movement, approval mutation, runtime mutation, telemetry mutation, Reports mutation, dashboard mutation, broker/live trading behavior, real orders, real webhooks, credentials, secrets, or UE5 implementation.

MISSION:
Inspect the Crew Core Campaign Bridge recommendation and determine what AI_OS is trying to connect next. Map the bridge between crew helpers, campaign registry, worker identity, lock/collision validators, and work packet state. Produce the next safe APPLY or DRY_RUN recommendation without mutating state.

Known prior evidence to verify, not trust blindly:

* `CAMPAIGN-CREW-CORE` is READY and high priority.
* `EAST_OCC_01` is recommended as a temporary East worker identity.
* Active and approved work packet queues were empty.
* Lock registry had no active locks.
* Worker claim registry contained a placeholder claim warning.
* `EAST_OCC_01` was absent from active worker registries.
* Crew APPLY readiness remained blocked pending separate approval and cleanup.

STOP POINT:
Stop after final DRY_RUN report and proposed next packet. Do not mutate anything.

VALIDATOR CHAIN:

* repo path check
* branch check
* clean working tree check
* main synced check
* authority readback
* current AIOS status reproduction
* crew assignment recommendation
* crew integration recommendation
* campaign registry inspection
* campaign schema inspection
* worker registry inspection
* window identity registry inspection
* worker claim collision readback
* lock registry integrity readback
* worker lock status readback
* active/approved/proposed packet state readback
* safe next-lane recommendation
* no-mutation verification
* final git status

PREFLIGHT:
Run from PowerShell inside `C:\Dev\Ai.Os`:

```powershell
cd C:\Dev\Ai.Os
pwd
git status --short --branch
git branch --show-current
git remote -v
git rev-parse --show-toplevel
git fetch origin --prune
git status --short --branch
git log --oneline -12
```

Required:

* repo path: `C:\Dev\Ai.Os`
* branch: `main`
* working tree: clean
* main synced with `origin/main`
* latest main includes PR #597 merge

If path mismatch, branch mismatch, dirty state, or unsynced main is found, stop BLOCKED and report exact evidence.

READ BEFORE INSPECTION:

* `AGENTS.md`
* `README.md`
* `RISK_POLICY.md`
* `docs/governance/source-of-truth-map.md`
* `docs/audits/active-system-map.md`
* `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
* `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` if present
* `docs/governance/aios-identity-and-lane-governance.md` if present
* `automation/orchestration/README.md` if present

ALLOWED INSPECTION PATHS:

* `automation/orchestration/crew/**`
* `automation/orchestration/campaign_registry/**`
* `automation/orchestration/workers/**`
* `automation/window_identity/**`
* `automation/orchestration/claims/**`
* `automation/orchestration/locks/**`
* `automation/orchestration/work_packets/**`
* `automation/orchestration/validators/**`
* `automation/orchestration/approval_inbox/**`
* `docs/workflows/**`
* `docs/governance/**`
* `docs/audits/**`
* `schemas/aios/orchestration/**`
* `aios.ps1`

FORBIDDEN MUTATION PATHS:

* every path in the repository

FORBIDDEN ACTIONS:

* no file edits
* no file creation
* no file deletion
* no file move
* no file rename
* no staging
* no commit
* no push
* no merge
* no deploy
* no worker assignment
* no worker registration
* no worker claim
* no lock claim
* no lock release
* no campaign registry mutation
* no queue mutation
* no packet movement
* no approval mutation
* no approval consumption
* no runtime mutation
* no telemetry mutation
* no Reports mutation
* no scheduler mutation
* no dashboard mutation
* no app/runtime mutation
* no dependency install
* no package changes
* no APPLY scripts
* no credentials
* no secrets
* no broker/live behavior
* no real orders
* no real webhooks
* no UE5 implementation

PHASE 1 - REPRODUCE AIOS STATUS

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\aios.ps1 -Mode status
```

Capture:

* health
* branch
* packet_id
* packet_status
* approval_summary
* approval_matches
* worker inbox items
* overall_readiness
* next_safe_action
* recommended_worker
* recommended_lane
* recommended_validators
* collision_warning
* commit_package_preview

PHASE 2 - CREW RECOMMENDER READBACK

Inspect first, then run only if read-only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/crew/Get-AiOsCrewAssignmentRecommendation.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/crew/Get-AiOsCrewIntegrationRecommendation.DRY_RUN.ps1
```

Capture:

* command
* result
* recommended worker
* recommended lane
* campaign and packet reference
* approval requirements
* collision warnings
* lock warnings
* APPLY readiness
* mutation observed

If a recommender attempts mutation, stop that command, report `SKIPPED_WRITES_STATE`, confirm git status remains clean, and continue.

PHASE 3 - CAMPAIGN REGISTRY READBACK

Inspect:

* `automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json`
* `schemas/aios/orchestration/aios-strategic-campaign-registry.schema.json` if present

Determine:

* campaign count
* `CAMPAIGN-CREW-CORE` status
* `CAMPAIGN-CREW-CORE` priority
* campaign owner or lane if present
* required workers
* required validators
* required approvals
* blocked paths
* output expectations
* whether schema validates or has gaps
* whether campaign registry is authority, planning evidence, or runtime state
* whether campaign bridge work can remain DRY_RUN only
* whether APPLY would need exact mutation paths later

Do not edit registry files.

PHASE 4 - WORKER REGISTRY AND IDENTITY READBACK

Inspect:

* `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` if present
* `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` if present
* `automation/window_identity/AIOS_WORKER_REGISTRY.json` if present
* `docs/governance/aios-identity-and-lane-governance.md` if present
* `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` if present

Determine:

* whether `EAST_OCC_01` exists in any registry
* whether `EAST_OCC_01` is allowed as a temporary identity
* whether `crew-core-campaign-bridge` exists as a lane
* whether temporary workers require registration before APPLY
* whether dual worker registries conflict
* whether window identity registry is presentation-only or active
* whether missing `EAST_OCC_01` is a blocker for DRY_RUN or only APPLY
* what exact file would need future APPLY if registration is required

Do not edit registries.

PHASE 5 - COLLISION AND LOCK READBACK

Run only safe DRY_RUN/read-only validators:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1 -OutputJson
```

Do not run:

* `automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1`
* `automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1`
* any script that writes lock state, worker state, telemetry, Reports, runtime, packets, or queue state

Capture:

* identity result
* orchestration chain result
* worker claim collision result
* placeholder claim warning details
* lock registry result
* lock_count
* active_lock_count
* collision_risk_count
* whether APPLY is blocked by placeholder only
* exact file/path that owns placeholder claim if reported
* safe future action

PHASE 6 - PACKET STATE READBACK

Inspect:

* `automation/orchestration/work_packets/active/**`
* `automation/orchestration/work_packets/approved/**`
* `automation/orchestration/work_packets/proposed/**`
* `automation/orchestration/work_packets/complete/**`
* `automation/orchestration/work_packets/rejected/**`
* `automation/orchestration/work_packets/deferred/**`

Run if read-only:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1
```

Determine:

* active queue count
* approved queue count
* proposed remaining live/future packets
* whether crew campaign packet exists
* whether `PKT-CREW-CAMPAIGN-BRIDGE-DRYRUN` exists as a packet file
* whether a packet should be created in future APPLY
* whether work packet state helper has stale folder/status mismatch
* whether current `rulebook-foundation` complete packet is harmless or confusing

Do not move or create packets.

PHASE 7 - SAFE NEXT PACKET DECISION

Recommend exactly one next packet:

Option A:
`AIOS-WORKER-CLAIM-PLACEHOLDER-CLEANUP-APPLY-V1`

Use if the placeholder claim registry blocks meaningful crew APPLY readiness.

Option B:
`AIOS-WORKER-REGISTRY-EAST-OCC-DRY-RUN-V1`

Use if `EAST_OCC_01` identity/registry mismatch needs inspection before any crew APPLY packet.

Option C:
`AIOS-CREW-CAMPAIGN-BRIDGE-APPLY-PLAN-DRY-RUN-V1`

Use if packet state, worker identity, and lock collision evidence are clear enough to design a future APPLY lane without changing state.

Option D:
`AIOS-CREW-CAMPAIGN-BRIDGE-INSPECTION-COMPLETE-NOOP`

Use if inspection proves no immediate repo mutation should happen and Cloudflare/privacy or Dependabot should be next.

For the recommended packet, provide:

* packet ID
* mode
* allowed mutation paths if APPLY
* forbidden paths
* validator chain
* stop point
* why it is next

PHASE 8 - FINAL NO-MUTATION CHECK

Run:

```powershell
git status --short --branch
```

Confirm:

* files changed: NONE
* commit performed: NO
* push performed: NO
* merge performed: NO

FINAL REPORT FORMAT:

1. CURRENT STATE

* repo path:
* branch:
* HEAD:
* git status:
* mutation performed: NO

2. AIOS STATUS

* health:
* packet_id:
* packet_status:
* approval_summary:
* approval_matches:
* worker inbox items:
* overall_readiness:
* recommended worker:
* recommended lane:
* collision warning:
* commit package preview:

3. CREW RECOMMENDER RESULTS

For each recommender:

* command:
* result:
* worker:
* lane:
* campaign:
* blockers:
* APPLY readiness:
* mutation observed:

4. CAMPAIGN REGISTRY

* registry path:
* valid JSON:
* campaign count:
* `CAMPAIGN-CREW-CORE` status:
* priority:
* required workers:
* required validators:
* approval requirements:
* schema status:
* risk:

5. WORKER / IDENTITY REGISTRY

* orchestration worker registry:
* worker profiles:
* window identity registry:
* `EAST_OCC_01` present:
* `EAST_OCC_01` allowed:
* dual registry risk:
* APPLY blocker:

6. COLLISION / LOCK VALIDATION

* identity spine:
* orchestration validator chain:
* worker claim collision:
* placeholder claim details:
* lock registry:
* worker lock status:
* active locks:
* collision risks:
* APPLY blocker:

7. PACKET STATE

* active:
* approved:
* proposed:
* complete:
* rejected:
* deferred:
* crew packet exists:
* packet creation needed:

8. SAFE NEXT PACKET

* recommended option:
* packet ID:
* mode:
* why:
* allowed future mutation paths:
* forbidden paths:
* validator chain:
* stop point:

9. RISKS

* worker collision risk:
* lock registry risk:
* dual registry risk:
* campaign registry risk:
* packet state risk:
* operator confusion risk:

10. FINAL STATE

* git status:
* files changed: NONE
* commit performed: NO
* push performed: NO
* final status: PASS / REVIEW / WARNING / BLOCKED
