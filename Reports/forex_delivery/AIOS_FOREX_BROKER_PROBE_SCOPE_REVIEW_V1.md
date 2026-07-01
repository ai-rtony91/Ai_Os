# AIOS Forex Broker Probe Scope Review V1

## Purpose
This review defines the smallest allowed broker-probe scope that may be approved later by the owner.
It is value-free, read-only, and intentionally excludes live execution.

## MAY do later, only if the owner approves
- Check reachability of the OANDA practice or demo endpoint.
- Read account summary only.
- Use a runtime token from environment variables at execution time only.
- Emit local evidence that a read-only probe was attempted or completed.

## MAY NOT do
- Place orders.
- Touch live endpoints.
- Store credentials in the repo.
- Persist account identifiers in the repo.
- Read `.env` files in this packet.
- Write broker tokens or secrets to disk.
- Move money.
- Create live execution authority.

## Read-only verification
I verified by code inspection that `automation/forex_engine/forex_demo_proof_ledger_v1.py` builds a dated `new_entry` with `_utc_date()` and only appends it when `apply=True`.
That is the real dated-entry seam for the supervised demo proof record. The repository's demo proof ledger currently contains 3 historical mock/stub lines in `telemetry/forex/demo_proof_ledger.jsonl`; they are preserved, marked superseded-by-real-run here, and are not counted as real-run evidence.

## Exact owner command for the supervised demo proof seam
```powershell
python automation/forex_engine/forex_demo_proof_ledger_v1.py --repo-root C:\Dev\Ai.Os --record-demo-day --apply --pretty
```

## Owner decision block
- Decision: [ ] APPROVE  [ ] HOLD  [ ] ADJUST
- Owner signature: ____________________
- Date: ____________________
- Notes: ____________________

## Non-goals
- No broker API call in this document.
- No order path in this document.
- No credential storage in this document.
- No account identifier persistence in this document.

## Next safe action
If the owner approves later, run the exact command above and keep the result local-only until the next governance step.
