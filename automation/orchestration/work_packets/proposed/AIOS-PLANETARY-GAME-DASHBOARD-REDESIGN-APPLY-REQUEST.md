CODEX-ONLY PROMPT

PROPOSED REVIEW-ONLY APPLY REQUEST

The execution token is intentionally omitted. This draft is not executable until Anthony approves a future APPLY packet and supplies or approves the token.

identity marker: Codex East local executor
supervisor identity: ChatGPT Personal
packet ID: AIOS-PLANETARY-GAME-DASHBOARD-REDESIGN-APPLY-REQUEST-V1
mode: APPLY REQUEST - REVIEW ONLY
zone: dashboard UX redesign / planetary command map / browser-first prototype
worker identity: Codex East
lane: planetary-game-dashboard-redesign-apply
worktree: C:\Dev\Ai.Os
branch: create only after clean synced preflight and Anthony approval

approval authority:
Anthony must separately approve this APPLY packet before any dashboard overwrite, dashboard source edit, package change, dependency install, local preview server, commit, push, PR creation, or merge.

review status:
This file is a request for review only. It does not authorize execution.

mission:
Implement Phase 1 of the AI_OS planetary game dashboard as a browser-first, safe, readable, realistic command-map prototype while preserving the current Vite/React dashboard bridge and all AI_OS safety boundaries.

visual identity anchor:
The uploaded AI_OS visual identity image is a brand/theme reference only. It must guide written art direction and future visual review, but it must not be copied, committed, or added as an asset unless Anthony separately approves that exact asset action.

The goal is not to change the AI_OS visual identity; the goal is to enhance it into a realistic, cinematic, game-navigable command system.

Future implementation must preserve:
- Dark cinematic space background.
- Blue/purple energy language.
- Lightning/energy symbol.
- Signal tower / communications tower.
- Earth / global intelligence theme.
- Currency / trading / finance symbol.
- AIOS lettering.
- Tagline direction: intelligent, adaptive, yours.
- Reflective premium command-center mood.
- High-contrast futuristic fintech plus aerospace identity.

Future implementation must enhance, not replace:
- Realism, physical lighting, material detail, planetary realism, reflections, depth, and readability.
- Premium fintech polish.
- Consistency with Mars, Moon, Earth, Galaxy, and Black Hole dashboard zones.
- NASA-grade, cinematic, serious, realistic, operational command-center mood.

candidate files to change only after approval:
- apps/dashboard/src/App.jsx
- apps/dashboard/src/App.css
- apps/dashboard/src/runtimeVisibilityAdapter.js
- apps/dashboard/mock-data/aios-planetary-dashboard-state-v1.example.json
- apps/dashboard/skeleton/dashboard-structure.md
- apps/dashboard/skeleton/safety-rules.md

candidate files not to change:
- apps/dashboard/package.json
- apps/dashboard/package-lock.json
- apps/dashboard/vite.config.js
- apps/dashboard/server.js
- apps/dashboard/service-worker.js
- apps/dashboard/manifest.webmanifest
- apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json
- apps/dashboard/mock-data/aios-operator-status-v1.example.json
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
- Replace the first-screen information architecture with a planetary command map.
- Show only global status, AIOS EdgeMark, mode, safety state, current objective, next allowed action, critical alerts, and zone entries.
- Provide Mars Lab, Moon Control, Earth Hub, Galaxy Intelligence, and Black Hole Vault entry points.
- Move raw telemetry, queues, scheduler, runtime, GitHub checks, workers, debug JSON, logs, security details, freshness, and source trace to an Advanced drawer.
- Preserve `UNKNOWN`, `STALE`, `BLOCKED`, `NEEDS_APPROVAL`, `PASS`, and `FAIL` text labels.
- Preserve read-only runtime visibility behavior and fixture fallback behavior.
- Add a unified navigation model for mouse and keyboard in Phase 1.
- Design gamepad hooks but do not require Gamepad API implementation unless separately approved.
- Preserve reduced-motion and non-3D fallback.
- Use realistic cinematic aerospace visual direction, not cartoon, toy-like, low-poly, or arcade-only styling.
- Preserve the current AI_OS identity and enhance it into a realistic cinematic command system.
- Keep UI overlays readable, accessible, safe-state explicit, and governance-bound.
- Treat realism-first visual review as a required implementation gate before any dashboard overwrite.
- Do not mutate dashboard implementation in the visual-anchor documentation packet; implementation requires this future APPLY packet or another separately approved packet.

explicitly blocked in this APPLY request:
- No Cloudflare, Azure, DNS, tunnel, OAuth, Turnstile, or provider configuration.
- No secrets.
- No runtime mutation.
- No scheduler mutation.
- No queue mutation.
- No approval inbox mutation.
- No worker inbox mutation.
- No command queue mutation.
- No broker or live-trading mutation.
- No live trading.
- No UE5 project creation.
- No UE5 assets.
- No uploaded visual identity asset commit unless separately approved.
- No game engine dependencies.
- No multiplayer/live leaderboard implementation.
- No public/remote exposure.
- No commit, push, PR creation, merge, or PR closure unless separately approved after diff and validation review.

realism-first visual requirements:
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

prohibited visual directions:
- Do not remove the core AI_OS symbols.
- Do not make it childish, cartoon, toy-like, flat, low-poly, arcade-only, mobile-game style, or unrelated sci-fi.
- Do not overuse neon until it hurts readability.
- Do not turn the dashboard into a decorative poster instead of a usable command system.
- Do not expose secrets, broker data, live trading state, private paths, or unsafe controls.

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

required manual review:
- Desktop screenshot review.
- Mobile screenshot review.
- Keyboard-only navigation review.
- Reduced-motion review.
- Realism-first visual review against the AI_OS visual identity anchor.
- Screenshot/manual review before any dashboard overwrite.
- Confirm no dashboard source hides critical safety labels.
- Confirm no secrets, broker controls, runtime mutation, scheduler mutation, queue mutation, approval mutation, or live-trading controls appear.
- Confirm no uploaded visual asset was committed unless separately approved.
- Confirm no UE5 project was created unless separately approved.
- Confirm local preview before merge.

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
Stop after local implementation, validation, and manual preview evidence. Do not stage, commit, push, create a PR, merge, expose remotely, or start provider configuration without separate Anthony approval.
