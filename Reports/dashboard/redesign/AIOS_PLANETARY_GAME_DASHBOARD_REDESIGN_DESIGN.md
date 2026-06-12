# AI_OS Planetary Game Dashboard Redesign Design

Status: DRY_RUN design report  
Packet: AIOS-PLANETARY-GAME-DASHBOARD-REDESIGN-DESIGN-DRY-RUN-V1  
Worker: Codex East  
Generated: 2026-06-12  
Branch: feature/planetary-game-dashboard-redesign-design-v1  

## Executive Summary

AI_OS should move from a dense operations dashboard toward a browser-first planetary command map. The first screen should feel like a serious space-command interface, not a spreadsheet of cards. It should show only global readiness, AIOS EdgeMark, safety state, current objective, next allowed action, critical alerts, and five zone entry points: Mars Lab, Moon Control, Earth Hub, Galaxy Intelligence, and Black Hole Vault.

The goal is not to change the AI_OS visual identity; the goal is to enhance it into a realistic, cinematic, game-navigable command system.

The visual target is realistic and cinematic: NASA and aerospace inspired, physically grounded, readable, and serious. The dashboard should avoid cartoon planets, low-poly game art, fake neon overload, and mobile-game aesthetics. UI overlays should feel like a high-end trading terminal and command system layered over believable space environments.

No dashboard source changes are approved by this design packet. The current Vite/React dashboard remains the active bridge. Future implementation should be phased: first a lightweight web planetary shell, then richer browser 3D, then a separate Unreal Engine 5 evaluation for premium immersive mode.

## Current Dashboard Noise Assessment

Inspected surfaces:

- `apps/dashboard/src/App.jsx`
- `apps/dashboard/src/App.css`
- `apps/dashboard/src/runtimeVisibilityAdapter.js`
- `apps/dashboard/src/runtimeVisibilityClient.js`
- `apps/dashboard/vite.config.js`
- `apps/dashboard/server.js`
- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`
- `automation/orchestration/dashboard/Update-AiOsDashboardState.ps1`
- `docs/concepts/aios-dashboard-and-interface-concepts.md`
- `docs/specs/aios-dashboard-data-contracts.md`

Current first-screen elements include:

- React operations header with runtime status, source label, freshness, and backpressure.
- 24-hour mission summary with worker activity, passed, blocked, approvals waiting, Night Supervisor, T9 savepoint, and next safe action.
- Worker rooms for Codex, Claude, Relay, and Night Supervisor.
- Operator Status fixture panels.
- Autonomy Bridge state.
- Playlist Dock.
- Advanced telemetry drill-down.
- Static preview start screen, side rails, Work Table, Apps Hub, music dock, status strips, status cards, registry fixtures, assistant details, and many hidden legacy sections.

Noise and duplication:

- Multiple panels repeat worker, approval, safety, and runtime concepts.
- The current first screen mixes end-user status, operator-only telemetry, side-rail app navigation, fixture status, media controls, and work-table details.
- Labels such as worker leases, execution ledger, poison packets, backpressure, and raw source traces are useful for operators but too dense for an end-user first screen.
- The static preview and React app both preserve safety boundaries, but their UI hierarchy competes with itself.

End-user-safe elements:

- Global status with explicit `READY`, `BLOCKED`, `NEEDS_APPROVAL`, `UNKNOWN`, `STALE`, `PASS`, and `FAIL`.
- Paper-only Trading Lab state.
- AIOS EdgeMark explanation.
- Next safe action.
- Zone entry points.
- Learning missions, paper league progress, and safe achievements.

Operator-only elements:

- Raw telemetry.
- Queue tables.
- Worker leases.
- Scheduler state.
- Runtime process details.
- GitHub PR/check details.
- Debug JSON.
- Source trace and stale-source diagnostics.
- Approval inbox internals.

Dangerous elements that must never appear on public or remote surfaces:

- Secrets, tokens, API keys, broker keys, private keys, recovery keys, repo credentials, Git credentials, Azure tokens, Cloudflare tokens, and account credentials.
- Live broker controls, order placement controls, real webhook firing, or live order paths.
- Local file paths that expose private machine structure unless intentionally redacted.
- Active approval inbox mutation controls.
- Worker launch, stop, or mutation controls that bypass AI_OS approval gates.
- Scheduler or runtime mutation controls.

State dependencies that must not be broken:

- React app imports `apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json`.
- React app imports `apps/dashboard/mock-data/aios-operator-status-v1.example.json`.
- Vite virtual module reads `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` or falls back to `apps/dashboard/mock-data/autonomy_bridge_state.sample.json`.
- Optional read-only runtime visibility API is `/api/runtime/visibility` and must return `schema: aios.runtime_visibility_api.v1` and `mode: READ_ONLY`.
- Vite dev server proxies `/api` to `http://localhost:5050`.
- Static server exposes local files and a read-only live autonomy bridge JSON route.
- `Update-AiOsDashboardState.ps1` writes `apps/dashboard/data/aios_live_state.json` when invoked, but dashboard writer activation is not approved by this design.

