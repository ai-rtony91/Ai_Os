# AI_OS Phase 13 Stage 13.2 Mobile Drawer/Menu Responsive Validation DRY_RUN

Date: 2026-05-07
Mode: DRY_RUN
Classification: AI_OS project work only

## Stage

Phase 13 - Dashboard UI Implementation

Stage 13.2 - Mobile Drawer/Menu Responsive Validation

## Mission

Verify and plan mobile behavior for the dashboard MENU reopen control after Stage 13.1 drawer changes. The MENU button must remain visible, aligned, and non-overlapping while the drawer remains fully hidden when closed and opens as a safe overlay on mobile.

## Files Inspected

- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/js/aios-static-preview.js

## Current Desktop Behavior

- MENU is inside the top navigation row before Work Table.
- MENU is hidden while the drawer is open.
- MENU is displayed when `body.sidebar-collapsed` is active.
- The drawer closed state uses a zero-width / zero-height / hidden / no-pointer-events rule.
- Desktop closed layout changes the dashboard grid to `0 minmax(0, 1fr)` so main content can expand.
- Drawer state persists through `sessionStorage` using `aios.drawer.closed`.

## Current Mobile Behavior Observed From CSS/JS

- Mobile breakpoint at `max-width: 1120px` changes dashboard shell to one column.
- The drawer becomes fixed overlay width `min(84vw, 320px)`.
- `.drawer-reopen` is displayed by default in the mobile media block.
- `body.sidebar-open .drawer-reopen` hides MENU while overlay drawer is open.
- `body.sidebar-open .drawer-backdrop` displays the backdrop.
- `max-width: 720px` changes the top nav to a two-column grid and gives `.drawer-reopen` the same min-height as status chips.
- `max-width: 430px` changes status strip and status panel tabs to one column.

## Mobile Risks

1. At widths below 430px, `body.sidebar-collapsed .status-strip` may still attempt a two-column rule from the 720px block before the later one-column rule, depending cascade order and selector strength.
2. Mobile MENU visibility currently depends on the 1120px media block rather than only the saved closed state. This is acceptable for access, but APPLY should verify it does not visually appear during unintended open states.
3. The two-column 720px layout could place MENU beside Work Table correctly, but long labels such as System Status and Run Diagnostics need preview validation to confirm no horizontal pressure.
4. The status panel tab row below the top nav must be checked separately for no overlap after nav wraps.

## Mobile Fix Plan For APPLY

No immediate code change is approved in this DRY_RUN. If preview validation shows overlap or wrapping issues, APPLY should edit only:

- apps/dashboard/css/aios-static-preview.css

Planned safe CSS changes if needed:

- Add an explicit `body.sidebar-collapsed .status-strip { align-items: center; }` inside mobile breakpoints.
- At `max-width: 430px`, ensure `body.sidebar-collapsed .status-strip` resolves to `grid-template-columns: 1fr` or a stable first-row MENU slot that does not overlap other buttons.
- Preserve `.drawer-reopen { justify-self: center; align-self: center; }`.
- Keep MENU in the top navigation control area, not fixed over content.
- Keep drawer overlay controlled by `body.sidebar-open`.
- Do not edit HTML/JS unless visual validation proves CSS cannot solve the issue.

## Preview Validation Checklist

Desktop:

- Close drawer.
- Confirm no left rail, logo, App Dock text, drawer buttons, or safety lock panel remain.
- Confirm MENU is centered in the leading top nav slot before Work Table.
- Confirm Work Table, Reports, Telemetry, Admin, System Status, and Run Diagnostics do not overlap.

Tablet / Mobile:

- Test around 1120px, 720px, and 430px widths.
- Confirm MENU remains reachable while drawer is closed.
- Confirm MENU does not cover Work Table or any status panel buttons.
- Confirm top nav wraps cleanly without horizontal scroll.
- Confirm opening MENU shows overlay drawer with backdrop.
- Confirm drawer content is scrollable.
- Confirm Escape/backdrop close behavior remains safe.

## Files To Edit On APPLY

Planned only if preview validation finds a visible mobile issue:

- apps/dashboard/css/aios-static-preview.css

No APPLY changes should edit:

- protected root governance files
- dashboard folders or new standalone dashboard files
- broker, database, live AI API, or deployment logic

## Safety Blocks Confirmed

- No secrets.
- No external APIs.
- No database connection.
- No broker connection.
- No live AI API connection.
- No live trading code.
- No deployment.
- No protected root governance file modification.
- No dual Codex / POI / worktree files.

## DRY_RUN Result

DRY_RUN_COMPLETE_PENDING_APPLY

The current implementation appears structurally safe for mobile overlay behavior, but visual preview validation is still required before deciding whether a CSS-only APPLY fix is needed.

## Next Safe Action

Run APPLY only after operator approval if preview testing confirms mobile overlap, wrapping, or readability issues.
