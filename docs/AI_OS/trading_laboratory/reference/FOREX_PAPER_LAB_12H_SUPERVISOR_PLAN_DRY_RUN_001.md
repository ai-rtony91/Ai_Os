# Forex Paper Lab 12H Supervisor Plan DRY_RUN 001

## Status

- DRY_RUN preparation report only.
- Does not start Night Supervisor.
- Does not enable or disable a scheduled task.
- Does not edit runtime behavior.
- Does not authorize APPLY, commit, push, merge, broker work, webhook execution, API keys, secrets, real market data, real orders, or live trading.

Base44 gives us the map. AIOS Lab paints the map later.

## Scope

This plan prepares a safe 12-hour Night Supervisor work session for the AIOS Lab Forex Paper Trading Simulation workflow.

Focus areas:

1. Signal Intake
2. Risk Gate / Safety Check
3. Practice Ledger / Paper Trade Review
4. Latency Tracker
5. Scorecard / Reports
6. Strategy Journal / Strategy Studio
7. Educational Use Only wording
8. Base44 reference map alignment

## Files Inspected

- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/night_supervisor/README.md`
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_CONFIG.json`
- `automation/orchestration/night_supervisor/NIGHT_SUPERVISOR_SAFETY_POLICY.json`
- `telemetry/night_supervisor/reports/night_summary_2026-06-02.json`
- `telemetry/night_supervisor/alerts/night_alert_2026-06-02.json`
- `telemetry/night_supervisor/night_ledger.jsonl`
- `docs/AI_OS/trading_laboratory/reference/BASE44_FOREX_PAPER_TRADING_LAB_REFERENCE_001.md`
- `apps/dashboard/mock-data/trading-lab-workspace.example.json`
- `apps/dashboard/mock-data/trading-lab-paper-runner.example.json`
- `apps/dashboard/mock-data/trading-lab-latency-replay.example.json`
- `apps/dashboard/mock-data/trading-lab-performance-review.example.json`
- `apps/dashboard/mock-data/trading-lab-strategy-ranking.example.json`
- `apps/dashboard/mock-data/trading-lab-evidence-analyzer.example.json`
- `apps/trading_lab/README.md`
- `apps/trading_lab/trading_lab/models.py`
- `apps/trading_lab/trading_lab/ingest/paper_signal_api.py`
- `apps/trading_lab/trading_lab/ingest/paper_signal_test_pack_runner.py`
- `apps/trading_lab/trading_lab/execution/risk_gate.py`
- `apps/trading_lab/trading_lab/execution/live_broker_stub.py`
- `apps/trading_lab/trading_lab/runner/paper_bot_runner.py`
- `apps/trading_lab/trading_lab/reports/paper_signal_scorecard.py`
- `apps/trading_lab/trading_lab/reports/paper_runtime_summary.py`

## 1. 12-Hour Run Support

Partially supported.

`automation/orchestration/Invoke-AiOsNightCycle.ps1` already supports:

- `-Watch`
- `-IntervalSeconds`
- `-MaxCycles`
- `-Apply`
- `-MorningBrief`
- `-ResumeFrom`

