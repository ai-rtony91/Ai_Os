# AIOS Forex Technical Debt Audit V1 Report

## Packet Identity

- Mission ID: MISSION-AIOS-FOREX
- Mission Name: AIOS Forex Technical Debt Audit
- Program ID: PRG-FOREX-001
- Program Name: AIOS Forex Supervised Operational Validation
- Epic ID: EPC-FOREX-TECHNICAL-DEBT-V1
- Epic Name: Forex Technical Debt Audit
- Bucket ID: BKT-FOREX-CLEANUP-V1
- Bucket Name: Cleanup Planning
- Packet ID: AIOS-FOREX-TECHNICAL-DEBT-AUDIT-V1
- Packet Name: Forex Technical Debt Audit V1
- Mode: LOCAL_APPLY
- Zone: Report Only
- Lane: Technical Debt Audit
- Worker identity: Codex Technical Debt Auditor
- Worktree: C:\Dev\Ai.Os
- Observed branch: main
- Report path: Reports/forex_delivery/AIOS_FOREX_TECHNICAL_DEBT_AUDIT_V1_REPORT.md
- Report date: 2026-06-27

## Boundary

This is a report-only technical debt audit.

No code, tests, runners, existing reports, docs, branches, worktrees, stashes, commits, pushes, pull requests, merges, broker/API paths, credentials, account data, schedulers, daemons, webhooks, production systems, orders, trades, or money movement were modified or invoked.

This report does not approve cleanup. All cleanup recommendations are for after publication and require a separate Human Owner-approved packet with exact paths, dependency evidence, validators, and stop point.

## Authority Read

Required authority and context read:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `RISK_POLICY.md`
- `Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`

Additional context read because AI_OS bootstrap and front-door rules require current repo memory, identity, source-of-truth, and active system context:

- `docs/governance/AI_OS_REPO_MEMORY.md`
- `docs/governance/aios-identity-and-lane-governance.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`

Cleanup-oriented Forex reports also inspected to avoid duplicate recommendations:

- `Reports/forex_delivery/AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CLEANUP_CLASSIFICATION_DRYRUN_V2.md`
- `Reports/forex_delivery/AIOS_FOREX_REMAINING_WORK_INVENTORY_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_MASTER_CLOSURE_LONG_RUN_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md`

Authority summary:

- `AGENTS.md` remains highest local repo authority for Codex behavior, packet governance, protected actions, and report format.
- `RISK_POLICY.md` remains root safety authority for trading, broker, OANDA, credentials, secrets, live execution, production, and fail-closed behavior.
- `README.md` defines active repo identity: `C:\Dev\Ai.Os`, GitHub repo `ai-rtony91/Ai_Os`, branch `main`.
- Generated reports under `Reports/forex_delivery` are evidence or planning artifacts unless an active authority file explicitly promotes them.
- Cleanup must not create duplicate authority, weaken safety boundaries, or delete evidence by filename alone.

## Preflight State

Observed preflight:

```text
pwd
C:\Dev\Ai.Os

git branch --show-current
main

git remote -v
origin https://github.com/ai-rtony91/Ai_Os.git (fetch)
origin https://github.com/ai-rtony91/Ai_Os.git (push)
```

Observed status before this report:

```text
## main...origin/main [ahead 1]
```

The worktree already contained modified same-mission Forex files and broad untracked Forex reports, modules, runners, and tests. This packet allowed current branch only and report-only output, so no branch switch, stash, reset, clean, stage, commit, push, PR, or merge was performed.

## Audit Method

Read-only inventory and evidence checks were run over:

- `automation/forex_engine`
- `scripts/forex_delivery`
- `tests/forex_engine`
- `tests/forex_delivery`
- `Reports/forex_delivery`
- `src/forex_delivery`
- `apps/trading_lab/trading_lab`
- `aios/modules/trader`
- `automation/trading_lab`
- `tests/trader`
- selected Forex docs under `docs/forex_delivery`, `docs/trading_lab`, `docs/orchestration`, and `docs/AI_OS/trading*`