Current input assumptions:

- Mouse and touch are primary in the static preview.
- Keyboard support exists for Enter and Space activation on some controls, Escape for mobile rail close, and media shortcuts.
- Arrow keys currently control the music dock, not dashboard navigation.
- No browser Gamepad API support is present.
- No unified command/focus abstraction exists across mouse, keyboard, touch, and controller.

## Existing Concept/Spec Alignment

This design aligns with the current concept and data-contract docs:

- Web dashboard remains first.
- UE5 remains a future premium client evaluation, not an immediate replacement.
- Keyboard, mouse, and Xbox controller are first-class input targets.
- Future clients read state through approved backend APIs only.
- Secrets, broker keys, repo file reads, telemetry ledger reads, approval inbox reads, worker queue reads, scheduler reads, and environment file reads are blocked for clients.
- Live trading and live broker execution remain blocked.
- Missing data is `UNKNOWN`, stale data is explicit, and validator output is evidence only.

## AI_OS Visual Identity Anchor

The uploaded AI_OS visual identity image is a brand/theme reference only. It must not be committed, copied, recreated as a repository asset, or treated as an implementation dependency by this documentation packet.

The goal is not to change the AI_OS visual identity; the goal is to enhance it into a realistic, cinematic, game-navigable command system.

Preserve:

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

Enhance only:

- Increase realism, physical lighting, material detail, planetary realism, reflections, depth, and readability.
- Improve premium fintech polish without turning the interface into a decorative poster.
- Keep the visual language aligned with Mars, Moon, Earth, Galaxy, and Black Hole dashboard zones.
- Make the system feel NASA-grade, cinematic, serious, realistic, and operational.
- Preserve readable AIOS lettering and tagline treatment.

Do not:

- Remove the core AI_OS symbols.
- Replace the AI_OS identity with unrelated sci-fi styling.
- Make it cartoon, toy-like, flat, low-poly, childish, arcade-only, or mobile-game style.
- Overuse neon until it hurts readability.
- Expose secrets, broker data, live trading state, private paths, unsafe controls, or privileged operator actions.

## Planetary Information Architecture

The home view should be a galaxy command map with five selectable bodies:

1. Mars Lab: development and build world.
2. Moon Control: mission control and operational health.
3. Earth Hub: personal apps, school, work, contacts, notes, and user workspace.
4. Galaxy Intelligence: agents, memory, research, roadmap, automation map, and strategy.
5. Black Hole Vault: restricted security boundary, blocked live trading, secrets boundary, and emergency references.

Each zone should share a unified structure:

- Zone identity and safety status.
- Current objective.
- Next allowed action.
- Critical alerts only.
- Compact score or readiness metric.
- Enter zone command.
- Advanced drawer for raw details.

The first screen should never require the user to parse raw telemetry to understand whether AI_OS is safe, blocked, or ready.

## Realistic Visual Direction

Realism is essential. Realistic cinematic space art is the top visual requirement, with NASA / aerospace / mission-control inspiration and realistic sci-fi rather than fantasy sci-fi. The design target is a premium fintech/trading terminal merged with space exploration: reflective, physical, serious, and operational.

Required visual cues:

