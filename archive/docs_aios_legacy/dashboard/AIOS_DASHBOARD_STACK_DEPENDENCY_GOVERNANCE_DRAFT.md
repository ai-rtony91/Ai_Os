# AI_OS Dashboard Stack Dependency Governance Draft

## Purpose

This draft defines stack and dependency governance for future dashboard preview planning.

No protected root files are edited by this draft. Human approval is required before adding packages or changing dependencies. This draft creates no live automation, no production dashboard, and no trading automation.

## Governance Rules

- Static-first preview preference.
- No production services yet.
- No hidden background services.
- No auto-start behavior.
- No unaudited network dependencies.
- Dependency inventory required before install.
- Approval required before adding packages.
- Rollback plan required for package changes.

## Dependency Boundary

This draft does not install dependencies. Future dependency work requires explicit approval, package inventory, rollback plan, and validator pass before commit.

## Boundary

This draft does not activate production dashboard services, live automation, startup tasks, or trading automation.