Checks included:

- file counts and approximate sizes
- exact content duplicate hashes
- generated cache inventory
- report family and suffix/version clustering
- runner to module pairing
- test to module pairing
- Python AST import scan for obvious unused modules
- common helper/function name counts
- stale, superseded, obsolete, deprecated, draft, and manual-finalization keyword searches
- current report evidence comparison against older cleanup and closure reports

No source code was executed except read-only inventory/parsing commands and required report validators.

## Current Inventory

Source, script, test, and report inventory excluding Python cache files:

| Area | Files | Approx size |
| --- | ---: | ---: |
| `automation/forex_engine` | 427 | 6563.2 KB |
| `scripts/forex_delivery` | 146 | 544.6 KB |
| `tests/forex_engine` | 382 | 3044.3 KB |
| `tests/forex_delivery` | 9 | 138.4 KB |
| `Reports/forex_delivery` | 561 | 2966.0 KB |

Python inventory:

| Area | Count |
| --- | ---: |
| Engine Python files excluding `run_*` wrappers | 376 |
| Engine `run_*` wrapper/demo Python files | 40 |
| `scripts/forex_delivery` Python runners | 146 |
| Forex test Python files | 391 |
| Forex delivery reports and evidence files | 561 |

Adjacent Forex and Trading Lab topology:

| Area | Files | Approx size |
| --- | ---: | ---: |
| `src/forex_delivery` | 10 | 299.2 KB |
| `apps/trading_lab/trading_lab` | 89 | 217.0 KB |
| `aios/modules/trader` | 19 | 37.4 KB |
| `automation/trading_lab` | 49 | 211.0 KB |
| `tests/trader` | 2 | 4.5 KB |

Generated local cache and runtime artifacts:

| Area | Finding |
| --- | --- |
| Python cache | 1350 `.pyc` files under Forex source/test trees, 24.83 MB total, ignored by `.gitignore`, not tracked by `git ls-files` |
| Runtime generated files | `automation/forex_engine/runtime/.gitignore` ignores all runtime outputs except itself |
| Exact duplicate runtime files | `historical_data_readiness_synthetic.csv` appears identically in `runtime/historical_data_demo` and `runtime/large_dataset_backtest_demo` |
| Runtime journal | `automation/forex_engine/runtime/journal/forex_paper_journal_20260606.jsonl` is ignored generated evidence |

Repo-level Python packaging note:

- No root `pyproject.toml`, `setup.cfg`, `setup.py`, `tox.ini`, or `pytest.ini` was found.
- Only `apps/trading_lab/requirements.txt` appeared in the packaging-related file search.
- This makes package ownership and import routing more dependent on ad hoc path insertion and test runner behavior.

## Executive Findings

1. The biggest technical debt is report sprawl and stale-reader risk, not proven dead code.
2. No high-confidence unused engine module was proven by the import/test/runner scan.
3. There is heavy responsibility duplication across demo, OANDA, broker, live, evidence, proof, profit, owner, and readiness modules.
4. The runner layer has substantial repeated boilerplate and could be simplified after publication.
5. The test layer is broad and mostly paired with source modules, but integration and runner tests create many files whose purpose is hard to infer from names alone.
6. The Forex implementation is split across at least five package or tool roots: `automation/forex_engine`, `src/forex_delivery`, `apps/trading_lab/trading_lab`, `aios/modules/trader`, and `automation/trading_lab`.
7. Generated caches and ignored runtime outputs are a local size and noise issue, but not a tracked repo-size issue.
8. Older reports now contain stale claims because current local work advanced beyond prior missing-module reports.
9. Cleanup should be publication-first, index-first, dependency-checked, and deletion-last.

## Duplicated Module Responsibility Clusters

Filename-term counts show where responsibility overlap is concentrated:

