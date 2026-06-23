# AIOS Dashboard Capital Flow Panel V10 Report

## Objective
Add a compact Capital Flow / Treasury Control Panel to the minimalist dashboard using sanitized fixtures, custom AIOS icons, policy-status display, draft request visibility, and blunt safety language.

## Dashboard Files Changed
- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/App.css`
- `apps/dashboard/src/aiosSymbolManifest.js`
- `apps/dashboard/src/assets/aios-symbols/README.md`
- `apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json`
- `apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json`

## Icons Created
- `apps/dashboard/src/assets/aios-symbols/capital-flow.svg`
- `apps/dashboard/src/assets/aios-symbols/funds-sweep.svg`
- `apps/dashboard/src/assets/aios-symbols/resupply.svg`
- `apps/dashboard/src/assets/aios-symbols/compound-target.svg`
- `apps/dashboard/src/assets/aios-symbols/withdrawal-gate.svg`

## Capital Fields Added
- Capital Flow status
- Trading float
- Max trading float cap
- Minimum trading float floor
- Sweep threshold
- Resupply threshold
- Compounding threshold
- Compounding target
- Withdrawal request status
- Resupply request status
- Sweep request status
- Compound request status
- Maintenance window status
- Approval status
- Connector proof status
- Risk freeze status
- Last capital action
- Next safe capital action
- Sanitized account aliases
- Draft-only recommendations
- Draft-only request previews

## Mobile Readability
The panel collapses the treasury safety statements, status rows, metrics, aliases, and drawer cards to single-column layouts on narrow viewports.

## Desktop Readability
The panel uses the existing cockpit grid, compact metric tiles, status rows, and collapsed drawer layout to keep the top-level view readable.

## Safety Boundaries Preserved
- AIOS does not hold funds.
- AIOS does not move money from the dashboard.
- Account aliases only.
- Real transfers require future connector proof and human approval.
- Instant withdrawal/deposit depends on supported broker/bank/payment rails.
- No Buy, Sell, Execute, Place Order, Close Trade, Arm Live, deposit execution, withdrawal execution, or transfer execution control was added.

## Execution Authority Status
Display-only. The dashboard renders sanitized fixture data and local policy recommendations only.

## Validator Results
- `python -m pytest tests/forex_engine/test_capital_flow_policy_v1.py -q`: PASS, 10 passed.
- `python -m pytest tests/forex_engine/test_expectancy_ticket_gate_closure_v1.py -q`: PASS, 8 passed.
- `npm --prefix apps/dashboard run build`: PASS.
- `npm --prefix apps/dashboard run test --if-present`: PASS, no configured output.
- `npm --prefix apps/dashboard run lint --if-present`: PASS.
- `node --check apps/dashboard/src/aiosSymbolManifest.js`: PASS.
- `python -m compileall automation/forex_engine`: SANDBOX_LAUNCH_FAILURE_1312 after one retry.
- `git diff --check`: NOT RUN because validator chain stopped after repeated SANDBOX_LAUNCH_FAILURE_1312.
- Validator-chain `git status --short --branch`: NOT RUN because validator chain stopped after repeated SANDBOX_LAUNCH_FAILURE_1312.

Manual PowerShell validator commands remaining:

```powershell
python -m compileall automation/forex_engine
git diff --check
git status --short --branch
```

## Git Status
Final status command captured after the stopped validator chain:

```text
## feature/dashboard-restore-localhost-four-emoji-v1
 M apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json
 M apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json
 M apps/dashboard/src/AIOSLiveOperatorPanel.css
 M apps/dashboard/src/App.css
 M apps/dashboard/src/App.jsx
 M apps/dashboard/src/MinimalOperatorDashboard.jsx
 M apps/dashboard/src/PreservedLegacyModules.css
 M apps/dashboard/src/PreservedLegacyModules.jsx
?? Reports/dashboard_delivery/AIOS_DASHBOARD_CAPITAL_FLOW_PANEL_V10_REPORT.md
?? Reports/forex_delivery/AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V10.md
?? Reports/forex_delivery/AIOS_CAPITAL_FLOW_POLICY_SIMULATION_V10.md
?? Reports/forex_delivery/AIOS_CAPITAL_FLOW_TREASURY_CONTROL_PANEL_V10.md
?? apps/dashboard/src/aiosSymbolManifest.js
?? apps/dashboard/src/assets/aios-symbols/
?? automation/forex_engine/capital_flow_policy_v1.py
?? tests/forex_engine/test_capital_flow_policy_v1.py
```

Additional preserved dirty/untracked dashboard, forex, docs/legal, and report artifacts remain present and were not staged, committed, pushed, deleted, reset, stashed, or discarded.
