# Open PR Classification

| number | title | state | mergeable | category | required_by_packet | reason |
|---|---|---|---|---|---|---|
| 554 | chore(reports): refresh autonomy spine evidence | OPEN | MERGEABLE | report_only_refresh | True | Evidence refresh packet aligns with final closeout evidence maintenance. |
| 550 | feat(runtime): enrich P2 queue contract | OPEN | CONFLICTING | should_not_merge_without_rebase | True | Dirty/conflicting state (mergeable=CONFLICTING) with overlapping scope; requires conflict resolution before merge consideration. |
| 533 | feat(autonomy): add self-build evidence ledger | OPEN | MERGEABLE | report_only_refresh | True | Autonomy evidence ledger useful but not required to resolve current approval mismatch blocker. |
| 528 | feat(autonomy): add canonical decision packet drafter | OPEN | MERGEABLE | report_only_refresh | True | Decision packet drafting is adjacent utility, not direct approval/queue-chain blocker for this closeout. |
| 521 | feat(autonomy): loop-closure Lane A — evidence ledger + drafter, promotion review, approval card, APPLY inventory, path-guard | OPEN | MERGEABLE | stale_conflict_risk | True | Large legacy lane packet with proposal overlap and likely superseded by later focused packets. |
| 511 | Autonomy completion Big-Pack: CONNECT/TRUST/ACT/ARM/PROVE (DRY_RUN-first) | OPEN | MERGEABLE | stale_conflict_risk | True | High-level big-pack planning packet; now partially obsolete as pieces were split into merged focus packets. |
| 504 | jsonl rotation + retention (DRY_RUN-first, preserves proof history) | OPEN | MERGEABLE | report_only_refresh | True | Retention proof useful for longer-run stability but not yet connected to queue-approval mismatch. |
| 502 | SOS Telegram arming v2 (DRY_RUN-first, supersedes stale #468) | OPEN | MERGEABLE | relevant_to_final_autonomy_closeout_now | True | Directly targets SOS wake path, one of the remaining end-state objectives. |
| 469 | Packet B+C: restart supervisor + git timeouts (#456 completion, DRY_RUN-first) | OPEN | MERGEABLE | report_only_refresh | True | Restart/timeouts packet is relevant for 24h stability, not immediate queue-approval mismatch. |
| 468 | Packet 2: SOS last-mile arming (DRY_RUN-first, serialized) | OPEN | MERGEABLE | stale_conflict_risk | True | Explicitly superseded by #502 by PR author notes; stale candidate. |
| 466 | Packet 3: dispatch closure + atomic worker-state + CI tests (DRY_RUN-first, serialized) | OPEN | MERGEABLE | report_only_refresh | True | Dispatch closure required for full runtime lane; not direct queue-specific approval blocker. |
| 462 | ci(governance): add execution bridge gates | OPEN | MERGEABLE | report_only_refresh | True | Execution bridge gates strengthen proof safety but are not currently required to proceed with approval target mismatch fix. |
| 451 | feat(governance): close weekend readiness control gaps v1 | OPEN | CONFLICTING | should_not_merge_without_rebase | True | CONFLICTING state and wide scope indicate merge risk without cleanup/rebase. |
| 449 | fix(governance): add Tier 1 restart safety gate | OPEN | CONFLICTING | should_not_merge_without_rebase | True | CONFLICTING state overlaps restart gate lineage; requires controlled rebasing/review. |
| 445 | build(deps): bump actions/setup-python from 5 to 6 | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 444 | build(deps): bump actions/checkout from 4 to 6 | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 437 | feat: add operator relief closed loop | OPEN | CONFLICTING | stale_conflict_risk | True | Large operator-relief lane likely stale against the current approved workflow model. |
| 436 | feat: add forex engine large dataset backtest adapter | OPEN | MERGEABLE | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 359 | build(deps): bump react and @types/react in /apps/dashboard | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 358 | build(deps-dev): bump eslint from 9.39.4 to 10.4.1 in /apps/dashboard | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 357 | build(deps): bump react-dom from 19.2.6 to 19.2.7 in /apps/dashboard | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 301 | Night Supervisor effector layer on Codex V2 spine | OPEN | MERGEABLE | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 300 | Add Layer 2 Night Supervisor memory and evidence systems | OPEN | CONFLICTING | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 295 | ci(dashboard): add static web apps workflow | OPEN | MERGEABLE | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 294 | chore(dashboard): add Azure request logging | OPEN | MERGEABLE | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 274 | Normalize JSON helper output for preview chain | OPEN | CONFLICTING | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 267 | automation: worker control layer -- morning brief, Claude hooks, validator chain runner (PKT-WEST-APPLY-005) | OPEN | MERGEABLE | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 251 | build(deps-dev): bump @eslint/js from 9.39.4 to 10.0.1 in /apps/dashboard | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 249 | build(deps-dev): bump eslint-plugin-react-hooks from 7.0.1 to 7.1.1 in /apps/dashboard | OPEN | UNKNOWN | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 243 | Add PR creation state to lane runner | OPEN | CONFLICTING | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
| 236 | Fix task generator work packet repo identity | OPEN | CONFLICTING | unrelated_trading_or_old_lane | False | Not in minimum required closeout targets for this packet. |
