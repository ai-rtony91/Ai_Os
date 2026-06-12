# AI_OS Planetary Game Dashboard Implementation Prep

Status: DRY_RUN implementation prep  
Packet: AIOS-PLANETARY-GAME-DASHBOARD-IMPLEMENTATION-PREP-DRY-RUN-V1  
Worker: Codex East  
Generated: 2026-06-12  
Branch: feature/planetary-game-dashboard-implementation-prep-v1  

## Executive Summary

The current dashboard is ready for a scoped Phase 1 planetary shell pass, but not for a full 3D/game-engine rewrite. The safest first implementation is a no-new-dependency Vite/React redesign inside the existing active bridge: replace the React first-screen hierarchy with a realistic cinematic planetary command map, preserve the read-only runtime visibility adapter/client, and keep raw operational detail in an Advanced drawer.

The implementation should enhance the AI_OS visual identity, not replace it. The direction remains realistic cinematic space art, NASA-grade aerospace mood, premium fintech/trading-terminal polish, blue/purple energy language, AIOS lettering, signal/communications motifs, Earth/global intelligence, and paper-only Trading Lab framing. It must not become cartoon, toy-like, flat, low-poly, childish, arcade-only, or decorative at the expense of readability.

No dashboard source files were edited by this prep packet. This report creates a cut list and a review-only APPLY request for a later packet.

## Current Dashboard Implementation Map

Active app/runtime:

- `apps/dashboard/package.json` defines a Vite/React app with `dev`, `build`, `lint`, `preview`, and `start` scripts.
- `apps/dashboard/src/main.jsx` renders `App` into `#root` under React `StrictMode`.
- `apps/dashboard/src/App.jsx` owns most visible React dashboard composition, including operations header, mission summary, worker rooms, operator status fixture panels, autonomy bridge state, playlist dock, and Advanced telemetry drill-down.
- `apps/dashboard/src/App.css` owns the React dashboard visual system: dark operational palette, section/card grids, status pills, responsive layout, and Advanced telemetry styling.
- `apps/dashboard/src/index.css` still contains starter/global Vite styling and constrains `#root`; it is lower-priority for Phase 1 and should be avoided unless the later APPLY proves it blocks layout.

Read-only state boundary:

- `apps/dashboard/src/runtimeVisibilityAdapter.js` normalizes fixture and local API response shapes into a display model.
- `apps/dashboard/src/runtimeVisibilityClient.js` fetches `/api/runtime/visibility` with `GET` only and rejects non-`aios.runtime_visibility_api.v1` or non-`READ_ONLY` responses.
- `apps/dashboard/vite.config.js` wires a virtual autonomy bridge state module that reads `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` at build/dev time and falls back to `apps/dashboard/mock-data/autonomy_bridge_state.sample.json`.
- Vite proxies `/api` to `http://localhost:5050`.

Static preview/PWA/readiness:

- `apps/dashboard/index.html` redirects to `AIOS_STATIC_PREVIEW.html` and states no backend, API, persistence, service-worker registration, or trading automation is enabled.
- `apps/dashboard/AIOS_STATIC_PREVIEW.html`, `apps/dashboard/js/aios-static-preview.js`, and `apps/dashboard/css/aios-static-preview.css` remain the large static preview surface with rails, Work Table, Apps Hub, status panels, fixture-driven local UI, and a music dock.
- `apps/dashboard/manifest.webmanifest`, `apps/dashboard/service-worker.js`, `apps/dashboard/icons/`, and `apps/dashboard/PUBLISHING_READINESS.md` are readiness artifacts. The service worker is intentionally not registered and has no cache/fetch handler.
- `apps/dashboard/server.js` serves static files and a read-only `/live-data/autonomy_bridge_state.json` route.

Assets and mock data:

- Current visual anchors include `apps/dashboard/assets/ai_osgalaxy.theme.jpg`, `apps/dashboard/src/assets/hero.png`, `apps/dashboard/assets/aios-icon.svg`, `apps/dashboard/icons/aios-icon.svg`, and `apps/dashboard/assets/brand/`.
- `apps/dashboard/mock-data/` contains many fixture examples. The React app currently imports only `aios-runtime-visibility-v1.example.json`, `aios-operator-status-v1.example.json`, and the Vite virtual autonomy bridge fallback.

