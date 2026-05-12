# Dashboard Change Boundary

Dashboard planning lives in docs. Dashboard code lives in `apps/dashboard/`.

No dashboard code edit is approved unless the user names the exact dashboard path.

Dashboard change types should stay separate:

- static preview HTML
- static preview CSS
- static preview JavaScript
- React app source
- dashboard mock data
- dashboard assets
- private media
- dashboard documentation

Blocked by default:

- hidden execution
- report writing
- telemetry persistence
- API calls
- broker controls
- OANDA controls
- live trading controls
- secrets
- credentials
- service worker changes unless named
- mixed unrelated dashboard commits

Before commit, dashboard changes need visual or text validation appropriate to the change.