- Planetary scale should feel real, even if artistically compressed for usability.
- Mars should feel dusty, geologic, harsh, and physical.
- Earth should look atmospheric, alive, and recognizable, not icon-like.
- Moon should feel cold, cratered, reflective, and mission-control adjacent.
- Galaxy space should use believable star fields, nebula depth, red dwarf inspiration, black-hole lensing inspiration, and orbital distance cues.
- Black Hole Vault should feel serious, dangerous, gravitational, distorted, and restricted.
- Lighting should have clear physical motivation: sun direction, rim light, shadow, controlled bloom, and atmospheric scattering.
- Materials should feel real: dust, rock, metal, glass, worn panels, astronaut suit fabric, visor reflections, and cockpit surfaces.
- UI overlays should feel like a serious command system layered over a realistic world, not decorative neon.
- Realism must not hurt readability, accessibility, safety states, or operator clarity.

Avoid:

- Cartoon planets.
- Flat emoji-style planets.
- Toy-like low-poly assets.
- Arcade-only composition.
- Childish color palettes.
- Heavy fake neon that reduces readability.
- Decorative effects that hide state labels.

## First-Screen Design

First screen content:

- AI_OS global status: `READY`, `BLOCKED`, or `NEEDS_APPROVAL`.
- AIOS EdgeMark score.
- Mode: `observe-only`, `paper-safe`, or `blocked`.
- Safety state: live trading blocked, broker blocked, secrets safe.
- Current objective.
- Next allowed action.
- Critical alerts only.
- Entry points for Mars, Moon, Earth, Galaxy, and Black Hole.

First screen layout:

- Full-screen realistic space field.
- Mars is the large foreground/lower-screen world and primary development entry.
- Moon sits near mission-control overlays.
- Earth is recognizable and alive, used for personal/work apps.
- Deep space and red-dwarf inspired background represent intelligence and research.
- Black Hole Vault is visually separated with gravitational distortion and a restricted badge.
- Status overlay is compact and stable, not a stack of cards.

What to remove from the first screen:

- Worker lease tables.
- Queue counters.
- Poison packet tables.
- Raw telemetry event log.
- Full approval inbox.
- GitHub check details.
- Debug JSON.
- Fixture source traces.
- Music/player dock.
- App registry details.
- Multiple repeated status panels.
- Long assistant explanations.

What to move to Advanced:

- Runtime status details.
- Scheduler actions.
- Worker leases.
- Active packets.
- Failed packet grouping.
- Backpressure inputs.
- Raw telemetry log.
- Execution ledger.
- Source paths and schema details.
- Cloudflare/login state.
- Security state details.
- Debug JSON.

## Mars Lab Design

Purpose: developer/build world.

Mars Lab should show:

- Codex lanes.
- GitHub PRs and checks.
- Workers.
- Test status.
- Work packets.
- Build status.
- Local dev tools.
- Dashboard redesign/dev tools.

Visual direction:

- Mars terrain with dust, rock, rim-lit ridges, and rover-like surface markers.
- Build lanes appear as grounded habitat modules or route markers.
- PR/check state appears as mission beacons, not spreadsheet rows.
- Status labels remain text-readable over the 3D scene.

Safety:

- No commit, push, merge, branch deletion, cleanup, or PR closure from one click.
- Protected actions show preview cards and require AI_OS approval gates.
- Failed validators block promotion.

## Moon Control Design

Purpose: mission control and operational health.

Moon Control should show:

- AI_OS health.
- AIOS EdgeMark.
- Scheduler state.
- Approvals.
- Current objective.
- Safety gates.
- Critical alerts.

Visual direction:

- Cold cratered moon surface with mission-control instrumentation.
- Reflective panels, radar-like orbital arcs, and restrained command-room overlays.
- Status hierarchy: `BLOCKED` and `NEEDS_APPROVAL` dominate.

Safety:

- Scheduler and runtime controls remain display-only or approval-request previews.
- Approval state is evidence, not permission.

## Earth Hub Design

Purpose: personal and user workspace.

Earth Hub should show:

- Personal apps.
- Created apps.
- Contacts.
- Notes.
- School/work/Microsoft entry.
- User profile.
- Future end-user workspace.

Visual direction:

- Atmospheric Earth with cloud layers, city-light hints where appropriate, and recognizable continents.
- Personal app surfaces should feel calm and useful, not consumer-game clutter.

Safety:

- No OAuth, provider configuration, Cloudflare, Azure, DNS, tunnel, Turnstile, or account connection setup in this design.
- No credentials, private links, or private profile data stored in frontend.

## Galaxy Intelligence Design

Purpose: intelligence, memory, and strategy.

Galaxy Intelligence should show:

