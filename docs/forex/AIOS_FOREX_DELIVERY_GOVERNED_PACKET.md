# AI_OS Forex Delivery Governed Packet

Status: governed repo-side readiness packet.

This packet supports Forex Delivery readiness without granting live execution authority. It connects the existing Trading Lab / Forex paper, demo-review, and broker-sandbox evidence to the future Single Live Micro-Trade Exception review path.

## Authority Constraints

- `AGENTS.md` is the highest local Codex conduct and packet governance authority.
- `README.md` states Trading Lab / Forex is staged inside broker-capable AI_OS architecture and blocks live broker execution, real orders, broker credentials, and uncontrolled automation unless governed approval exists.
- `RISK_POLICY.md` blocks live trading, broker execution, OANDA or live order execution, real webhook execution, real orders, and broker credentials unless the Single Live Micro-Trade Exception is active.
- `docs/governance/AI_OS_REPO_MEMORY.md` records Forex Paper Bot work as paper/simulation gated unless separately approved.

## Existing Repo Components Used As Evidence

- `docs/AI_OS/trading/FOREX_OANDA_BOUNDARY.md` defines the active Forex and OANDA boundary.
- `docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.md` defines broker-paper sandbox readiness as non-live and protected-gate-only.
- `automation/forex_engine/broker_paper_presecurity_gate.py` defines blocked broker SDK, credential, network, webhook, scheduler, daemon, broker-paper order, and live-order capabilities.
- `automation/forex_engine/broker_paper_adapter_stub_contract.py` defines stub-only local intent validation.
- `automation/forex_engine/broker_specific_paper_demo.py` defines OANDA-shaped paper/demo mappings without OANDA SDK use, network calls, repo-stored credentials, live account access, or real order routing.
- `automation/forex_engine/oanda_demo_auth_handoff.py` defines the external OANDA demo authentication handoff readiness layer, credential boundary, demo account validation, failure states, and sanitized audit evidence without storing credentials.
- `automation/forex_engine/oanda_demo_runtime_handoff_intake.py` defines the protected runtime-handoff intake layer, sanitized metadata acceptance/rejection rules, account-ID rejection, credential-value rejection, live endpoint rejection, unauthorized intake rejection, and sanitized intake evidence without accepting credential values.
- `automation/forex_engine/oanda_demo_runtime_handoff.py` defines the runtime-only handoff contract, runtime-auth-reference validation, runtime-boundary enforcement, account-ID rejection, credential-value rejection, sanitized handoff evidence, and fail-closed validation without accepting credential values.
- `automation/forex_engine/oanda_demo_connection_gate.py` defines the one-shot OANDA practice/demo connection gate specification, runtime-only auth boundary requirements, sanitized connection evidence schema, no-order/no-account-ID logging rules, network/broker-call approval gate, timeout controls, and fail-closed readiness validation without making a broker connection.
- `automation/forex_engine/oanda_demo_connection_probe.py` defines the guarded OANDA practice/demo probe validation path, runtime-auth reference interface, fail-closed CLI argument rejection, sanitized probe evidence schema, one-shot stop controls, and validation-only probe command boundary without making a broker connection.
- `automation/forex_engine/oanda_demo_protected_connection_attempt.py` defines the protected one-shot OANDA practice/demo connection/auth proof boundary, external runtime connector interface, required approval/runtime fields, fail-closed preflight, sanitized result model, connector-output sanitization, and no-account/no-order/no-market-data/no-live protections.
- `automation/forex_engine/live_micro_trade_contract.py` defines contract-only fail-closed Single Live Micro-Trade validation.

## Governed Delivery Chain

| Chain link | Repo-side status |
|---|---|
| BROKER CONNECT | Paper/demo adapter connection only; real broker connection blocked. |
| AUTHENTICATION | Paper/demo local session only; broker credential material blocked. |
| OANDA DEMO AUTH HANDOFF READINESS | External demo-auth readiness contract only; missing, malformed, unsupported, live-account, or execution-attempt inputs fail closed. |
| OANDA DEMO RUNTIME HANDOFF INTAKE | Protected intake contract for sanitized runtime-handoff metadata; account IDs, credential-like values, live endpoint references, malformed references, and unauthorized intake attempts fail closed. |
| OANDA DEMO RUNTIME HANDOFF | Runtime-only boundary contract; missing/malformed runtime references, account IDs, credential-like values, live endpoints, and unauthorized probe attempts fail closed. |
| OANDA DEMO CONNECTION GATE | One-shot practice/demo connection gate specification only; missing approval, missing runtime auth proof, account identifiers, credential-like values, live endpoints, order routes, network/API enablement, and missing stop controls fail closed. |
| OANDA DEMO CONNECTION PROBE | Validation-only guarded probe command; sanitized runtime-auth reference metadata, one-shot stop controls, CLI rejection, and evidence schema exist, but no broker connection is performed. |
| OANDA PROTECTED DEMO CONNECTION ATTEMPT | Protected one-shot practice/demo connection/auth proof boundary; it can call an injected external runtime connector once after all gates pass, then stores sanitized evidence only and stops. |
| MARKET DATA | Paper/demo adapter reads deterministic local fixture price only. |
| ACCOUNT STATE | Paper/demo adapter returns sanitized in-memory account state only. |
| RISK CHECK | Pair allowlist, spread, margin, position size, max loss, and stop-loss gates. |
| ORDER BUILD | Paper-only payload builder with no broker request. |
| PAPER EXECUTION | Paper/demo adapter creates a simulated order/fill/position only. |
| FILL VERIFY | Paper/demo simulated fill status recorded as evidence. |
| POSITION MONITOR | Paper/demo adapter returns in-memory position state only. |
| POSITION CLOSE | Paper/demo adapter closes simulated position and captures P/L only. |
| BROKER-SPECIFIC MAPPING | OANDA-shaped paper/demo reference mappings only; no OANDA API client, no network/API call, no live account access, and no real order routing. |
| EVIDENCE LOG | Sanitized local paper/demo adapter, auth handoff readiness, and OANDA-shaped mapping evidence record. |
| LIVE MICRO-TRADE ARMING CHECKLIST | Field completeness check only; live submission remains blocked. |

## Required Stop Point

Repo-side governed live micro-trade readiness packet complete; live order remains blocked until Human Owner activates the Single Live Micro-Trade Exception with all required `RISK_POLICY.md` fields.

## Dry-Run Command

```powershell
python scripts/forex_delivery/validate_forex_delivery_readiness.py --mode paper
```

This command prints a sanitized paper readiness result. It does not call a broker, read credentials, use network APIs, write reports, or submit orders.