Orchestration writer:

- `automation/orchestration/dashboard/Update-AiOsDashboardState.ps1` writes `apps/dashboard/data/aios_live_state.json` when invoked. Phase 1 must not invoke or modify this writer.

Likely safe files for a later Phase 1 APPLY:

- `apps/dashboard/src/App.jsx`
- `apps/dashboard/src/App.css`
- `apps/dashboard/mock-data/aios-planetary-dashboard-state-v1.example.json`
- `apps/dashboard/skeleton/dashboard-structure.md`
- `apps/dashboard/skeleton/safety-rules.md`

Likely dangerous or avoid-first files:

- `apps/dashboard/package.json` and `apps/dashboard/package-lock.json`, because dependency changes expand blast radius.
- `apps/dashboard/vite.config.js`, because it controls static-copy behavior, virtual module behavior, and API proxying.
- `apps/dashboard/server.js`, because it controls local static serving and the live autonomy bridge route.
- `apps/dashboard/service-worker.js`, because service-worker activation/persistence is explicitly blocked.
- `apps/dashboard/manifest.webmanifest`, because publishing/PWA behavior is not part of Phase 1.
- `apps/dashboard/AIOS_STATIC_PREVIEW.html`, `apps/dashboard/js/aios-static-preview.js`, and `apps/dashboard/css/aios-static-preview.css`, because the static preview is large, fixture-heavy, and should not be changed in the same first React shell cut.
- Existing runtime visibility fixtures unless a later packet proves the schema must change.

Current build/preview commands:

```powershell
cd apps/dashboard
npm run build
npm run lint
npm run preview
npm run dev
npm run start
```

## Redesign Doc Alignment

The merged redesign docs require:

- A browser-first planetary command map.
- Five zones: Mars Lab, Moon Control, Earth Hub, Galaxy Intelligence, and Black Hole Vault.
- A first screen that shows only global status, AIOS EdgeMark, mode, safety state, current objective, next safe action, critical alerts, and zone entries.
- Raw telemetry, queues, scheduler, runtime, GitHub checks, workers, debug JSON, logs, freshness, and source trace moved into Advanced.
- AI_OS visual identity preserved as a brand/theme anchor.
- Realism-first visual direction: NASA / aerospace / mission-control, realistic sci-fi, premium fintech/trading terminal merged with space exploration.
- Keyboard, mouse, touch, and Xbox controller support planned through a unified command model.
- UE5 as future premium client evaluation only.
- Paper League and leaderboards simulated/paper-only.
- Broker/live trading blocked.

This prep recommends preserving the current Vite/React bridge and making Phase 1 a lightweight React/CSS implementation with no new dependency.

## Phase 1 Implementation Recommendation

Phase 1 should build a realistic 2D/2.5D planetary command shell in the existing React app.

Recommended scope:

- Replace the visible React first-screen hierarchy in `App.jsx` with `PlanetaryCommandShell`.
- Preserve runtime visibility, operator status fixture, and autonomy bridge data as read-only inputs.
- Add a new local fixture `apps/dashboard/mock-data/aios-planetary-dashboard-state-v1.example.json` for zone copy, visual labels, AIOS EdgeMark placeholder values, Paper League paper-only summary, and safe UI strings.
- Keep Advanced telemetry available through a collapsed drawer.
- Preserve `UNKNOWN`, `STALE`, `BLOCKED`, `NEEDS_APPROVAL`, `PASS`, `FAIL`, and `REVIEW` as text labels.
- Implement keyboard/mouse navigation first, with a small `useAiosInputNavigation` hook that can later absorb Gamepad API events.
- Add visual planets with CSS gradients, pseudo-elements, masks, layered backgrounds, and existing safe assets only.
- Avoid new dependencies, Three.js, React Three Fiber, Drei, Tailwind, shadcn/ui, GSAP, Framer Motion, and UE5 in the first APPLY.

