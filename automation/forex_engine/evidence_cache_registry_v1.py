from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any, Callable, TypeAlias


PathRecord: TypeAlias = dict[str, Any]


LatencyCategory = str
DEFAULT_CACHE_SCOPE = "process_local_session"
KNOWN_LATENCY_CATEGORIES = {"hot", "medium", "medium_to_hot", "heavy"}


FOREX_HOT_PATH_REGISTRY: dict[str, PathRecord] = {
    "paper_forward_evidence_v2": {
        "name": "paper_forward_evidence_v2",
        "file_path": "automation/forex_engine/paper_forward_evidence_v2.py",
        "role": "Builds deterministic paper-only evidence bundle for v2 review pipeline.",
        "expected_latency_category": "heavy",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when fixture catalog or builder implementation changes.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Core deterministic evidence bundle used by many downstream tests.",
    },
    "oos_expansion": {
        "name": "oos_expansion",
        "file_path": "automation/forex_engine/oos_expansion.py",
        "role": "Runs expanded out-of-sample plan and validation across deterministic split families.",
        "expected_latency_category": "heavy",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when split policy or fixture inputs change.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Purely deterministic pipeline when fixtures are fixed.",
    },
    "low_vol_edge_redesign": {
        "name": "low_vol_edge_redesign",
        "file_path": "automation/forex_engine/low_vol_edge_redesign.py",
        "role": "Computes low-volatility edge redesign policy and action result.",
        "expected_latency_category": "medium",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when repair input or policy inputs change.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Used after OOS repair in validation-only chains.",
    },
    "opportunity_capture": {
        "name": "opportunity_capture",
        "file_path": "automation/forex_engine/opportunity_capture.py",
        "role": "Summarizes simulated opportunity and opportunity-quality metrics.",
        "expected_latency_category": "medium",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when evidence bundle changes.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Deterministic metrics from evidence; does not change safety decisions.",
    },
    "oos_repair": {
        "name": "oos_repair",
        "file_path": "automation/forex_engine/oos_repair.py",
        "role": "Repairs OOS degradation blockers for deterministic test evidence.",
        "expected_latency_category": "medium",
        "safe_to_cache": False,
        "cache_scope": "disabled",
        "invalidation_hint": "never reuse across runs unless explicitly reviewed for deterministic proof.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": True,
        "notes": "Safety-sensitive and policy-adjacent; excluded from default caching.",
    },
    "broker_paper_sandbox_readiness": {
        "name": "broker_paper_sandbox_readiness",
        "file_path": "automation/forex_engine/broker_paper_sandbox_readiness.py",
        "role": "Evaluates readiness blockers for broker-paper sandbox path.",
        "expected_latency_category": "heavy",
        "safe_to_cache": False,
        "cache_scope": "disabled",
        "invalidation_hint": "recompute per evaluation to avoid stale readiness context.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": True,
        "notes": "Contains gate logic; cache must remain opt-in and explicit.",
    },
    "month_end_readiness": {
        "name": "month_end_readiness",
        "file_path": "automation/forex_engine/month_end_readiness.py",
        "role": "Builds month-end readiness review snapshot.",
        "expected_latency_category": "medium",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when review inputs or evidence bundle changes.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Consolidated review snapshot for regression output.",
    },
    "forex_dashboard_contract": {
        "name": "forex_dashboard_contract",
        "file_path": "automation/forex_engine/forex_dashboard_contract.py",
        "role": "Builds deterministic dashboard contract for evidence summaries.",
        "expected_latency_category": "light_to_medium",
        "safe_to_cache": True,
        "cache_scope": DEFAULT_CACHE_SCOPE,
        "invalidation_hint": "invalidate when summary input changes.",
        "trading_runtime_path": False,
        "dev_validation_path": True,
        "safety_sensitive": False,
        "notes": "Evidence-only dashboard contract builder.",
    },
}


_KNOWN_FIELDS = {
    "name",
    "file_path",
    "role",
    "expected_latency_category",
    "safe_to_cache",
    "cache_scope",
    "invalidation_hint",
    "trading_runtime_path",
    "dev_validation_path",
    "safety_sensitive",
    "notes",
}


@dataclass(frozen=True)
class _CacheKey:
    builder_name: str
    params_signature: str


_EVIDENCE_CACHE: dict[_CacheKey, Any] = {}


def get_forex_known_paths_v1() -> list[PathRecord]:
    return [dict(entry) for entry in FOREX_HOT_PATH_REGISTRY.values()]


def get_forex_latency_hot_paths_v1() -> list[str]:
    return sorted(FOREX_HOT_PATH_REGISTRY.keys())


def classify_forex_path_latency_v1(path_or_name: str) -> LatencyCategory:
    key = _normalize_path_or_name(path_or_name)
    if key in FOREX_HOT_PATH_REGISTRY:
        return FOREX_HOT_PATH_REGISTRY[key]["expected_latency_category"]
    raise KeyError(f"Unknown forex path: {path_or_name}")


def run_cached_evidence_builder_v1(
    builder_name: str,
    builder_fn: Callable[..., dict[str, Any]],
    *,
    cache_enabled: bool = True,
    copy_result: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    record = FOREX_HOT_PATH_REGISTRY.get(builder_name)
    if record is None:
        raise KeyError(f"Unknown builder_name: {builder_name}")
    if not record.get("safe_to_cache", False) and cache_enabled:
        raise KeyError(f"Caching disabled for builder_name: {builder_name}")
    if not cache_enabled:
        return dict(builder_fn(**kwargs))
    key = _build_cache_key(builder_name, kwargs)
    if key not in _EVIDENCE_CACHE:
        _EVIDENCE_CACHE[key] = builder_fn(**kwargs)
    cached = _EVIDENCE_CACHE[key]
    return copy.deepcopy(cached) if copy_result else cached


def clear_evidence_cache_v1() -> None:
    _EVIDENCE_CACHE.clear()


def validate_forex_hot_path_entry_structure_v1(record: PathRecord) -> None:
    missing = _KNOWN_FIELDS - set(record.keys())
    if missing:
        raise ValueError(f"Path record missing required fields: {sorted(missing)}")
    if record["expected_latency_category"] not in KNOWN_LATENCY_CATEGORIES and not str(
        record["expected_latency_category"]
    ).startswith("light") and not str(record["expected_latency_category"]).startswith("medium"):
        raise ValueError(f"Unknown latency category: {record['expected_latency_category']}")


def validate_forex_forex_hot_path_registry_v1() -> None:
    for value in FOREX_HOT_PATH_REGISTRY.values():
        validate_forex_hot_path_entry_structure_v1(value)


def _normalize_path_or_name(path_or_name: str) -> str:
    value = path_or_name.strip().lower()
    if value.endswith(".py") and "/" in value:
        value = value.rsplit("/", 1)[-1].replace(".py", "")
    return value


def _build_cache_key(builder_name: str, kwargs: dict[str, Any]) -> _CacheKey:
    serial = _stable_serialize(kwargs)
    hashed = hashlib.sha256(serial.encode("utf-8")).hexdigest()
    return _CacheKey(builder_name=builder_name, params_signature=hashed)


def _stable_serialize(value: Any) -> str:
    if isinstance(value, (str, int, float, bool, type(None))):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_stable_serialize(item) for item in value) + "]"
    if isinstance(value, dict):
        items = sorted((str(_stable_serialize(key)), _stable_serialize(value[key])) for key in value.keys())
        return "{" + ",".join(f"{k}:{v}" for k, v in items) + "}"
    return repr(value)