A later approved run could approximate 12 hourly checkpoints with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/Invoke-AiOsNightCycle.ps1 -Watch -IntervalSeconds 3600 -MaxCycles 12
```

Important limit: this is cycle-count based, not a strict wall-clock 12-hour cutoff. Each cycle duration adds time before the next sleep. A dedicated 12-hour profile should add explicit wall-clock cutoff evidence before unattended use.

## 2. Timer / Duration Limit

Existing timer controls:

- `IntervalSeconds`: validated range 5 to 86400 seconds.
- `MaxCycles`: validated range 1 to 1000000, where `0` means unlimited while `-Watch` is active.

Missing:

- No dedicated `-MaxHours 12` parameter.
- No dedicated Forex Paper Lab 12-hour profile.
- No per-hour work-queue binding.
- No guarantee that one cycle equals one hour of useful Trading Lab work.

## 3. STOP Marker Behavior

STOP behavior exists.

`Invoke-AiOsNightCycle.ps1` defines:

```text
control/self_continuation/STOP
```

The script checks this marker:

- before each cycle.
- before sleep while watching.
- after sleep while watching.

When present, it logs a stopped state, closes the cycle marker when needed, updates dashboard state, and exits with code `0`.

Recommended safety requirement for any later 12-hour run:

- The STOP marker path must be verified before launch.
- The operator must know the exact stop-marker command before launch.
- The run must not begin if the STOP marker cannot be created or verified.

## 4. Approval / Blocker Handling

Approval and blocker handling exists, but it must stay report-first.

Night Supervisor currently:

- classifies approval inbox evidence.
- keeps LOW auto-approval disabled in DRY_RUN.
- holds MEDIUM, HIGH, UNKNOWN, governance, and protected-action items for Human Owner review.
- writes proposed state under `telemetry/night_supervisor/`.
- does not grant APPLY, commit, push, merge, worker launch, scheduler authority, broker authority, or live trading authority.

Night cycle can pass `-Apply` only to child steps that already support apply gates. That is too broad for a Forex Paper Lab session unless a dedicated scoped queue and gate are created first.

Recommendation: run the 12-hour Forex Paper Lab session as report/plan-only until a separate approved packet creates a scoped work queue and explicit allowlist.

## 5. Tasker / Telegram Alert Bridge

Status: missing for live external wake-up.

Observed alert capability:

- File-channel SOS output exists under `relay/reports/SOS_OUTBOX/`.
- Local alert files exist under `telemetry/night_supervisor/alerts/`.
- Notification config defaults to `file`.
- Telegram/webhook style channels require credentials and remain gated.

Missing or not approved:

- No confirmed Tasker bridge.
- No confirmed Telegram live-send approval.
- No approved notification secrets.
- No approved phone wake-up path.

This means a 12-hour unattended run can write local alerts, but cannot reliably wake the Human Owner through Tasker/Telegram unless a separate notification-bridge APPLY packet is approved and validated first.

## 6. Safe Unattended Work

Night Supervisor can safely do this unattended when kept in report-only mode:

- collect repo/status/safety baseline evidence.
- inspect existing Trading Lab files and dashboard mock-data.
- compare workflow coverage against the Base44 reference map.
- draft gap reports.
- draft APPLY packet proposals.
- draft validator/checklist proposals.
- write report outputs only under an approved report path.
- preserve Educational Use Only and Paper Trading Simulation boundaries.
- keep live execution, broker, OANDA, Webull, Alpaca, real orders, webhook execution, real market data, API keys, and secrets blocked.

## 7. Must Stop And Ask

Night Supervisor must stop and ask for Human Owner approval before:

- editing repo files beyond approved report outputs.
- creating or changing dashboard UI, CSS, theme, layout, colors, assets, typography, icons, or visual identity.
- changing Trading Lab runtime code.
- changing scheduler state.
- enabling the disabled `AIOS_Night_Cycle` task.
- creating branches, commits, pushes, PRs, or merges.
- creating or moving work packets into active execution state.
- releasing locks.
- approving packets.
- connecting Tasker, Telegram, webhook, broker, OANDA, Webull, Alpaca, TradingView, or live market data.
- reading, writing, printing, or storing secrets.
- creating real orders or live trading paths.

## 8. Recommended 12-Hour Work Queue

Hour 1: repo/status/safety baseline

- Verify branch and clean state.
- Verify `AIOS_Night_Cycle` is intentionally disabled unless separately approved.
- Verify Live Execution Blocked / No Real Orders language remains visible.
- Output: `hour_01_repo_status_safety_baseline.md`.

Hour 2: forex paper workflow map

- Compare Base44 map to AIOS Lab Trading Lab assets.
- Preserve AIOS Lab visual identity.
- Output: `hour_02_forex_paper_workflow_map.md`.

Hour 3: signal intake gap report

- Inspect paper signal API, test pack, dashboard fixtures, and signal handoff examples.
- Identify duplicate prevention, validation, and ID alignment gaps.
- Output: `hour_03_signal_intake_gap_report.md`.

Hour 4: risk gate gap report

- Inspect `risk_gate.py`, risk fixtures, and dashboard risk gate language.
- Identify bypass, confirmation, and service-layer gaps.
- Output: `hour_04_risk_gate_gap_report.md`.

Hour 5: practice ledger gap report

- Inspect paper runner outputs, paper result ledger, and paper review status.
- Prefer Practice Ledger / Paper Trade Review wording.
- Output: `hour_05_practice_ledger_gap_report.md`.

Hour 6: latency tracker gap report

- Inspect latency replay, latency ledger, stale-signal thresholds, and negative-latency evidence.
- Standardize 300-second delay and 900-second stale boundaries for later review.
- Output: `hour_06_latency_tracker_gap_report.md`.

Hour 7: scorecard/report gap report

- Inspect scorecard, performance review, runtime summary, and paper signal scorecard.
- Keep P/L in R-multiples and avoid money/profit claims.
- Output: `hour_07_scorecard_reports_gap_report.md`.

Hour 8: strategy journal gap report

- Inspect strategy ranking, evidence analyzer, strategy metrics, and journal records.
- Identify Strategy Journal / Strategy Studio rebuild needs.
- Output: `hour_08_strategy_journal_gap_report.md`.

Hour 9: wording/safety-label gap report

- Identify remaining rough wording such as mock-only, bot, execution, or order-like language.
- Recommend Educational Use Only / Paper Trading Simulation wording without changing UI.
- Output: `hour_09_wording_safety_label_gap_report.md`.

Hour 10: packet queue generation

- Draft proposed DRY_RUN and APPLY packets only.
- Do not activate or enqueue execution.
- Output: `hour_10_packet_queue_proposals.md`.

Hour 11: validator/checklist generation

- Draft validators/checklists for paper-only safety, wording, schema, latency, and report outputs.
- Do not execute validators unless explicitly approved.
- Output: `hour_11_validator_checklist_proposals.md`.

Hour 12: final digest and next-action queue

- Summarize all reports.
- Rank the next safe APPLY packet.
- Output: `hour_12_final_digest_next_action_queue.md`.

## 9. Proposed Hourly Checkpoints

Each checkpoint should record:

- timestamp.
- current branch.
- git status summary.
- active hour.
- files inspected.
- outputs written.
- blockers found.
- safety confirmation.
- next safe action.

Each checkpoint should explicitly state:

- Educational Use Only.
- Paper Trading Simulation only.
- Live Execution Blocked.
- No Real Orders.
- No broker/OANDA/Webull/Alpaca.
- No webhook execution.
- No API keys or secrets.
- No automatic merge or push.
- No dashboard visual identity changes.
- No Base44 code/style import.

## 10. Proposed Stop Conditions

Stop immediately if:

- STOP marker exists at `control/self_continuation/STOP`.
- repo branch is not the expected branch.
- git status shows unexpected uncommitted changes outside approved report outputs.
- a requested action would edit runtime code, dashboard visuals, CSS, assets, theme, layout, or component structure.
- a requested action would create, enable, disable, or delete a scheduled task.
- a requested action would connect broker, webhook, Tasker, Telegram live send, API, market data, secrets, or real orders.
- a validator fails or cannot prove safety.
- a report suggests APPLY without a separate Human Owner approval packet.
- output path would leave the approved report/reporting boundary.
- Base44 code, CSS, theme, layout, icons, or branding language appears in a proposed implementation.
- live-trading wording or order-placement behavior appears in proposed work.

## 11. Proposed Output Files

Recommended later output root:

```text
telemetry/night_supervisor/forex_paper_lab_12h/YYYY-MM-DD/
```

Recommended files:

- `run_manifest.json`
- `hour_01_repo_status_safety_baseline.md`
- `hour_02_forex_paper_workflow_map.md`
- `hour_03_signal_intake_gap_report.md`
- `hour_04_risk_gate_gap_report.md`
- `hour_05_practice_ledger_gap_report.md`
- `hour_06_latency_tracker_gap_report.md`
- `hour_07_scorecard_reports_gap_report.md`
- `hour_08_strategy_journal_gap_report.md`
- `hour_09_wording_safety_label_gap_report.md`
- `hour_10_packet_queue_proposals.md`
- `hour_11_validator_checklist_proposals.md`
- `hour_12_final_digest_next_action_queue.md`
- `blocked_actions.json`
- `next_apply_packet_recommendation.md`

No dashboard, runtime, broker, webhook, API, secret, CSS, theme, asset, or Trading Lab code files should be changed by the 12-hour run.

## 12. Exact Next APPLY Packet Needed

Before any 12-hour session starts, create a separate APPLY packet for a scoped 12-hour report-only runner.

Recommended packet:

```text
identity marker: AI_OS_FOREX_PAPER_LAB_12H_REPORT_RUNNER
mode: APPLY
zone: report-only runner scaffold
lane: night-supervisor-forex-paper-lab
mission: create a dedicated report-only 12-hour Forex Paper Lab runner/wrapper that uses existing Night Cycle STOP semantics, enforces MaxCycles 12, IntervalSeconds 3600, report-only output paths, and hard blocked-path checks.
allowed paths:
- automation/orchestration/night_supervisor/
- telemetry/night_supervisor/
- docs/AI_OS/trading_laboratory/reference/
forbidden paths:
- apps/dashboard/css/
- apps/dashboard/assets/
- apps/trading_lab/ execution code unless separately approved
- broker/
- webhooks/
- API/secret files
- .env
- AGENTS.md
- README.md
- WHITEPAPER.md
- docs/governance/
- docs/architecture/
stop point: create wrapper/report contracts only; do not run the 12-hour session.
```

The APPLY packet should add:

- a dedicated 12-hour report-only plan runner or config profile.
- explicit output root under `telemetry/night_supervisor/forex_paper_lab_12h/`.
- wall-clock cutoff or cycle cutoff evidence.
- preflight check proving the STOP marker can be created by the operator.
- preflight check proving `AIOS_Night_Cycle` remains disabled unless separately approved.
- alert status check showing file-channel only unless Tasker/Telegram is separately approved.
- hard blocked-path list for dashboard visuals, trading execution, brokers, webhooks, APIs, and secrets.

## Recommendation

Do not start the 12-hour run yet.

Safest path:

1. Keep `AIOS_Night_Cycle` disabled tonight unless separately re-enabled.
2. Approve a narrow APPLY packet to create the dedicated 12-hour report-only runner/profile.
3. Validate STOP marker behavior and output paths.
4. Validate local file-channel SOS output.
5. Defer Tasker/Telegram until a separate notification bridge approval proves credentials and live-send safety.
6. Start the 12-hour run only after those gates pass.

## Safety Confirmation

- Educational Use Only.
- Paper Trading Simulation only.
- Live Execution Blocked.
- No Real Orders.
- No broker connection.
- No OANDA, Webull, or Alpaca.
- No webhook execution.
- No real market data.
- No API keys.
- No secrets.
- No automatic merge.
- No automatic push.
- No dashboard theme, CSS, layout, color, or visual identity changes.
- No Base44 code/style import.