- AI agents.
- Memory.
- Research.
- Automation map.
- Strategy.
- Roadmap.
- Long-term intelligence layer.

Visual direction:

- Deep field with believable stars, dust lanes, orbital depth, red dwarf inspiration, and subtle nebula structure.
- Agent and memory nodes appear as mapped constellations with source confidence labels.

Safety:

- AI assistant surfaces remain display-only until separately approved.
- No live AI API calls or private prompt storage are implied by this design.

## Black Hole Vault Design

Purpose: restricted/security zone.

Black Hole Vault should show:

- Secrets boundary.
- Broker/live-trading block.
- Emergency stop and break-glass references.
- Access warnings.
- Restricted state.

Visual direction:

- Black hole lensing inspiration, distorted rings, gravity-warning motion, and serious restricted-zone UI.
- This should feel dangerous and controlled, not decorative.

Safety:

- Never show secrets.
- Never expose broker/account credentials.
- Never provide live broker or live-trading controls.
- Protected action authority stays in AI_OS approval gates, not UI identity alone.

## First-Person Astronaut Mode Design

First-person astronaut mode is future/immersive. It is not a Phase 1 dependency.

Experience:

- User can move as an astronaut or cockpit-like explorer in AI_OS space.
- User can move, orbit, inspect, and enter zones.
- Keyboard, mouse, and Xbox controller are supported.
- Movement does not trigger destructive actions.
- Entering a zone is a safe navigation action.
- Protected actions require confirmation and AI_OS approval gates.
- Non-3D dashboard remains usable.

Phase 1:

- Browser-first 2D/2.5D planetary command map.
- Unified focus and command model.
- Reduced-motion and non-3D fallback.
- No first-person movement.

Phase 2:

- Web 3D prototype with React Three Fiber, Three.js, and Drei.
- Orbit camera, selectable planets, controller navigation, command palette, and fallback.
- Lightweight physically based materials and compressed textures.

Phase 3:

- UE5 premium client evaluation.
- Full first-person astronaut or cockpit mode.
- Highest realism tier with Lumen/Nanite-style direction, realistic planet materials, atmosphere, visor/cockpit reflections, and controller-native movement.

## Gamified Paper League Design

Paper League is simulated only. It must not use real money, gambling framing, live broker execution, or one-click live trading.

Core loop:

- Season mode.
- Leagues and divisions.
- Learning missions.
- Paper trading performance.
- AIOS EdgeMark progression.
- Badges and streaks.
- Safe onboarding.
- Evidence-backed improvement.

Allowed user actions:

- Join simulated season.
- Review paper strategy.
- Submit paper-only results.
- Complete learning mission.
- Review score explanation.
- Compare standings.

Blocked:

- Real-money competition.
- Gambling framing.
- Live broker action.
- Broker credentials.
- Live order execution.
- External leaderboard writes until a later backend/API packet approves them.

## Leaderboard Safety Model

Leaderboard categories:

- Biggest paper P&L.
- Best risk-adjusted return.
- Lowest drawdown.
- Best consistency streak.
- Best execution quality.
- Best AIOS EdgeMark.
- Best learning progression.
- Best latency readiness later.
- Best rule discipline.

Primary ranking should reward discipline, consistency, risk control, evidence quality, and clean validation. Biggest paper P&L can exist, but it must not dominate the primary score. A user who takes reckless max-risk paper trades should score poorly on drawdown, discipline, and risk-adjusted categories.

## AIOS EdgeMark Model

AIOS EdgeMark is a benchmark-style readiness and discipline score inspired by trading edge and system readiness.

Inputs:

- Validation cleanliness.
- Safety gate status.
- Paper/live boundary.
- Signal quality later.
- Latency readiness later.
- Execution quality later.
- Scheduler/automation health.
- Repo clean-state reliability.
- Stale/unknown evidence penalty.
- Rule discipline.

Score bands:

- 90-100: READY, evidence-backed, clean validation, paper/live boundary clear.
- 70-89: REVIEW, generally healthy with warnings or stale details.
- 40-69: NEEDS_APPROVAL or NEEDS_WORK, important gaps remain.
- 0-39: BLOCKED, failed validation, unsafe state, or unknown critical evidence.

Rules:

- Missing data lowers confidence.
- Stale data lowers confidence.
- `UNKNOWN` is not treated as success.
- Live trading shows `BLOCKED` until separately approved.
- Score explanation must be visible.
- No fake confidence.