| Term | Engine modules | Scripts | Tests | Reports |
| --- | ---: | ---: | ---: | ---: |
| demo | 135 | 70 | 136 | 190 |
| oanda | 105 | 75 | 105 | 134 |
| broker | 44 | 9 | 44 | 60 |
| live | 44 | 24 | 49 | 91 |
| evidence | 42 | 24 | 45 | 74 |
| paper | 37 | 1 | 38 | 13 |
| owner | 33 | 26 | 33 | 42 |
| profit | 28 | 19 | 28 | 51 |
| readiness | 28 | 14 | 32 | 39 |
| proof | 22 | 15 | 25 | 63 |
| runtime | 22 | 7 | 23 | 40 |
| risk | 12 | 1 | 12 | 5 |
| dashboard | 2 | 1 | 2 | 4 |

These are not exact duplicates. They are overlapping domain slices that need canonical ownership.

High-value module consolidation candidates:

| Cluster | Examples | Debt type | Cleanup recommendation |
| --- | --- | --- | --- |
| Demo validation | `demo_validation_orchestrator.py`, `demo_validation_supervisor.py`, `demo_validation_contract.py`, `demo_validation_result_aggregator.py`, `demo_validation_scorecard.py` | Multiple adjacent coordination/reporting layers | Keep until publication; then pick one orchestration owner and demote the others to helpers or historical adapters after tests prove coverage |
| Evidence bundle/intake | `evidence_aggregator.py`, `evidence_bundle_runner.py`, `evidence_ledger.py`, `evidence_cache_registry_v1.py`, `replay_evidence_intake_v1.py`, `walk_forward_evidence_intake_v1.py`, `profitability_evidence_intake_v1.py`, `observation_evidence_intake_v1.py`, `final_evidence_bundle_v1.py`, `final_closure_evidence_v1.py` | Many evidence entry points and summary layers | Create one evidence index and one canonical final-bundle adapter; avoid deleting stage adapters until dependency tests pass |
| Broker/OANDA proof | OANDA demo, OANDA live, read-only, vault, telemetry, owner-run, result, and transport modules | Broker-specific proof path sprawl | Split into demo-read-only, live-exception evidence, and historical owner-run groups under `RISK_POLICY.md` boundary |
| Live micro-trade | one-shot, arming, final gate, owner runbook, result capture, reconciliation, post-trade capture modules | High-risk naming overlap | Preserve fail-closed behavior; build one live-exception spine and archive older packet chains only after successor links exist |
| Paper/demo promotion | `paper_to_demo_promotion.py`, `paper_to_demo_promotion_workflow.py`, demo readiness, demo review, OANDA demo bridge modules | Stage transition overlap | Pick one current promotion map; keep paper and demo evidence separated |
| Profit/capital/compounding | profit proof, profitability evidence, capital flow, compounding, P/L bucket modules | Repeated money-state concepts | Create one capital/P&L/profit truth index with simulated, demo, and live scopes separated |
| Dashboard/readiness summaries | dashboard truth, readiness recalculation, owner go/no-go, final readiness, decision brief modules | Many operator-facing status surfaces | Keep one final owner decision chain; mark old status reports as historical or evidence-only |

## Duplicated Package Topology

Forex code is spread across these active or semi-active roots:

| Root | Role observed | Technical debt |
| --- | --- | --- |
| `automation/forex_engine` | Largest implementation and evidence engine surface | Main current implementation root, but mixes library modules, demo wrappers, evidence adapters, generated runtime folder, and historical stage modules |
| `scripts/forex_delivery` | CLI runners and validators | 146 mostly thin wrappers with repeated path/bootstrap/output logic |
| `src/forex_delivery` | Small live/read-only delivery package | Uses both `src.forex_delivery.*` and `forex_delivery.*` import styles in scripts/tests, which creates packaging ambiguity |
| `apps/trading_lab/trading_lab` | Paper-only Trading Lab app package | Likely long-term app package, but overlaps with `automation/forex_engine` and `aios/modules/trader` paper trading concepts |
| `aios/modules/trader` | Separate paper trader module | Active because tests import it; source-of-truth map already marks this overlap as `REVIEW_REQUIRED` |
| `automation/trading_lab` | PowerShell validation/control scripts | Active paper/trading lab workflow scripts, but separate from Python package roots |