The first pass should not try to deliver first-person astronaut mode. It should make the dashboard feel navigable and cinematic without adding heavy rendering, install steps, or runtime dependencies.

## Phase 1 Non-Goals

- No UE5 project.
- No first-person astronaut implementation.
- No multiplayer.
- No live leaderboard backend.
- No dependency installation.
- No Three.js or React Three Fiber unless separately approved.
- No game engine dependency.
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
- No public/remote exposure.

## Exact Proposed File Cut List

Primary later APPLY files:

- `apps/dashboard/src/App.jsx`: Introduce the planetary shell, status model derivation, zone list rendering, Advanced drawer, Paper League display boundary, and input navigation hook.
- `apps/dashboard/src/App.css`: Replace or substantially revise React dashboard styling with a cinematic planetary shell, responsive layout, focus states, reduced-motion rules, and safety label treatment.
- `apps/dashboard/mock-data/aios-planetary-dashboard-state-v1.example.json`: Add deterministic local fixture for zone definitions, AIOS EdgeMark placeholder/model values, paper-only league summary, visual copy, and blocked capability labels.
- `apps/dashboard/skeleton/dashboard-structure.md`: Update reference structure to reflect planetary shell plus Advanced drawer.
- `apps/dashboard/skeleton/safety-rules.md`: Update reference safety rules for planetary navigation, input controls, Paper League, and blocked protected actions.

Optional only if later APPLY proves it is necessary:

- `apps/dashboard/src/runtimeVisibilityAdapter.js`: Add derived display fields only if the planetary shell cannot compute them safely in `App.jsx`.
- `apps/dashboard/src/index.css`: Adjust global root constraints only if `App.css` cannot fully control the layout.

Files to avoid in first APPLY:

