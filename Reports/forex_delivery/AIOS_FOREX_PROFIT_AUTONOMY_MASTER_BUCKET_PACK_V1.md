# AIOS Forex Profit Autonomy Master Bucket Pack V1

## Bucket Identity
bucket_id: AIOS-FOREX-PROFIT-AUTONOMY-MASTER-BUCKET-PACK-V1
lane: forex-profit-autonomy-master-bucket-pack
mode: APPLY
worktree: C:\Dev\Ai.Os
branch: resolved after preflight

## Anthony Mission
Anthony's mission is to build AIOS toward profit autonomy through evidence, governed execution, risk controls, broker-state reconciliation, operator approval, and compounding only after proof.

## Hard Requirement
Guaranteed profit autonomy is treated as a proof requirement.
AIOS must prove it or block it.
This bucket does not fake proof.
Synthetic, paper, and demo-only evidence must never be used to claim real-money readiness.

## Current Landed Milestones
- Profit Validation Loop V1.
- Loss To Next Profit Candidate Gate V1.
- Candidate Evidence Intake V1.
- Candidate To Gate Bridge V1.
- Review-Ready Candidate Selector V1 local-only dependency detected from the current untracked selector files and report.

## Master Bucket Sequence

### FX-BUCKET-00-STATE-AUTHORITY-PREFLIGHT
stage id: FX-BUCKET-00-STATE-AUTHORITY-PREFLIGHT
title: State, Authority, and Dirty-File Preflight
purpose: Confirm repo, branch, dirty files, AGENTS.md, README.md, whitepaper, source-of-truth map, and active system map.
entry criteria:
- active worktree is C:\Dev\Ai.Os.
- current branch is observed without checkout.
- dirty files are classified.
exit criteria:
- wrong worktree is blocked.
- unrelated dirty files are blocked.
- conflicting authority is blocked.
validators:
- pwd.
- git status --short --branch.
- git branch --show-current.
- git remote -v.
- git log -1 --oneline.
blocked actions:
- checkout.
- branch switch.
- merge.
- rebase.
- stash.
- reset.
- clean.
owner approval boundary: Anthony approval required for any protected action.
next stage: FX-BUCKET-01-SELECTOR-LANDED-GATE
stop point: Stop if worktree, branch, dirty state, or authority is unsafe.

### FX-BUCKET-01-SELECTOR-LANDED-GATE
stage id: FX-BUCKET-01-SELECTOR-LANDED-GATE
title: Review-Ready Candidate Selector Landing Gate
purpose: Complete selector local validation, then require commit, push, PR, checks, and merge through protected-action approval.
entry criteria:
- selector files are present or missing state is known.
- selector tests are validated or blocked by explicit validator failure.
- untracked selector files are recognized as local-only dependency files.
exit criteria:
- selector is committed only after Anthony approval.
- selector is pushed only after Anthony approval.
- selector PR is created only after Anthony approval.
- selector is merged only after Anthony approval and checks.
validators:
- selector py_compile.
- selector focused pytest.
- git diff --check.
- protected commit/push/PR gate review.
blocked actions:
- stage.
- commit.
- push.
- PR create.
- merge.
- direct push to main.
owner approval boundary: Anthony approval required for every protected Git action.
next stage: FX-BUCKET-02-PROFIT-PROOF-LEDGER
stop point: Stop after reporting selector landing requirement. Do not stage or commit.

### FX-BUCKET-02-PROFIT-PROOF-LEDGER
stage id: FX-BUCKET-02-PROFIT-PROOF-LEDGER
title: Profit Proof Ledger V1
purpose: Centralize evidence proving or blocking profit-autonomy claims.
entry criteria:
- Review-Ready Candidate Selector V1 is landed.
- candidate proof categories are known.
- no guaranteed-profit claim is made.
exit criteria:
- proof ledger records every required proof category.
- missing proof is explicit.
- guaranteed_profit_proven remains false unless every category passes.
validators:
- proof ledger schema validation.
- deterministic JSON output.
- focused pytest.
- git diff --check.
blocked actions:
- guaranteed profit claim.
- real money approval.
- compounding approval.
- broker action.
owner approval boundary: Anthony approval required for any proof promotion that changes execution posture.
next stage: FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET
stop point: Stop after proof ledger reports missing and passed proof categories.

### FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET
stage id: FX-BUCKET-03-CANDIDATE-REVIEW-DECISION-PACKET
title: Candidate Review to Operator Decision Packet V1
purpose: Turn selected review-ready candidate into a human-readable decision packet.
entry criteria:
- selected review-ready candidate exists.
- proof ledger is available.
- blocked and not-approved actions are listed.
exit criteria:
- selected candidate is named.
- selection reason is shown.
- next safe action is one exact action.
validators:
- operator text readback.
- JSON output parse.
- candidate selection trace review.
- git diff --check.
blocked actions:
- demo trade approval.
- broker action.
- real money approval.
- compounding approval.
owner approval boundary: Anthony decides whether a future demo approval packet may be created.
next stage: FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE
stop point: Stop after creating the review decision packet.

### FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE
stage id: FX-BUCKET-04-DEMO-PERMISSION-ENVELOPE
title: Demo Trade Permission Envelope V1
purpose: Determine whether another controlled demo trade is even eligible for approval.
entry criteria:
- review-ready selected candidate.
- profit proof ledger sufficient for demo review.
- broker read-only state available or explicitly mocked only for planner.
- risk envelope complete.
- owner demo approval is represented for any future approval.
exit criteria:
- demo eligibility is explicit.
- broker_action_allowed remains false unless a future execution bridge separately authorizes it.
- no trade is placed.
validators:
- permission envelope pytest.
- permission JSON parse.
- blocked action readback.
- git diff --check.
blocked actions:
- broker action.
- live trading.
- real money approval.
- compounding approval.
owner approval boundary: Anthony approval required before any separate demo execution packet.
next stage: FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER
stop point: Stop after eligibility report. Do not execute demo trade.

### FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER
stage id: FX-BUCKET-05-BROKER-READ-ONLY-RECONCILER
title: Broker Read-Only State Reconciler V1
purpose: Read, listen, hear, and interpret broker-side account state without mutation.
entry criteria:
- no credentials are persisted in repo.
- account id may be present only at runtime and never persisted in repo.
- read-only state contract is defined.
exit criteria:
- balance present.
- margin available.
- open trades listed.
- open positions listed.
- pending orders listed.
- last transaction id represented without repo persistence.
- transaction stream snapshot represented.
- instrument availability, spread, market hours, margin closeout risk, unknown exposure, and stale state are evaluated.
validators:
- read-only snapshot sanitizer tests.
- no credential persistence check.
- no account identifier persistence check.
- git diff --check.
blocked actions:
- broker write.
- order submit.
- credential persistence.
- account id persistence.
- network submit.
owner approval boundary: Anthony approval and separate scoped packet required before credential or broker access.
next stage: FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER
stop point: Stop after read-only state reconciliation. Do not mutate broker state.

### FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER
stage id: FX-BUCKET-06-RISK-ENVELOPE-POSITION-SIZER
title: Risk Envelope and Position Sizer V1
purpose: Calculate allowed demo-only position size under max loss rules.
entry criteria:
- broker read-only state exists.
- max risk per trade is known.
- max daily loss is known.
- symbol and instrument precision are known.
exit criteria:
- max risk per trade enforced.
- max daily loss enforced.
- max open trades, pending orders, exposure, spread, market hours, stop loss, take profit, kill switch, duplicate order guard, minimum units, and maximum units are enforced.
validators:
- position-size deterministic tests.
- risk envelope rejection tests.
- safety boundary readback.
- git diff --check.
blocked actions:
- real money approval.
- broker action.
- live trading.
- order placement.
owner approval boundary: Anthony approval required for any future demo execution packet.
next stage: FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER
stop point: Stop after local risk preview. Do not place an order.

### FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER
stage id: FX-BUCKET-07-DEMO-ORDER-INTENT-PLANNER
title: Demo Order Intent Planner V1
purpose: Create a local-only order intent preview.
entry criteria:
- risk envelope passed.
- broker read-only state is fresh.
- selected candidate remains review-ready.
exit criteria:
- symbol, direction, units, stop loss, take profit, risk amount, expected max loss, expected reward, spread gate, slippage assumption, and rejection reasons are output.
validators:
- order intent JSON parse.
- deterministic idempotency key test.
- no broker call safety readback.
- git diff --check.
blocked actions:
- broker call.
- order submit.
- live trading.
- credential access.
owner approval boundary: Anthony approval required before any separate execution bridge.
next stage: FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN
stop point: Stop after intent preview. Do not call broker.

### FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN
stage id: FX-BUCKET-08-EXECUTION-BRIDGE-DRY-RUN
title: Controlled Demo Execution Bridge Dry Run V1
purpose: Prepare future demo execution bridge without enabling broker action.
entry criteria:
- order intent is reviewed.
- demo permission envelope exists.
- future bridge is scoped as separate packet.
exit criteria:
- dry-run bridge requirements are defined.
- broker_action_allowed remains false.
- owner approval requirement is explicit.
validators:
- dry-run bridge tests.
- no broker mutation static scan.
- no credential access scan.
- git diff --check.
blocked actions:
- broker action.
- order submit.
- scheduler.
- daemon.
- live trading.
owner approval boundary: Anthony approval required for separate future controlled demo execution bridge.
next stage: FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH
stop point: Stop after dry-run bridge plan. Do not execute.

### FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH
stage id: FX-BUCKET-09-TRADE-MONITOR-KILL-SWITCH
title: Trade Monitor and Kill Switch V1
purpose: Monitor open demo trade state and stop conditions.
entry criteria:
- future execution bridge exists as a separate approved lane.
- stop conditions are enumerated.
- no daemon is started in this bucket.
exit criteria:
- max loss breach, daily loss breach, spread blowout, stale broker state, duplicate order evidence, unexpected open exposure, rejected order loop, missing stop loss, missing take profit, and human stop flag are represented.
validators:
- monitor state tests.
- kill switch trigger tests.
- non-daemon safety readback.
- git diff --check.
blocked actions:
- daemon start.
- scheduler start.
- live trading.
- broker mutation.
owner approval boundary: Anthony approval required before any runtime monitor is started.
next stage: FX-BUCKET-10-POST-TRADE-RECONCILIATION
stop point: Stop after monitor contract. Do not start background work.

### FX-BUCKET-10-POST-TRADE-RECONCILIATION
stage id: FX-BUCKET-10-POST-TRADE-RECONCILIATION
title: Post-Trade Reconciliation and Loss Response V1
purpose: Reconcile closed demo trade with broker transaction data, candidate evidence, and loss/profit validation loop.
entry criteria:
- closed demo trade evidence exists.
- sanitized broker transaction data exists.
- proof ledger and selector are available.
exit criteria:
- reconciliation feeds profit validation.
- reconciliation feeds loss to next profit candidate gate.
- reconciliation feeds evidence intake.
- reconciliation feeds selector.
validators:
- reconciliation tests.
- loss/profit loop handoff tests.
- no raw broker payload persistence check.
- git diff --check.
blocked actions:
- profit claim without reconciliation.
- real money approval.
- broker action.
owner approval boundary: Anthony approval required for any next trade request.
next stage: FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE
stop point: Stop after reconciliation evidence. Do not approve next trade.

### FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE
stage id: FX-BUCKET-11-AUDIT-REPLAY-EVIDENCE
title: Audit Replay and Evidence Ledger V1
purpose: Preserve sanitized, local-only evidence replay so AIOS can prove what happened before next decision.
entry criteria:
- reconciliation evidence exists.
- sensitive fields are excluded.
- local-only ledger scope is defined.
exit criteria:
- sanitized replay exists.
- decision trace exists.
- validator evidence exists.
- credentials and account identifiers are absent.
validators:
- replay ledger tests.
- sensitive-field scan.
- JSON parse.
- git diff --check.
blocked actions:
- credential storage.
- account identifier storage.
- raw broker payload storage.
owner approval boundary: Anthony approval required for any evidence promotion that changes execution posture.
next stage: FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY
stop point: Stop after sanitized evidence ledger. Do not store secrets.

### FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY
stage id: FX-BUCKET-12-OPERATOR-DASHBOARD-VISIBILITY
title: Operator Visibility and Dashboard Evidence V1
purpose: Expose status, not authority.
entry criteria:
- sanitized evidence exists.
- dashboard projection is display-only.
- authority fields are separated from evidence fields.
exit criteria:
- dashboard cannot approve trades.
- dashboard cannot approve real money.
- dashboard cannot approve compounding.
- dashboard cannot approve commits, pushes, PRs, or merges.
validators:
- display-only projection tests.
- mutation_allowed false check.
- execution_allowed false check.
- git diff --check.
blocked actions:
- dashboard trade approval.
- dashboard commit approval.
- dashboard PR approval.
- dashboard merge approval.
owner approval boundary: Dashboard displays evidence only; Anthony remains approval authority.
next stage: FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF
stop point: Stop after display contract. Do not add execution controls.

### FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF
stage id: FX-BUCKET-13-NIGHT-SUPERVISOR-RELAY-HANDOFF
title: Night Supervisor and Relay Evidence Handoff V1
purpose: Route evidence into summaries while preserving human approval.
entry criteria:
- sanitized evidence projection exists.
- Relay and Night Supervisor are evidence-only.
- protected actions remain blocked.
exit criteria:
- Night Supervisor cannot approve protected actions.
- Relay cannot approve protected actions.
- summaries preserve approval_required.
validators:
- evidence handoff tests.
- approval boundary readback.
- no mutation scan.
- git diff --check.
blocked actions:
- Night Supervisor trade approval.
- Relay commit approval.
- protected action self-approval.
owner approval boundary: Anthony remains final authority for protected actions.
next stage: FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS
stop point: Stop after evidence handoff. Do not approve or execute.

### FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS
stage id: FX-BUCKET-14-GOVERNED-DEMO-AUTONOMY-READINESS
title: Governed Demo Autonomy Readiness Gate V1
purpose: Decide whether AIOS has a complete supervised demo autonomy loop.
entry criteria:
- all prior demo gates pass.
- owner approval requirement remains explicit.
- execution remains a separate lane.
exit criteria:
- governed demo autonomy review path is defined or blocked.
- next_demo_trade_allowed remains false unless future approval packet separately proves permission.
validators:
- readiness gate tests.
- proof summary review.
- protected action lock readback.
- git diff --check.
blocked actions:
- automatic execution.
- broker action.
- live trading.
- real money approval.
owner approval boundary: Anthony approval required for any actual demo execution.
next stage: FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW
stop point: Stop after readiness review. Do not execute.

### FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW
stage id: FX-BUCKET-15-SINGLE-LIVE-MICRO-TRADE-EXCEPTION-REVIEW
title: Single Live Micro-Trade Exception Review Gate V1
purpose: Future review only through existing governed live micro-trade exception doctrine.
entry criteria:
- governed demo autonomy evidence exists.
- explicit human approval is available in a separate future packet.
- runtime-only credentials, one-order-only, micro-size, stop loss, take profit, max loss, daily stop, kill switch, sanitized evidence, and no persistence requirements are all satisfied.
exit criteria:
- live trading remains disabled in this bucket.
- future live exception is review-only here.
validators:
- live exception readiness review.
- no credential persistence scan.
- no broker call scan.
- git diff --check.
blocked actions:
- live trade.
- credential persistence.
- account id persistence.
- broker call.
- network call.
owner approval boundary: Anthony approval and existing live exception doctrine required.
next stage: FX-BUCKET-16-REAL-MONEY-LOCK
stop point: Stop after future exception review requirements. Do not enable live trading.

### FX-BUCKET-16-REAL-MONEY-LOCK
stage id: FX-BUCKET-16-REAL-MONEY-LOCK
title: Real Money Lock V1
purpose: Keep real-money trading blocked until evidence and owner approval exist.
entry criteria:
- non-synthetic proof exists.
- real-money policy review exists.
- explicit owner approval exists.
exit criteria:
- real_money_allowed remains false in this bucket.
- missing proof is explicit.
validators:
- real-money lock tests.
- proof category review.
- approval boundary readback.
- git diff --check.
blocked actions:
- real money trade.
- funding approval.
- live trading.
- broker action.
owner approval boundary: Anthony approval required in a separate future lane.
next stage: FX-BUCKET-17-COMPOUNDING-LOCK
stop point: Stop after lock report. Do not approve real money.

### FX-BUCKET-17-COMPOUNDING-LOCK
stage id: FX-BUCKET-17-COMPOUNDING-LOCK
title: Compounding Lock V1
purpose: Keep compounding blocked until real-money growth proof, drawdown control, and owner approval exist.
entry criteria:
- real-money growth proof exists.
- drawdown control evidence exists.
- Anthony compounding approval exists in a separate future lane.
exit criteria:
- compounding_allowed remains false in this bucket.
- compounding blockers are explicit.
validators:
- compounding lock tests.
- growth proof review.
- drawdown proof review.
- git diff --check.
blocked actions:
- compounding approval.
- automatic size increase.
- money movement.
owner approval boundary: Anthony approval required in a separate future lane.
next stage: FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK
stop point: Stop after compounding lock report. Do not compound.

### FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK
stage id: FX-BUCKET-18-BROKER-TO-BANK-MOVEMENT-LOCK
title: Broker To Bank Movement Lock V1
purpose: Keep deposits, withdrawals, bank movement, account movement, and funding automation out of Forex trading engine.
entry criteria:
- bank movement remains out of Forex engine.
- any future bank movement is assigned to a separate lane.
- owner approval remains required.
exit criteria:
- bank_movement_allowed remains false.
- funding automation remains absent.
validators:
- bank movement lock tests.
- forbidden path scan.
- no account movement code scan.
- git diff --check.
blocked actions:
- deposit.
- withdrawal.
- bank linkage.
- account movement.
- funding automation.
owner approval boundary: Anthony approval and separate lane required for any future money movement discussion.
next stage: FX-BUCKET-19-MASTER-CONTINUATION-ROUTER
stop point: Stop after bank movement lock report. Do not move money.

### FX-BUCKET-19-MASTER-CONTINUATION-ROUTER
stage id: FX-BUCKET-19-MASTER-CONTINUATION-ROUTER
title: Master Continuation Router V1
purpose: Determine the single next safe Codex packet or protected action after current status.
entry criteria:
- current bucket status is evaluated.
- blockers are listed.
- permissions are listed.
exit criteria:
- one next safe action is output.
- no executable child packet is generated unless all required child fields are known in a separate packet.
validators:
- deterministic JSON output.
- operator text output.
- next packet intent output.
- git diff --check.
blocked actions:
- multiple next actions.
- self approval.
- protected action execution.
owner approval boundary: Anthony remains the approval authority.
next stage: NONE
stop point: Stop after one next safe action.

## Proof Categories
- candidate_evidence_present
- selector_present
- sample_size_sufficient
- expectancy_positive
- profit_factor_sufficient
- max_drawdown_within_limit
- consecutive_losses_within_limit
- walk_forward_passed
- out_of_sample_passed
- market_regime_coverage
- spread_sensitivity_passed
- slippage_sensitivity_passed
- latency_sensitivity_passed
- news_filter_validated
- demo_execution_reconciled
- broker_state_reconciled
- risk_controls_reconciled
- post_trade_reconciliation_passed
- loss_response_validated
- strategy_decay_monitor_present
- real_money_evidence_present
- compounding_evidence_present
- bank_movement_policy_present
- owner_approval_present

## Current Permission Defaults
candidate_review_allowed: false by default.
next_demo_trade_allowed: false.
broker_action_allowed: false.
real_money_allowed: false.
compounding_allowed: false.
bank_movement_allowed: false.
live_trading_allowed: false.
scheduler_allowed: false.
daemon_allowed: false.
credential_access_allowed: false.
repo_commit_allowed: false.
repo_push_allowed: false.
pr_creation_allowed: false.
owner_approval_required: true.

## Protected Action Locks
- no commit without Anthony approval.
- no push without Anthony approval.
- no PR without Anthony approval.
- no merge without Anthony approval.
- no broker action without Anthony approval.
- no credential access without Anthony approval and separate scoped packet.
- no demo trade without Anthony approval and separate scoped packet.
- no live trade without existing governed live micro-trade exception path and Anthony approval.
- no bank movement in Forex engine.
- no compounding approval in this bucket.

## Next Safe Action Logic
- If Review-Ready Candidate Selector V1 files are untracked, next safe action is protected commit / push / PR / merge workflow for selector.
- If selector is missing, next safe action is recover or build selector.
- If selector is landed, next safe action is Profit Proof Ledger V1.
- If proof ledger is landed, next safe action is Broker Read-Only Reconciler V1.
- If broker reconciler is landed, next safe action is Risk Envelope and Position Sizer V1.
- If risk envelope is landed, next safe action is Demo Permission Envelope V1.
- If demo permission is landed, next safe action is Demo Order Intent Planner V1.
- Broker execution remains separate future protected action.
- Real money, compounding, and bank movement remain locked.

## Operator Answer
AIOS now has a master bucket path for Forex profit autonomy. It does not approve a trade, broker action, real money, compounding, or bank movement. It defines the exact sequence required to keep moving without losing context or bypassing proof.