## Mouse Input Model

Commands:

- Click planet/body: focus or enter zone, depending on context.
- Hover: highlight zone and show concise status.
- Drag/pan/rotate: allowed for camera control only where appropriate.
- Wheel zoom: optional and constrained to avoid disorientation.
- Right-click/context action: safe menus only.

Safety:

- No destructive action on accidental click.
- Protected actions require confirmation and approval gates.
- Hover text must not hide critical safety labels.

## Keyboard Input Model

Commands:

- Tab and Shift+Tab move between planet zones and UI controls.
- Enter or Space activates focused zone.
- Escape returns to galaxy/home view.
- Arrow keys or WASD move focus/selection.
- `/` or Ctrl+K opens command palette.

Requirements:

- Visible focus rings.
- No keyboard trap.
- Keyboard-only users can operate all important features.
- Focus order matches visual order and role importance.
- Critical status is reachable before decorative controls.

## Xbox Controller / Gamepad Input Model

Commands:

- Left stick or D-pad moves focus between zones.
- Right stick controls camera/orbit where appropriate.
- A selects or enters a zone.
- B backs out or returns to galaxy view.
- X opens Advanced or actions.
- Y opens search/command palette.
- LB/RB switches major zones.
- LT/RT controls zoom or speed where appropriate.
- Start/Menu opens system menu.
- Back/View opens help/controls overlay.

Safety:

- Controller disconnect falls back to keyboard/mouse.
- No critical destructive action from one accidental button press.
- Protected actions require explicit review and approval gates.

## Unified Input Abstraction

Design a command layer that maps mouse, keyboard, touch, and gamepad to the same commands:

- `focusZone(zoneId)`
- `selectZone(zoneId)`
- `enterZone(zoneId)`
- `back()`
- `openCommandPalette()`
- `openAdvancedDrawer()`
- `moveFocus(direction)`
- `setCameraIntent(intent)`

State model:

- `focusedZone`
- `selectedZone`
- `activeView`
- `activeInput`
- `reducedMotion`
- `advancedOpen`
- `commandPaletteOpen`
- `safetyState`

This abstraction allows the existing Vite/React bridge to evolve without mixing interaction logic into raw visual components.

## Accessibility / Reduced-Motion Model

Required:

- Non-3D fallback view.
- Reduced-motion mode.
- High-contrast mode.
- Visible focus rings.
- Screen-reader labels for zones and status.
- Stable status text outside the 3D canvas.
- No critical status conveyed by color alone.
- `UNKNOWN`, `STALE`, `BLOCKED`, `NEEDS_APPROVAL`, `PASS`, and `FAIL` have text labels.
- No keyboard trap.
- Motion never blocks reading.

Reduced-motion fallback:

- Static realistic planet stills or CSS background layers.
- Same zone cards and status text.
- No orbit animation.
- No camera drift.
- No bloom-heavy transitions.

## Web-First Technology Stack Recommendation

Current bridge:

- Keep current Vite/React dashboard active until a separate APPLY packet approves source changes.
- Do not break current mock-data import, Vite virtual module, or read-only runtime visibility API contract.

Future web target:

- Next.js + React + TypeScript can be evaluated later for production app structure.
- React Three Fiber / Three.js / Drei for browser-native planetary 3D.
- Tailwind + shadcn/ui for readable command panels if the design system migrates.
- Zustand or equivalent lightweight store for navigation, focus, and view state.
- TanStack Query or equivalent for read-only backend state queries.
- Browser Gamepad API for Xbox controller support.
- Framer Motion or GSAP only where transitions improve orientation.
- Reduced-motion and non-3D fallback modes.
- No secrets in frontend.

Realism implementation:

- Use optimized physically based materials.
- Use compressed textures.
- Use HDRI-style lighting direction where practical.
- Use controlled bloom, atmosphere, and star-field depth.
- Keep critical status labels outside shader-heavy layers.

## UE5 Premium Client Evaluation

UE5 is a future evaluation lane only.

Good UE5 fit:

- Premium command-center client.
- Immersive desktop app.
- Kiosk operator mode.
- Possible launcher.
- First-person astronaut/cockpit mode if the web prototype is too heavy.
- Highest realism tier with Lumen/Nanite-style direction, planet materials, atmosphere, cockpit surfaces, astronaut presence, and controller-native exploration.