Recommended owner decision after publication:

1. Keep `automation/forex_engine` as the current evidence/closure engine until the published state is preserved.
2. Treat `src/forex_delivery` as a compatibility/live-read-only delivery package pending dependency mapping.
3. Keep `apps/trading_lab/trading_lab` as the likely long-term app package only after a separate canonical package decision.
4. Keep `aios/modules/trader` active until tests and imports are migrated or explicitly retained.
5. Do not consolidate these roots in a cleanup packet that lacks import and test evidence.

## Duplicated Reports

`Reports/forex_delivery` contains 561 files. Prior classifier and governance reports already identify the report layer as the main complexity source.

High-value report duplication clusters:

| Cluster | Examples | Recommendation |
| --- | --- | --- |
| First demo connection proof attempts | `AIOS_FIRST_DEMO_CONNECTION_PROOF_*_REPORT.md` and matching `*_SANITIZED_EVIDENCE.md` files | Keep final/current proof and index attempts as history |
| Live micro-trade exception packet chain | `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_01_REPORT.md` through packet 09 dry-run reports | Collapse into one exception history/readiness index after publication |
| OANDA demo/live proof chains | OANDA demo execution truth, owner-run, read-only P/L, vault, telemetry, live microtrade proof reports | Split demo-read-only evidence from live-exception evidence |
| Capital flow version chain | `AIOS_CAPITAL_FLOW_*_V10.md`, `AIOS_CAPITAL_FLOW_*_V11.md` | Mark current successor and archive older version after dependency check |
| Manual finalization companions | `*_MANUAL_FINALIZATION_V1.md` paired with base or epic reports | Convert to final-result pointers after canonical result is named |
| Base/report duplicate pairs | `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md` and `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md`; similar strategy/profit/autonomy pairs | Keep one operator-facing report and classify the other as evidence or legacy |
| JSON/report state pairs | `readiness_state_recalculation_v1_report.json` plus report; proof and journey JSON plus report | Preserve machine-readable JSON as evidence, but point humans to one current report |
| Real evidence intake/revalidation | `REAL_EVIDENCE_INTAKE_V1`, `REVALIDATION_V1`, `REVALIDATION_V2`, long-run/continuation reports | Mark current latest and link older revalidations |
| Master closure/convergence reports | `MASTER_CLOSURE_LONG_RUN_V1`, `MASTER_COMPLETION_LONG_RUN_APPLY_V1`, `MASTER_CONVERGENCE_LONG_RUN_V2` | Treat `MASTER_CONVERGENCE_LONG_RUN_V2` as latest local convergence evidence until publication creates a newer canonical state |

Keyword scan signals in the Forex surface:

| Signal | Matching files |
| --- | ---: |
| `DRAFT` | 32 |
| `stale` | 159 |
| `superseded` | 16 |
| `obsolete` | 5 |
| `deprecated` | 1 |
| `manual finalization` | 3 exact text matches in reports |

Important interpretation:

- The keyword `stale` often appears in safety tests and blockers by design. It is not proof that the file itself is stale.
- The report layer contains true stale-reader risk because older reports describe missing modules that now exist locally.

## Stale Or Superseded Reports

The following reports are useful history but contain stale or superseded conclusions relative to current local evidence and `AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`:

