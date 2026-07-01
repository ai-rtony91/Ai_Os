# AIOS Forex Repeatability Ledger Plan V1

## 1. Status
`PARTIAL`

## 2. Ledger purpose
- Keep a deterministic, append-only history of proof-lane runs.
- Make each run auditable without rebuilding state from ad hoc reports.
- Tie paper/demo receipts, drawdown evidence, and post-trade review into one repeatable record.
- Reduce cherry-picking by forcing the run context to be explicit.

## 3. Required fields
The ledger should carry at least the following data groups:

| Group | Required fields |
|---|---|
| Run identity | `run_id`, `campaign_id`, `branch`, `base_head`, `commit_hash`, `started_at_utc`, `finished_at_utc` |
| Strategy identity | `strategy_id`, `strategy_name`, `strategy_version`, `strategy_hash` |
| Config identity | `config_hash`, `config_source`, `config_version` |
| Dataset identity | `dataset_id`, `source_type`, `source_revision`, `symbol`, `timeframe`, `sample_window` |
| Receipt linkage | `receipt_id_list`, `receipt_hash_list`, `receipt_mode`, `account_alias_non_secret` |
| PnL evidence | `realized_pnl_usd`, `gross_profit_usd`, `gross_loss_usd`, `fees_usd` |
| Drawdown evidence | `starting_balance_usd`, `ending_balance_usd`, `max_drawdown_usd`, `max_drawdown_pct`, `drawdown_series` |
| Review evidence | `post_trade_review_status`, `reviewer`, `review_notes`, `owner_approval_id` |
| Validation evidence | `validator_status`, `schema_version`, `redaction_status` |

## 4. Run identity
- Every record must identify the exact run that produced it.
- The run identity must be stable enough to cross-link reports, receipts, and test output.
- The ledger should record the branch and commit hash so a future reader can find the source state.

## 5. Strategy version
- Strategy identity must include a human-readable version plus a stable hash.
- If the strategy changes, the ledger should treat the new version as a distinct run family.
- Strategy identity must not be inferred from filenames alone.

## 6. Config hash concept
- Hash the normalized config payload after redaction and ordering.
- Include the config source and config version so the hash can be reproduced.
- A config hash should detect hidden changes in risk thresholds, symbols, or sampling policy.

## 7. Dataset/source identity
- Record where the evidence came from and which slice of the dataset was used.
- Include source revision or source snapshot identifiers where available.
- Capture the symbol, timeframe, and sample window so the run can be replayed or compared.

## 8. Demo/live receipt linkage
- Link each ledger line to the receipt IDs and receipt hashes that support it.
- Use the same linkage for demo receipts and any future live receipts, but keep raw identifiers redacted.
- Do not store broker secrets or raw payloads in the ledger.

## 9. Realized PnL evidence
- Record realized PnL, gross profit, gross loss, and fee totals as numeric evidence.
- Keep the figure tied to the supporting receipt set and sample window.
- Distinguish realized PnL evidence from backtest estimates and from any profit claim.

## 10. Drawdown series
- Record the equity or balance path that produced the max drawdown value.
- Preserve the series in a form that can be reviewed without recomputing hidden state.
- Include the worst point, the peak that preceded it, and the timestamp range.

## 11. Post-trade review
- Record whether a post-trade review happened and who performed it.
- Capture review notes that explain exceptions, blockers, or follow-up work.
- Keep review output separate from execution authority.

## 12. Pass/fail criteria
- Pass when every required field is present, redacted, linked, and reproducible.
- Fail when receipt linkage is missing, config identity is ambiguous, or the drawdown series cannot be explained.
- Fail when raw secrets, raw broker payloads, or unapproved private data appear.
- Fail when the run cannot be reproduced from the stored evidence set.

## 13. Anti-cherry-pick controls
- Pre-register the sample window before evaluating the run.
- Include the full run slice, not only the best subset.
- Preserve negative runs, blocked runs, and drawdown-relevant runs.
- Hash the selection manifest so post hoc edits are visible.

## 14. Minimum sample policy placeholder
- No canonical minimum sample policy is defined in this campaign.
- Do not invent a threshold for live or demo claims.
- Treat the minimum sample policy as an owner-approved follow-up decision before any proof promotion.

## 15. Next safe packet
- `AIOS_FOREX_PROOF_LANE_RECEIPT_SCHEMA_DRY_RUN_VALIDATOR_V1`