- `apps/dashboard/package.json`
- `apps/dashboard/package-lock.json`
- `apps/dashboard/vite.config.js`
- `apps/dashboard/server.js`
- `apps/dashboard/service-worker.js`
- `apps/dashboard/manifest.webmanifest`
- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`
- Existing runtime visibility/operator/autonomy fixtures unless separately approved.

## Proposed Component Cut List

The current app has local components in `App.jsx`, so the first APPLY should keep components local unless the file becomes unmanageable.

Recommended local components/functions:

- `PlanetaryCommandShell`
- `PlanetaryScene`
- `PlanetZoneNode`
- `AiosEdgeMarkPanel`
- `SafetyStatusStrip`
- `MissionObjectivePanel`
- `CriticalAlertsPanel`
- `PaperLeaguePanel`
- `AdvancedDrawer`
- `InputHelpOverlay`
- `StatusPill`
- `Metric`
- `useAiosInputNavigation`
- `buildPlanetaryDashboardModel`
- `deriveAiosEdgeMark`

Future split-file option after Phase 1 proves the shape:

- `apps/dashboard/src/components/PlanetaryCommandShell.jsx`
- `apps/dashboard/src/components/PlanetaryScene.jsx`
- `apps/dashboard/src/components/PlanetZoneNode.jsx`
- `apps/dashboard/src/components/AdvancedDrawer.jsx`
- `apps/dashboard/src/hooks/useAiosInputNavigation.js`
- `apps/dashboard/src/data/planetaryDashboardModel.js`

Do not split into new folders in the first APPLY unless Anthony explicitly approves that broader refactor.

## Visual Implementation Strategy

Use the existing React/CSS stack for Phase 1.

No-new-dependency first pass:

- Use CSS radial gradients, conic gradients, layered backgrounds, box shadows, and pseudo-elements for planets and orbital depth.
- Use existing `apps/dashboard/assets/ai_osgalaxy.theme.jpg` only as an existing brand reference if the later APPLY explicitly chooses to reference an already committed asset.
- Keep the uploaded visual identity image as a reference only. Do not commit it, copy it, or add it as an asset.
- Use restrained bloom/glow around status-critical elements and planet edges.
- Keep critical status text outside heavy visual effects.
- Add `prefers-reduced-motion` rules that remove orbit drift, parallax, shimmer, and camera-like movement.

Second pass if dependencies are later approved:

- Evaluate Three.js or React Three Fiber for browser 3D planets and orbital camera.
- Add compressed textures and physically based materials only after package/dependency approval.
- Add browser Gamepad API integration after keyboard/mouse command semantics are stable.

Avoid:

- SVG-only poster art as the primary experience.
- Low-poly planets.
- Cartoon spheres.
- Mobile-game reward UI.
- Heavy neon that reduces text contrast.
- Decorative effects that hide `BLOCKED`, `NEEDS_APPROVAL`, `UNKNOWN`, or `STALE`.

## AIOS Visual Identity Preservation Rules

The goal is not to change the AI_OS visual identity; the goal is to enhance it into a realistic, cinematic, game-navigable command system.

Preserve:

- Dark cinematic space background.
- Blue/purple energy language.
- Lightning/energy symbol direction.
- Signal tower / communications tower direction.
- Earth / global intelligence theme.
- Currency / trading / finance symbol direction.
- AIOS lettering.
- Tagline direction: intelligent, adaptive, yours.
- Reflective premium command-center mood.
- High-contrast futuristic fintech plus aerospace identity.

Enhance:

- Realism.
- Physical lighting.
- Material detail.
- Planetary realism.
- Reflections and depth.
- Premium fintech polish.
- Readability of AIOS and tagline treatment.
- Consistency across Mars, Moon, Earth, Galaxy, and Black Hole zones.

## Realism-First Implementation Rules

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

## Keyboard / Mouse / Xbox Input Implementation Plan

Phase 1 command model:

- `focusZone(zoneId)`
- `selectZone(zoneId)`
- `enterZone(zoneId)`
- `back()`
- `openAdvancedDrawer()`
- `closeAdvancedDrawer()`
- `moveFocus(direction)`
- `openInputHelp()`

Keyboard:

- Tab and Shift+Tab follow native focus order.
- Arrow keys or WASD move between zone nodes when focus is inside the planetary shell.
- Enter or Space selects the focused zone.
- Escape closes overlays, then returns to the galaxy/home view.
- `/` or Ctrl+K can be reserved for a later command palette.
- Visible focus rings are required.

Mouse/touch:

- Click/tap focuses or enters zones.
- Hover may show concise status, but hover content must not hide safety labels.
- Drag/orbit should be skipped in Phase 1 unless implemented as a harmless visual preview.

Xbox controller:

- Plan Gamepad API mapping but do not require implementation in Phase 1.
- Future mapping: D-pad/left stick move focus, A select, B back, X Advanced, Y command/search, LB/RB switch zones, Start/Menu help/system menu.
- No destructive one-button actions.

Accessibility:

- No keyboard trap.
- Focus order starts with global safety/status before decorative planets.
- Reduced-motion mode disables nonessential animation.
- Status is never color-only.

## Advanced Drawer Plan

The Advanced drawer should keep the existing raw/detail-heavy data available without making it the first-screen experience.

Move or retain inside Advanced:

- Runtime status details.
- Health summary.
- Queue counters.
- Active packets.
- Failed packets.
- Worker leases.
- Backpressure alerts.
- Telemetry log.
- Execution ledger.
- Operator status fixture details.
- Autonomy bridge source/fallback details.
- Debug/source/freshness details.

Rules:

- Default collapsed.
- Clearly labeled as operator/debug detail.
- Display-only.
- No mutation controls.
- No approval, scheduler, queue, worker, broker, or runtime action buttons.

## AIOS EdgeMark First-Pass Display Plan

Phase 1 should display AIOS EdgeMark as a transparent readiness placeholder/model, not as a fake live benchmark.

Recommended first-pass fields:

- Score value, such as `72`, sourced from the new fixture or derived conservatively from known display state.
- Confidence, such as `fixture` or `display model`.
- Band: `READY`, `REVIEW`, `NEEDS_APPROVAL`, or `BLOCKED`.
- Top reasons, such as `live trading blocked`, `runtime fixture stale`, `approval items visible`, or `validation evidence required`.
- Missing data lowers confidence.
- `UNKNOWN` never counts as success.

Do not imply live trading edge, live P&L, broker readiness, or real execution quality.

## Paper League First-Pass Display Boundaries

Paper League can appear as a small first-pass zone/panel only if it is explicitly simulated.

Allowed:

- Paper-only season placeholder.
- Learning mission status.
- Risk discipline score placeholder.
- Simulated leaderboard categories.
- AIOS EdgeMark education copy.

Blocked:

- Real-money framing.
- Gambling language.
- Broker credentials.
- Live P&L.
- Live order execution.
- Live leaderboard backend.
- External writes.
- Any UI that suggests one-click live trading.

## Testing / Preview Commands

Later implementation validation:

```powershell
git diff --check
cd apps/dashboard
npm run build
npm run lint
npm run preview
```

Manual preview:

- Open the local preview URL produced by Vite.
- Desktop screenshot review.
- Mobile viewport screenshot review.
- Keyboard-only walkthrough.
- Reduced-motion walkthrough.
- Advanced drawer open/close review.
- Confirm status labels remain readable over visual background.
- Confirm no secrets, broker controls, queue mutation, scheduler mutation, runtime mutation, approval mutation, live trading, or external exposure controls appear.

Repo validation:

```powershell
git status --short --branch
```

## Screenshot / Manual Review Checklist

- First viewport clearly signals AI_OS and the planetary command system.
- Mars, Moon, Earth, Galaxy, and Black Hole zones are visible and readable.
- Global safety state is visible before raw details.
- AIOS EdgeMark is labeled as readiness/discipline and does not imply live trading.
- Paper League is paper-only and simulated.
- `BLOCKED`, `NEEDS_APPROVAL`, `UNKNOWN`, `STALE`, `PASS`, and `FAIL` are text-visible.
- Advanced drawer contains raw telemetry/debug/operator detail.
- No critical text is hidden by bloom, gradients, motion, or planet art.
- Keyboard focus is visible and predictable.
- Reduced-motion mode removes nonessential motion.
- No uploaded visual identity image was committed.
- No UE5 project, dependency, provider config, runtime mutation, scheduler mutation, queue mutation, broker mutation, live trading, or secrets were introduced.

## Rollback Plan

- Keep implementation on a feature branch.
- Edit only exact approved files.
- Do not delete existing dashboard files during Phase 1.
- Run build/lint before PR.
- Capture before/after screenshots.
- If validation or manual review fails, restore only the exact changed files from the pre-implementation commit.
- Preserve current fixtures, Vite virtual module, static preview, server, service worker, manifest, and read-only runtime visibility API contract.

## Risk Register

- Browser performance: cinematic gradients, shadows, and animations can become expensive; use reduced motion and lightweight CSS first.
- Realism vs readability: realistic space art can hide text; keep safety labels in stable overlays.
- Dependency bloat: Three.js/R3F would add package changes; defer until separately approved.
- Dashboard state safety: do not expand live data sources or direct repo/runtime reads.
- Public/remote exposure: do not configure Cloudflare, Azure, DNS, tunnels, or publishing workflows in Phase 1.
- Game mechanics: Paper League must remain simulated and discipline-focused, not gambling or live-money competition.
- Controller support: browser Gamepad API differs by device/browser; plan hooks after keyboard semantics are stable.
- Visual identity drift: preserve AI_OS lettering, blue/purple energy, signal/global/trading motifs, and premium command-center mood.
- Static preview coupling: changing static preview alongside React shell would expand blast radius; keep it out of Phase 1.

## Exact Stop Point Before Implementation

Stop before editing or overwriting any file under `apps/dashboard/`.

The next APPLY packet must be reviewed and separately approved by Anthony before dashboard source changes. It must name exact files to change, exact files not to change, dependency policy, validators, local preview steps, screenshot/manual review requirements, rollback plan, and protected-action stop points.

