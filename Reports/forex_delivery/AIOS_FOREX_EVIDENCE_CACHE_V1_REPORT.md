# AIOS Forex Evidence Cache + Known Path Registry V1

## Purpose
- Reduce redundant deterministic evidence construction time in forex tests by reusing a local cache layer in test helpers.
- Centralize hot evidence paths and keep execution paper-only and deterministic.

## Hot Paths Identified
- `automation/forex_engine/paper_forward_evidence_v2.py`
- `automation/forex_engine/oos_expansion.py`
- `automation/forex_engine/low_vol_edge_redesign.py`
- `automation/forex_engine/opportunity_capture.py`
- `automation/forex_engine/broker_paper_sandbox_readiness.py` (via helper-based fixture setup)

## Known Path Registry
Declared in `tests/forex_engine/forex_evidence_cache.py` as `KNOWN_EVIDENCE_PATHS`:
- `paper_forward_v2` → `automation/forex_engine/paper_forward_evidence_v2.py`
- `oos_expansion` → `automation/forex_engine/oos_expansion.py`
- `low_vol_edge_redesign` → `automation/forex_engine/low_vol_edge_redesign.py`
- `opportunity_capture` → `automation/forex_engine/opportunity_capture.py`
- `broker_paper_sandbox_readiness` → `automation/forex_engine/broker_paper_sandbox_readiness.py`

## Files Changed
- `tests/forex_engine/forex_evidence_cache.py` (new)
- `tests/forex_engine/test_forex_evidence_cache_v1.py` (new)
- `tests/forex_engine/test_paper_forward_evidence_v2.py`
- `tests/forex_engine/test_oos_expansion.py`
- `tests/forex_engine/test_low_vol_edge_redesign.py`
- `tests/forex_engine/test_opportunity_capture.py`
- `tests/forex_engine/test_broker_paper_sandbox_readiness.py`

## Timing Baseline (before)
- `test_broker_paper_sandbox_readiness.py`: **~190.69s**
- `test_paper_forward_evidence_v2.py`: **~51.29s**
- `test_oos_expansion.py`: **~44.35s**
- `test_low_vol_edge_redesign.py`: **~24.97s**
- `test_opportunity_capture.py`: **~21.04s**
- `test_opportunity_capture.py` includes repeated paper bundle calls that were repeatedly constructing full evidence.

## Timing After (deterministic cache layer) 
- Full benchmark run was not collectable in this environment due shell execution restriction.
- New benchmark target added:
  - `tests/forex_engine/test_forex_evidence_cache_v1.py::test_cache_speed_smoke_for_default_bundle`
  - Measures first-vs-second `get_paper_forward_v2_bundle()` call latency and asserts cached call is not slower.
- Command to capture true before/after timings locally:
  ```powershell
  python -m pytest tests/forex_engine/test_forex_evidence_cache_v1.py::test_cache_speed_smoke_for_default_bundle -q
  python -m pytest tests/forex_engine/test_paper_forward_evidence_v2.py tests/forex_engine/test_oos_expansion.py tests/forex_engine/test_low_vol_edge_redesign.py tests/forex_engine/test_opportunity_capture.py tests/forex_engine/test_broker_paper_sandbox_readiness.py -q
  ```

## Notes
- Cache wrappers use deep copies so tests can mutate returned payloads without cross-test contamination.
- Only test-path changes were made; production module behavior remains unchanged.
- No broker credentials, live trading, API calls, or network behavior were introduced.

## Expected Result
- Repeated deterministic pipeline calls in the five targeted files now reuse memoized results and reduce duplicated execution cost.