| Report | Stale/superseded point | Recommendation |
| --- | --- | --- |
| `AIOS_FOREX_REMAINING_WORK_INVENTORY_V1_REPORT.md` | States several Sprint 2B-style modules were missing; current local inventory shows `risk_budget_engine_v1.py`, `broker_health_readonly_v1.py`, `profitability_evidence_v1.py`, `stop_pause_resume_engine_v1.py`, `supervised_demo_intent_card_v1.py`, `dashboard_truth_summary_v1.py`, and final closure bridge modules now present | Keep as historical planning; mark superseded by current convergence report after publication |
| `AIOS_FOREX_MASTER_CLOSURE_LONG_RUN_V1_REPORT.md` | Describes project closure path before current broad local convergence and full Forex test pass evidence in V2 | Keep as historical master planning; mark superseded by V2 |
| `AIOS_FOREX_CLEANUP_CLASSIFICATION_DRYRUN_V2.md` | Uses older counts and PR #1040-era readiness state; current local report and file counts have advanced substantially | Keep as older DRY_RUN classification evidence only |
| `AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md` | Filename-only classification over 509 reports; current report count is 561 | Use as classification seed, not current complete index |
| `AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md` | Counts and branch state are historical; findings remain directionally useful | Keep as consolidation roadmap evidence |

Reports that should remain high-priority current-state evidence until a newer publication packet says otherwise:

- `Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_CAPITAL_COMPOUNDING_SAFETY_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_SYSTEM_VALIDATION_CLOSURE_LANE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_OPERATIONAL_READINESS_CERTIFICATION_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md`
- current JSON/report evidence that feeds readiness and proof chains

## Duplicated Runners

Runner inventory:

- `scripts/forex_delivery`: 146 Python runner files.
- `automation/forex_engine`: 40 `run_*` wrapper/demo files.
- No exact same-name duplicate runner was found between the automation `run_*_demo.py` files and `scripts/forex_delivery/run_*.py` files.

Observed runner boilerplate pattern:

- insert repo root into `sys.path`
- import one or more engine functions
- create `argparse.ArgumentParser`
- accept `--json`, `--blocked`, `--incomplete`, `--sample-*`, or `--write-report`
- build deterministic sample input
- call one engine function
- print JSON or operator text
- return 0

This is maintainable for small counts, but 146 scripts makes it expensive to update output style, safety wording, path behavior, or JSON formatting.

Scripts without same-name `automation/forex_engine` module:

- `run_auto_exit_live_readiness.py`
- `run_live_micro_trade_arming_gate.py`
- `run_live_readiness_consolidated_blocker_burndown.py`
- `run_one_shot_live_micro_trade_execution_review.py`
- `run_paper_signal_execution_loop.py`
- `run_read_only_evidence_approval.py`
- `run_read_only_live_data_bridge.py`
- `run_trading_history_writeback_verification.py`

Interpretation:

- These are not dead by name alone. Most map to `src/forex_delivery` or cross-lane delivery validators.
- The debt is package split and import ambiguity, not confirmed unused runners.

Recommended runner cleanup after publication:

1. Create a read-only runner registry that maps runner names to module/function/report output.
2. Extract shared CLI output helpers only after tests prove runner behavior.
3. Retain compatibility wrappers temporarily.
4. Retire wrapper files only after the registry has test coverage and downstream references are checked.

## Duplicated Tests

Test inventory:

- 391 Forex test Python files across `tests/forex_engine` and `tests/forex_delivery`.
- Most engine modules have same-name test files.
- Same-name test gaps are limited to seven source modules.

Modules without same-name test files:

- `confidence`
- `demo_validation_scorecard`
- `journal`
- `models`
- `read_only_live_data_sanitizer`
- `regime`
- `signals`

Interpretation:

- These are not proven unused. Search evidence shows several are imported by active modules or tests.
- `confidence.py` is still imported by `backtest.py` and `test_confidence_v2.py`, even though `confidence_v2.py` exists.
- `models.py`, `regime.py`, and `signals.py` are foundational helpers.
- `demo_validation_scorecard.py`, `journal.py`, and `read_only_live_data_sanitizer.py` need targeted dependency review before any cleanup.

Tests without same-name engine modules include integration, runner, schema, and `src/forex_delivery` tests:

