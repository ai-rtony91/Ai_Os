CODEX-ONLY PROMPT

PROPOSED REVIEW-ONLY APPLY REQUEST

The execution token is intentionally omitted. This draft is not executable until Anthony approves a future APPLY packet and supplies or approves the token.

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-PLANETARY-GAME-DASHBOARD-IMPLEMENTATION-APPLY-REQUEST-V1
mode: APPLY REQUEST - REVIEW ONLY
zone: dashboard implementation / planetary game UI / browser-first React shell
worker identity: Codex East
lane: planetary-game-dashboard-implementation-apply
worktree: C:\Dev\Ai.Os
branch: create only after clean synced preflight and Anthony approval

approval authority:
Anthony must separately approve this APPLY packet before editing any file under `apps/dashboard/`, installing dependencies, starting a preview server, staging, committing, pushing, creating a PR, or merging.

review status:
This file is a request for review only. It does not authorize execution.

mission:
Implement Phase 1 of the AI_OS planetary game dashboard as a no-new-dependency, browser-first Vite/React planetary command shell while preserving the current read-only dashboard state boundaries, safety labels, AI_OS visual identity, and governance constraints.

required visual identity rule:
The goal is not to change the AI_OS visual identity; the goal is to enhance it into a realistic, cinematic, game-navigable command system.

candidate files to edit only after separate Anthony approval:
- apps/dashboard/src/App.jsx
- apps/dashboard/src/App.css
- apps/dashboard/mock-data/aios-planetary-dashboard-state-v1.example.json
- apps/dashboard/skeleton/dashboard-structure.md
- apps/dashboard/skeleton/safety-rules.md

candidate files not to edit in first APPLY unless separately approved:
- apps/dashboard/package.json
- apps/dashboard/package-lock.json
- apps/dashboard/vite.config.js
- apps/dashboard/server.js
- apps/dashboard/service-worker.js
- apps/dashboard/manifest.webmanifest
- apps/dashboard/index.html
- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/js/aios-static-preview.js
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/src/runtimeVisibilityClient.js
- apps/dashboard/src/runtimeVisibilityAdapter.js
- apps/dashboard/src/index.css
- apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json
- apps/dashboard/mock-data/aios-operator-status-v1.example.json
- apps/dashboard/mock-data/autonomy_bridge_state.sample.json
- telemetry/runtime/
- telemetry/night_supervisor/
- services/
- scripts/control/
- apps/trading_lab/
- aios/modules/trader/
- automation/orchestration/work_packets/active/
- automation/orchestration/work_packets/blocked/
- automation/orchestration/work_packets/complete/
- automation/orchestration/workers/inbox/
- automation/orchestration/command_queue/
- automation/orchestration/approval_inbox/
- .github/
- .git/
- .env
- secrets
- credentials

required implementation scope:
- Replace the React first-screen information architecture with a planetary command map.
- Preserve current Vite/React bridge.
- Preserve read-only runtime visibility behavior and fixture fallback behavior.
- Show Mars Lab, Moon Control, Earth Hub, Galaxy Intelligence, and Black Hole Vault.
- Show global status, AIOS EdgeMark placeholder/model, mode, safety state, current objective, next safe action, critical alerts, and zone entries.
- Move raw telemetry, queues, scheduler, runtime, GitHub checks, workers, debug JSON, logs, security details, freshness, and source trace into a collapsed Advanced drawer.
- Preserve `UNKNOWN`, `STALE`, `BLOCKED`, `NEEDS_APPROVAL`, `PASS`, `FAIL`, and `REVIEW` text labels.
- Add lightweight keyboard and mouse navigation through a frontend command model.
- Plan Xbox controller / Browser Gamepad API mapping, but do not require Gamepad API implementation unless separately approved.
- Preserve reduced-motion and non-3D fallback.
- Keep Paper League simulated and paper-only.
- Keep AIOS EdgeMark as readiness/discipline display, not live trading edge.

realism-first implementation requirements:
- Realistic cinematic space art is the top visual requirement.
- Use NASA / aerospace / mission-control inspiration.
- Use realistic sci-fi, not fantasy sci-fi.
- Merge a premium fintech/trading terminal with space exploration.
- Mars should feel geologic, dusty, harsh, and physical.
- Earth should look atmospheric, alive, and recognizable, not icon-like.
- Moon should feel cold, cratered, reflective, and mission-control adjacent.
- Galaxy/deep space should use believable star fields, nebula depth, red dwarf inspiration, black-hole lensing inspiration, and orbital distance cues.
- Black Hole/Vault should feel dangerous, gravitational, distorted, restricted, and visually serious.
- Lighting should feel physically motivated: sun direction, rim light, shadow, glow, atmospheric scattering, and carefully controlled bloom.
- Materials should feel real: dust, rock, metal, glass, worn panels, astronaut suit fabric, visor reflections, cockpit surfaces.
- UI overlays should feel like a serious command system layered over a realistic world.
- Realism must not hurt readability, accessibility, safety states, or operator clarity.

explicitly blocked:
- No dependency install unless explicitly approved.
- No `npm install`.
- No package/package-lock mutation unless explicitly approved.
- No Three.js, React Three Fiber, Drei, Tailwind, shadcn/ui, GSAP, or Framer Motion unless explicitly approved.
- No UE5 project creation.
- No UE5 assets.
- No uploaded image asset commit.
- No new assets unless separately approved.
- No Cloudflare, Azure, DNS, tunnel, OAuth, Turnstile, provider, or public exposure configuration.
- No secrets.
- No runtime mutation.
- No scheduler mutation.
- No queue mutation.
- No approval inbox mutation.
- No worker inbox mutation.
- No command queue mutation.
- No broker/live-trading mutation.
- No live trading.
- No real-money leaderboard.
- No multiplayer/live leaderboard backend.
- No commit, push, PR creation, merge, or PR closure unless separately approved after diff and validation review.

required preflight after Anthony approval:
```powershell
cd C:\Dev\Ai.Os
git status --short --branch
git diff --check
git branch --show-current
git remote -v
```

required validators after implementation:
```powershell
git diff --check
cd apps/dashboard
npm run build
npm run lint
git status --short --branch
```

required preview/manual review before merge:
- Start local preview only after Anthony approves the implementation APPLY.
- Desktop screenshot review.
- Mobile screenshot review.
- Keyboard-only navigation review.
- Reduced-motion review.
- Advanced drawer review.
- Realism-first visual review against the AI_OS visual identity anchor.
- Confirm no dashboard source hides critical safety labels.
- Confirm no secrets, broker controls, runtime mutation, scheduler mutation, queue mutation, approval mutation, or live-trading controls appear.
- Confirm no uploaded visual asset was committed.
- Confirm no UE5 project was created.
- Confirm no dependency install occurred unless separately approved.
- Confirm local preview before merge.

rollback plan:
- Keep implementation on an isolated feature branch.
- Change only exact approved files.
- Do not delete existing dashboard files during Phase 1.
- Preserve current fixtures, Vite virtual module, static preview, server, service worker, manifest, and read-only runtime visibility API contract.
- If validation or manual review fails, restore only the exact changed files from the prior commit.

required final report:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
FILES NOT CHANGED:
VALIDATION:
SCREENSHOT/MANUAL REVIEW:
SAFETY BOUNDARIES VERIFIED:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS: COMPLETE, NO COMMIT, NO PUSH

stop point:
Stop after local implementation, validation, and manual preview evidence. Do not stage, commit, push, create a PR, merge, expose remotely, create UE5 files, install dependencies, or start provider configuration without separate Anthony approval.

