# Phase 24 Trading Lab Workstation Dry Run

Status: APPLY scaffold created and validator passed.

Scope:
- Professional forex workstation layout for the Trading Lab dashboard route.
- Local mock-data only.
- Paper-first validation.
- Latency-aware workflow.

Safety:
- live_trading: BLOCKED
- broker: BLOCKED
- oanda: BLOCKED
- api_keys: BLOCKED
- real_webhooks: BLOCKED
- real_orders: BLOCKED
- ai_assisted_execution: BLOCKED

Validation command:

```powershell
powershell -ExecutionPolicy Bypass -File automation\trading_lab\Test-AiOsTradingLabPhase24Workstation.DRY_RUN.ps1
```

Validation result:
- JSON fixture parse: PASS
- Contract parse: PASS
- Dashboard JS syntax: PASS
- Phase 24 workstation validator: PASS

Phase 24.1 ergonomics refinement:
- Promotes selected pair, latency, risk gate, primary next action, and current workflow step.
- Reduces repeated safety locks, profile list weight, latency detail weight, and repeated Pending validation chips.
- Keeps Advanced diagnostics collapsed.

No broker, OANDA, API keys, real webhooks, real orders, account connection, autonomous execution, commit, or push are part of this scaffold.