- `aios_forex_demo_readiness_state_schema_v1`
- `auto_exit_live_readiness`
- `demo_readiness_trust_spine_no_forbidden_runtime_v1`
- `forex_end_to_end_journey`
- `forex_evidence_cache_v1`
- `governed_readiness`
- `live_arming_evidence_gap`
- `live_micro_trade_arming_gate`
- `live_micro_trade_packet_fixture`
- `one_shot_live_micro_trade_execution_review`
- `operator_next_trade_review_runner_v1`
- `paper_signal_execution_loop`
- `read_only_evidence_approval`
- `read_only_live_data_bridge`
- `review_chain_stage_chain_continuity_v1`
- `run_forex_journey_status_cli`
- `run_forex_proof_bundle_to_candidate_bridge_cli`
- `run_forex_proof_gap_closure_plan_cli`
- `run_forex_replay_reconciliation_proof_bundle_cli`
- `trading_history_writeback_verification`
- `weekly_milestone_stage_chain_continuity`

Interpretation:

- This is not deletion evidence. It reflects integration and CLI coverage.
- Future cleanup should classify tests as unit, integration, runner, schema, safety, and historical-regression tests.

## Dead Code And Unused Helpers

No high-confidence dead engine module was proven.

Evidence:

- Python AST parse completed with zero parse errors over the inspected Python surface.
- Import/test/runner scan found zero modules that simultaneously lacked import references, same-name tests, and matching runner coverage.
- Several modules that lack same-name tests are still imported elsewhere.

Low-confidence cleanup review candidates:

| Candidate | Why review | Required proof before cleanup |
| --- | --- | --- |
| `demo_validation_scorecard.py` | No same-name test found | Confirm whether supervisor/orchestrator still depends on it |
| `journal.py` | No same-name test found | Confirm whether older paper/backtest paths still need it |
| `read_only_live_data_sanitizer.py` | No same-name test found | Confirm whether it is superseded by newer read-only/OANDA sanitizers |
| `confidence.py` | `confidence_v2.py` exists | Confirm v1 is still needed by `backtest.py` or migrate consumers first |
| `signals.py` | Older simple signal helper | Confirm it is not superseded by `signal_rules.py` and strategy modules |

Do not delete these files from this audit. They require a dependency-confirmation APPLY packet after publication.

## Repeated Helper Patterns

Common top-level helper names indicate repeated adapter/report boilerplate:

| Function name | Module count |
| --- | ---: |
| `result_to_jsonable_dict` | 34 |
| `result_to_operator_text` | 34 |
| `to_jsonable_dict` | 31 |
| `to_markdown` | 31 |
| `to_operator_text` | 31 |
| `build_sample_unsafe_input` | 18 |
| `protected_flags_false` | 15 |
| `markdown_safety_lines` | 14 |
| `build_sample_ready_input` | 12 |

This duplication is mostly in safety/evidence adapters and OANDA/live microtrade review modules.

Recommendation:

- Do not refactor before publication.
- After publication, create one shared Forex report/adapter helper only if it reduces repeated JSON/text/protected-flag code without weakening fail-closed safety checks.
- Keep module-local constants for safety-critical statuses unless tests prove shared abstraction preserves exact behavior.

## Obsolete Or Risky Interfaces

Interfaces that need classification before future cleanup:

| Interface area | Evidence | Risk |
| --- | --- | --- |
| `src/forex_delivery` package | Scripts/tests import both `src.forex_delivery.*` and `forex_delivery.*` | Package ambiguity and duplicate delivery namespace |
| `scripts/forex_delivery` wrappers | 146 script files with local `sys.path` insertion | Repeated bootstrap and inconsistent import style risk |
| `automation/forex_engine/runtime` | Ignored runtime folder contains generated duplicate CSV and journal output | Local stale evidence and disk noise |
| `apps/trading_lab/trading_lab` vs `aios/modules/trader` | Source-of-truth map marks package ownership as unresolved | Duplicate paper-trading concepts and migration risk |
| Live/OANDA owner-run modules | Many fail-closed live/demo/review modules | High safety risk if archived or renamed without successor index |
| Old report-named packet chains | Many reports contain packet-like names outside canonical packet anchors | Operator confusion and duplicate authority risk |

