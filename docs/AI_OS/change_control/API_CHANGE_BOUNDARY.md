# API Change Boundary

API means a software connection that lets one system talk to another.

API planning may describe future request shapes, response shapes, and safety checks.

Blocked unless separately approved:

- real API keys
- secrets
- tokens
- real network calls
- deployed endpoints
- background services
- account login systems
- broker APIs
- OANDA APIs
- live trading APIs

API changes must be separate from UI changes unless the user names both scopes and approves both.

Mock JSON examples are allowed only when they contain no secrets, no real account data, and no live execution path.
