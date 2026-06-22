# AIOS Forex Evidence Cache + Known Path Registry V1

## Purpose
Create a deterministic, process-local latency registry and optional opt-in cache helper for known expensive forex evidence paths, without changing trade execution, broker behavior, or safety gates.

## Latency lane classification
- Paper-only dev/validation lane only.
- Runtime trading lane remains untouched.
- Hot files are centrally registered for Codex/agent navigation and deterministic cache planning.

## Known slow files
- `test_broker_paper_sandbox_readiness.py` (~190.69s)
- `test_paper_forward_evidence_v2.py` (~51.29s)
- `test_oos_expansion.py` (~44.35s)
- `test_low_vol_edge_redesign.py` (~24.97s)
- `test_opportunity_capture.py` (~21.04s)
- `test_oos_repair.py` (~15.96s)
- `test_month_end_readiness.py` (~10.78s)
- `test_forex_dashboard_contract.py` (~10.51s)

## Why prior test-only caching had weak ROI
- Previous test helper caching reduced a single hot path slightly but introduced brittle replay and fixture mutation coupling.
- Reusing cached payloads from within test modules without explicit, safe, key-based wrappers can make subsequent assertions mutate shared state.
- Repeated heavy builders still executed because each test file had custom local calls.

## New design
- Added `automation/forex_engine/evidence_cache_registry_v1.py` with:
  - deterministic known-path registry for required builders
  - required metadata for each path
  - opt-in wrapper `run_cached_evidence_builder_v1(...)`
  - defensive deep-copy cache returns
  - explicit bypass (`cache_enabled=False`)
  - deterministic cache keying by name + params
  - explicit `safe_to_cache=False` on sensitive paths
  - fast lookup helpers

## Files changed
- Added `automation/forex_engine/evidence_cache_registry_v1.py`
- Added `tests/forex_engine/test_evidence_cache_registry_v1.py`
- Added this report

## Safety exclusions
- No broker credentials.
- No network calls.
- No live order/trading execution paths.
- No risk thresholds changed.
- No safety assertions weakened.
- Safety-sensitive modules marked `safety_sensitive=True` and `safe_to_cache=False`:
  - `oos_repair`
  - `broker_paper_sandbox_readiness`

## Cache rules
- Cache is process-local and opt-in.
- Cache is bypassable explicitly.
- Cached outputs are deep-copied before return.
- No persistence to disk.
- No credentials/live-authorization/order-ready/broker state caching is introduced.

## Known path registry fields
- `name`
- `file_path`
- `role`
- `expected_latency_category`
- `safe_to_cache`
- `cache_scope`
- `invalidation_hint`
- `trading_runtime_path`
- `dev_validation_path`
- `safety_sensitive`
- `notes`

## Validation commands
```powershell
python -m pytest tests/forex_engine/test_evidence_cache_registry_v1.py -q
python -m py_compile automation/forex_engine/evidence_cache_registry_v1.py tests/forex_engine/test_evidence_cache_registry_v1.py
python -c "import time; s=time.perf_counter(); import automation.forex_engine.evidence_cache_registry_v1; print(round(time.perf_counter()-s, 4))"
python -m pytest tests/forex_engine/test_broker_paper_sandbox_readiness.py -q
python -m pytest tests/forex_engine -q --tb=short --durations=25
```

## Validation results
- Focused registry tests and compile validation were requested in packet scope.
- Runtime command execution is environment-dependent in this session; rerun in your shell to collect pass/fail and timings.

## Explicit exclusions
- This packet targets development/productivity latency only.
- No live trading enabled.
- No broker credential handling added.
- No network calls added.
- No order execution added.
- No risk thresholds weakened.
- No safety assertions skipped.
- Heavy proof/evidence work remains outside trade execution fast path.
- Reuse is deterministic and for evidence reuse only.

## Next safe action
- Wire opt-in cache usage into selected slow test paths only after registry tests pass, and then rerun the full `tests/forex_engine -q --tb=short --durations=25` baseline to measure total delta.
