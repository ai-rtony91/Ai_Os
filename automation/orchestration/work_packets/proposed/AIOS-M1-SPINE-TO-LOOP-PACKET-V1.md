CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_APPROVES_M1_PACKET_PROPOSAL_ONLY

AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

IDENTITY MARKER: AIOS-M1-SPINE-TO-LOOP-PACKET-V1

SUPERVISOR IDENTITY: ChatGPT supervisor/planner

WORKER IDENTITY: Codex East

PACKET ID: AIOS-M1-SPINE-TO-LOOP-PACKET-V1

MODE: PACKET_LAYER_ONLY

ZONE: coordination_spine_proof_readiness

LANE: AIOS_M1_SPINE_TO_LOOP

WORKTREE: C:\Dev\Ai.Os

BRANCH: resolve after preflight

ALLOWED PATHS:
- automation/orchestration/work_packets/proposed/

FORBIDDEN PATHS to edit:
- AGENTS.md
- README.md
- WHITEPAPER.md
- automation/orchestration/coordination_spine/
- automation/orchestration/night_supervisor/
- telemetry/
- tests/
- services/
- secrets/
- credentials/
- live_trading/
- broker/

APPROVAL AUTHORITY:
Anthony is approval authority.
Codex is authorized to draft and validate this packet only.
No runtime, telemetry, tests, or infrastructure changes are authorized in this packet.

PREFLIGHT:
1. pwd
2. git status --short --branch
3. git branch --show-current
4. git remote -v

MISSION:
Create a single proposed work packet for M1 spine→loop wiring so execution is staged and controlled.

INTENT:
- Keep scope strictly proposal-only.
- Add one proposed packet file under `automation/orchestration/work_packets/proposed/`.
- Explicitly gate all future implementation under a separate APPLY approval.
- Do not add, modify, or remove code, telemetry, tests, or runtime behavior.

BACKGROUND:
The M1 packet should define the additive, DRY_RUN-first coordination seam needed to connect spine output into loop intake intent.

SCOPED PROPOSAL:
1. Create exactly one DRY_RUN-first packet:
   - `AIOS-M1-SPINE-TO-LOOP-PACKET-V1`
2. Packet defines:
   - M1 objective and non-goals
   - expected input/output evidence files
   - explicit design dependencies (upstream/downstream)
   - gating checkpoints before any APPLY work
3. Keep future code/apply scope as explicit text in this packet, and forbid execution-path changes until separately approved.

FUTURE CODE PHASE (GATED):
- No APPLY actions in this lane.
- Any future implementation must have a separate explicit Human Owner approval packet with:
  - exact file list
  - validator chain
  - stop point
  - proof-readiness checks
- This packet is DRY_RUN and proposal-only.

OUT OF SCOPE:
- Runtime path edits
- Telemetry edits
- Test suite edits
- Dispatcher/recovery/lock/queue behavior edits
- Any scheduler, webhook, broker, SOS/ADB, dashboard, or secret path edits
- commit, push, merge, or branch operations

VALIDATOR CHAIN:
- git diff --check
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-M1-SPINE-TO-LOOP-PACKET-V1.md

STOP POINT:
Stop after packet creation and validator execution.
No runtime APPLY, commit, push, merge, or branch operations in this packet.

FINAL REPORT FORMAT:
SUMMARY:
FILE CREATED:
VALIDATION:
NEXT SAFE COMMAND:
STATUS:

SAFE NEXT ACTION:
git status --short --branch