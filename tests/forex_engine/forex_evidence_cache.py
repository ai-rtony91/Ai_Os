from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from automation.forex_engine import oos_expansion
from automation.forex_engine import low_vol_edge_redesign
from automation.forex_engine import opportunity_capture
from automation.forex_engine import paper_forward_evidence_v2


KNOWN_EVIDENCE_PATHS = {
    "paper_forward_v2": "automation/forex_engine/paper_forward_evidence_v2.py",
    "oos_expansion": "automation/forex_engine/oos_expansion.py",
    "low_vol_edge_redesign": "automation/forex_engine/low_vol_edge_redesign.py",
    "opportunity_capture": "automation/forex_engine/opportunity_capture.py",
    "broker_paper_sandbox_readiness": "automation/forex_engine/broker_paper_sandbox_readiness.py",
}


@dataclass(frozen=True)
class _CacheKey:
    func_name: str
    fixture_signature: str = ""
    repair_signature: str = ""
    low_vol_signature: str = ""


_KNOWN_CACHE: dict[_CacheKey, dict[str, Any]] = {}


def _cache_result(key: _CacheKey, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    if key not in _KNOWN_CACHE:
        _KNOWN_CACHE[key] = builder()
    return deepcopy(_KNOWN_CACHE[key])


def get_paper_forward_v2_bundle(fixture_ids: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    if fixture_ids is None:
        requested = None
    else:
        requested = list(fixture_ids)
    return _cache_result(
        _CacheKey(
            "paper_forward_v2",
            _signature_of_fixture_ids(fixture_ids),
        ),
        lambda: paper_forward_evidence_v2.build_paper_forward_evidence_v2(requested),
    )


def get_expanded_oos_validation(
    fixture_ids: list[str] | tuple[str, ...] | None = None,
    oos_repair_result: dict[str, Any] | None = None,
    low_vol_edge_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if (
        fixture_ids is not None
        or oos_repair_result is not None
        or low_vol_edge_result is not None
    ):
        return oos_expansion.run_expanded_oos_validation(fixture_ids, oos_repair_result, low_vol_edge_result)
    key = _CacheKey("oos_expansion", _signature_of_fixture_ids(None))
    return _cache_result(key, lambda: oos_expansion.run_expanded_oos_validation())


def get_low_vol_edge_redesign(oos_repair_result: dict[str, Any] | None = None) -> dict[str, Any]:
    if oos_repair_result is not None:
        return low_vol_edge_redesign.apply_low_vol_edge_redesign(oos_repair_result)
    key = _CacheKey("low_vol_edge_redesign")
    return _cache_result(key, lambda: low_vol_edge_redesign.apply_low_vol_edge_redesign())


def get_opportunity_capture(evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    if evidence is not None:
        return opportunity_capture.calculate_opportunity_capture(evidence)
    evidence = get_paper_forward_v2_bundle()
    key = _CacheKey("opportunity_capture")
    return _cache_result(key, lambda: opportunity_capture.calculate_opportunity_capture(evidence))


def clear_cache() -> None:
    _KNOWN_CACHE.clear()


def _signature_of_fixture_ids(fixture_ids: list[str] | tuple[str, ...] | None) -> str:
    if fixture_ids is None:
        return "default"
    normalized = tuple(fixture_ids)
    return "|".join(normalized)
