# Forex Dashboard Runtime UI V1

This is a static, local, repo-safe dashboard preview for Forex 110 completion state.

Open `docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.html` or `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_PREVIEW.html` directly in a browser.

## Emoji Windows

- 🏛️ **Command Center** - Forex 110 completion, blocker state, and next safe action.
- 🛡️ **Safety Gate** - Protected actions are blocked in this local dashboard preview.
- 🎯 **Candidate** - Selected candidate is review-ready, not execution-authorized.
- 📊 **Evidence** - Evidence status is visible without raw-data overload.
- 🚧 **Broker Boundary** - Broker connection proof is owner-gated and separate.
- 💰 **Profit Readiness** - Profit readiness is display-only.
- 📁 **Reports** - Report index for the local evidence used by this UI.
- 🆘 **SOS** - Escalate only if protected boundaries are violated or source artifacts go missing.
- ⚙️ **Settings** - Display preferences only; no execution controls.
- 🔒 **Secrets Later** - Bitwarden remains locked until owner confirmation after Forex 110.

## Default View

The first view shows only critical status, blockers, next safe action, and safety state.

## Hidden Detail Windows

Raw report detail, validator-heavy data, metadata, broker-boundary detail, candidate metrics, and evidence detail stay behind clickable emoji windows.

## Protected Behavior

This UI reads local Forex report artifacts only. It has no broker contact, no credential handling, no env reads, no account identifiers, no account inspection, no order execution, no demo authorization, no live authorization, no scheduler, no daemon, no webhook, and no background loop.

## Bitwarden Boundary

Bitwarden and Vaultwarden remain locked. Secrets migration and token storage are not started by this dashboard.

## Forex 110 Relationship

This complements Forex 110 by turning the completed repo-safe evidence gate into a readable dashboard preview while preserving the protected broker/live/secrets boundary.

Status: `FOREX_DASHBOARD_RUNTIME_UI_READY`
