# AI_OS Dashboard Transition Ergonomics Draft

## Purpose

Plan smooth, readable dashboard transitions without heavy animation.

## Desktop Rules

- One active major panel at a time.
- Drawer hide/show remains independent from panel state.
- MENU stays in the top nav leading slot.
- Content rail remains controlled so panels do not stretch wildly.

## Mobile Rules

- Drawer remains overlay.
- Main navigation wraps or scrolls safely.
- Widgets stack vertically.
- Touch targets remain large enough for mobile use.
- No horizontal overflow.

## Motion Rules

- Use lightweight opacity and transform transitions.
- Avoid heavy animation, WebGL, canvas, external libraries, or external assets.
- Respect `prefers-reduced-motion: reduce`.

## Safety Rules

Transitions are visual only and must not trigger file writes, API calls, account connections, broker actions, or deployment.
