# Paper Bot Build Plan

## Build Sequence

1. Confirm paper-only contract fields.
2. Route mock signal intake into the shared contract.
3. Record latency using paper-only timestamps.
4. Add regime tag evidence.
5. Run risk gate checks.
6. Create simulated paper trade result only after risk review.
7. Record win/loss result as paper-only data.
8. Update scorecard and sample-size warnings.
9. Log gaps to the global gap log.
10. Produce `CODEX_SUMMARY.md` and `NEXT_ACTION.md`.

## Starter Rule

Major Agents build the main system. Minor Agents only fix gaps. Validators check paper-only safety before any result is trusted.