## Opportunities To Reduce Repository Or Workspace Size

Immediate cleanup is not approved. These are future recommendations only.

| Opportunity | Approx impact | Current safety | Future safe handling |
| --- | ---: | --- | --- |
| Remove local ignored `.pyc` files under Forex source/test trees | 24.83 MB local workspace reduction | Ignored, not tracked | Separate approved local cleanup packet; no `git clean`; verify paths first |
| Remove or regenerate ignored runtime duplicate CSV files | 74 KB duplicate pair plus runtime noise | Ignored by `automation/forex_engine/runtime/.gitignore` | Retention decision first; preserve if needed as evidence |
| Retire stale report chains from operator-facing current index | High operator complexity reduction | Reports are evidence; not safe to delete by name | Create report index and archive-candidate map first |
| Consolidate runner boilerplate | Medium maintenance reduction | Runners are covered by tests and may be referenced externally | Registry/shared helper with compatibility wrappers |
| Classify `docs/AI_OS/trading*` legacy/reference docs | Medium stale-reader reduction | Source-of-truth map already marks these as subordinate/reference | Keep reference-only unless promoted |
| Resolve package roots | High long-term maintenance reduction | Active tests/imports span multiple roots | Separate architecture/implementation packet with dependency map |

## Cleanup Priority After Publication

Recommended order:

1. Publish or preserve the current Forex report/source/test state through approved protected-action flow.
2. Create a current machine-readable report index for all `Reports/forex_delivery` files.
3. Mark report families as current, evidence-only, superseded-candidate, archive-candidate, draft, manual-finalization, live-exception, demo, broker/OANDA, profit/P&L, dashboard truth, or governance.
4. Build a dependency map for `automation/forex_engine`, `src/forex_delivery`, `scripts/forex_delivery`, `apps/trading_lab/trading_lab`, and `aios/modules/trader`.
5. Classify runner scripts as active wrappers, compatibility wrappers, generated candidates, or archive candidates.
6. Classify tests as unit, integration, runner, schema, safety, or historical regression.
7. Remove local ignored caches only with an exact path-scoped cleanup packet.
8. Archive or retire files only after successor links, dependency checks, tests, and Human Owner approval.

## Do Not Cleanup Yet

Do not delete, move, rename, archive, or rewrite:

- any live/OANDA/broker/credential/owner-run safety module
- any fail-closed live micro-trade gate
- any report that contains unique evidence or current blocker state
- any test that preserves broker/live/credential/no-order safety
- `apps/trading_lab/trading_lab/execution/live_broker_stub.py`
- `aios/modules/trader`
- `src/forex_delivery`
- generated reports that have not been indexed
- runtime/generated evidence without retention decision
- any root governance or risk authority file

## Final Recommendation

AIOS Forex technical debt is cleanup-ready for planning but not cleanup-ready for deletion.

The fastest safe improvement is not a broad delete pass. The fastest safe improvement is:

```text
publish current state
-> create canonical report index
-> classify source/test/runner package ownership
-> extract shared runner/report helpers only after tests
-> archive old reports only after successor links
-> remove ignored local caches with exact path approval
```

Status:

```text
TECHNICAL_DEBT_AUDIT_COMPLETE = true
CODE_MODIFIED = false
CLEANUP_APPROVED = false
DELETE_APPROVED = false
COMMIT_APPROVED = false
PUSH_APPROVED = false
LIVE_TRADING_ALLOWED = false
BROKER_API_ALLOWED = false
```

## Safe Next Action

Use a separate protected-action packet if Anthony wants to preserve/publish the current Forex report bundle. Do not run cleanup, deletion, archive movement, runner refactor, package consolidation, commit, push, PR, merge, broker/API, credential, scheduler, daemon, webhook, production, or trading actions from this audit.

STATUS: TECHNICAL DEBT AUDIT COMPLETE