Boundaries:

- UE5 must read AI_OS state through approved backend APIs only.
- UE5 must not read repo files, telemetry ledgers, approval inboxes, worker queues, scheduler state, local environment files, or generated runtime files directly.
- UE5 must not store secrets, broker keys, Azure tokens, Cloudflare tokens, repo credentials, Git credentials, API keys, private keys, recovery keys, or persistent privileged sessions.
- UE5 controls for runtime, scheduler, queues, broker, and live-trading surfaces remain display-only or approval-request previews unless a separate approved workflow authorizes a specific action.
- Live broker execution and live trading remain blocked.

## Backend API / State Boundary

The dashboard and any future UE5 client should consume approved backend APIs only.

Required response features:

- Schema.
- Mode.
- Source label.
- Timestamp.
- Freshness.
- Stale/invalid markers.
- Approval requirement.
- Next safe action.
- Redacted source trace.
- No credentials.
- No broker/account identifiers.

Current compatible direction:

- Preserve `/api/runtime/visibility` as read-only.
- Preserve `mode: READ_ONLY`.
- Preserve fixture fallback behavior.
- Do not wire direct frontend reads to repo files, telemetry ledgers, approval inboxes, worker queues, scheduler state, or environment files.

## End-User vs Operator Role Model

End user:

- Sees simplified planetary UI, paper league, safe progress, and approved actions only.

Trader/student:

- Sees Paper League, learning missions, score explanations, paper performance, and rule-discipline feedback.

Operator:

- Sees Advanced drawer, state freshness, worker/PR status, approval state, raw telemetry, and source trace.

Admin:

- Sees control review surfaces, access state, break-glass references, and security boundaries.

Protected action authority:

- Stays in AI_OS approval gates.
- UI identity alone never approves protected actions.

## What Must Never Appear On Frontend

- Secrets.
- Credentials.
- API keys.
- Broker keys.
- Account numbers.
- Private keys.
- Recovery keys.
- Cloud provider tokens.
- Git credentials.
- Raw approval inbox mutation controls.
- Direct queue mutation controls.
- Scheduler mutation controls.
- Runtime process mutation controls.
- Live broker controls.
- Real order buttons.
- Real webhook firing controls.
- Unredacted private file paths in public mode.

## Phased Apply Plan

Phase 1 - design system and 2D/2.5D shell:

- Create planetary IA in React without changing backend behavior.
- Add zone model, first-screen hierarchy, safety overlay model, and Advanced drawer.
- Keep existing runtime visibility contracts.
- Use static or optimized realistic assets.
- Add keyboard-first focus model.
- Add non-3D fallback.

Phase 2 - browser 3D prototype:

- Add React Three Fiber / Three.js / Drei after separate approval.
- Implement selectable planets and camera orbit.
- Add browser Gamepad API support.
- Add reduced-motion fallback.
- Keep all data read-only.

Phase 3 - UE5 evaluation:

- Create separate UE5 evaluation packet.
- Define approved API contract first.
- Prototype immersive astronaut/cockpit mode.
- Keep no-secrets and no-live-trading boundaries.

## Rollback Plan

For future APPLY work:

- Keep current dashboard branch isolated.
- Change only approved files.
- Preserve current fixtures and read-only API behavior.
- Capture before/after screenshots.
- Run local preview before merge.
- Revert by restoring the exact changed files from the prior commit if validation or manual review fails.
- Do not delete existing dashboard files during the first redesign implementation.

## Preview/Test Plan

Future implementation validation should include:

- `npm run build` in `apps/dashboard`.
- `npm run lint` in `apps/dashboard` if lint config supports the changed code.
- Local Vite preview.
- Desktop screenshot review.
- Mobile screenshot review.
- Keyboard-only walkthrough.
- Reduced-motion walkthrough.
- Non-3D fallback walkthrough.
- Gamepad test if Gamepad API is implemented.
- Verify no secrets, broker controls, queue mutation, scheduler mutation, or live trading controls appear.

## Exact Stop Point Before Overwrite

Stop before editing or overwriting any file under `apps/dashboard/`.

The next APPLY packet must be reviewed and separately approved by Anthony before dashboard source changes. It must name exact files to change, exact files not to change, validators, preview steps, screenshot/manual review requirements, rollback plan, and protected-action stop points.
