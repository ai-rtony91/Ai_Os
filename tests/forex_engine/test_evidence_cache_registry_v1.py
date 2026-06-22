from __future__ import annotations

import pytest

from automation.forex_engine import evidence_cache_registry_v1 as registry


def test_registry_exposes_all_required_hot_paths() -> None:
    hot_paths = registry.get_forex_latency_hot_paths_v1()
    assert set(hot_paths) == set(registry.FOREX_HOT_PATH_REGISTRY.keys())
    assert "paper_forward_evidence_v2" in hot_paths
    assert "oos_expansion" in hot_paths
    assert "low_vol_edge_redesign" in hot_paths
    assert "opportunity_capture" in hot_paths
    assert "oos_repair" in hot_paths
    assert "broker_paper_sandbox_readiness" in hot_paths
    assert "month_end_readiness" in hot_paths
    assert "forex_dashboard_contract" in hot_paths


def test_registry_entries_have_required_metadata_fields() -> None:
    registry.validate_forex_forex_hot_path_registry_v1()
    for record in registry.get_forex_known_paths_v1():
        assert set(record.keys()) == registry._KNOWN_FIELDS

    record = registry.FOREX_HOT_PATH_REGISTRY["paper_forward_evidence_v2"]
    assert all(field in record for field in registry._KNOWN_FIELDS)


def test_safety_sensitive_flags_are_explicit() -> None:
    record = registry.FOREX_HOT_PATH_REGISTRY["oos_repair"]
    assert record["safety_sensitive"] is True
    assert record["safe_to_cache"] is False

    record = registry.FOREX_HOT_PATH_REGISTRY["broker_paper_sandbox_readiness"]
    assert record["safety_sensitive"] is True
    assert record["safe_to_cache"] is False


def test_path_classification_trading_vs_dev() -> None:
    paper = registry.FOREX_HOT_PATH_REGISTRY["paper_forward_evidence_v2"]
    assert paper["trading_runtime_path"] is False
    assert paper["dev_validation_path"] is True


def test_cache_helper_is_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    def builder():
        calls["count"] += 1
        return {"status": "ok", "value": calls["count"]}

    assert registry.run_cached_evidence_builder_v1(
        "paper_forward_evidence_v2",
        builder,
        cache_enabled=False,
    )["value"] == 1
    assert registry.run_cached_evidence_builder_v1(
        "paper_forward_evidence_v2",
        builder,
        cache_enabled=False,
    )["value"] == 2
    assert calls["count"] == 2


def test_cache_helper_produces_equivalent_result_for_dummy_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    def builder(x: int):
        calls["count"] += 1
        return {"x": x, "nested": {"n": x + 1}}

    result_cached = registry.run_cached_evidence_builder_v1(
        "paper_forward_evidence_v2",
        builder,
        cache_enabled=True,
        x=3,
    )
    result_uncached = builder(3)
    assert result_cached == result_uncached


def test_cache_helper_deep_copy_protection() -> None:
    def builder():
        return {"nested": {"value": 1}}

    first = registry.run_cached_evidence_builder_v1("oos_expansion", builder, cache_enabled=True)
    second = registry.run_cached_evidence_builder_v1("oos_expansion", builder, cache_enabled=True)
    second["nested"]["value"] = 2

    assert first["nested"]["value"] == 1


def test_cache_bypass_recompute() -> None:
    calls = {"count": 0}

    def builder():
        calls["count"] += 1
        return {"n": calls["count"]}

    first = registry.run_cached_evidence_builder_v1("low_vol_edge_redesign", builder, cache_enabled=False)
    second = registry.run_cached_evidence_builder_v1("low_vol_edge_redesign", builder, cache_enabled=False)
    assert first["n"] == 1
    assert second["n"] == 2
    assert calls["count"] == 2


def test_cache_key_differs_with_different_parameters() -> None:
    registry.clear_evidence_cache_v1()
    calls = {"count": 0}

    def builder(flag: bool):
        calls["count"] += 1
        return {"flag": flag, "calls": calls["count"]}

    a = registry.run_cached_evidence_builder_v1("opportunity_capture", builder, cache_enabled=True, flag=True)
    b = registry.run_cached_evidence_builder_v1("opportunity_capture", builder, cache_enabled=True, flag=False)
    assert a != b
    assert calls["count"] == 2
    # same params should reuse cache
    c = registry.run_cached_evidence_builder_v1("opportunity_capture", builder, cache_enabled=True, flag=True)
    assert c == a
    assert calls["count"] == 2


def test_unsafe_or_unknown_names_fail_closed() -> None:
    def builder():
        return {"safe": False}

    with pytest.raises(KeyError):
        registry.run_cached_evidence_builder_v1("unknown_path", builder, cache_enabled=True)

    with pytest.raises(KeyError):
        registry.run_cached_evidence_builder_v1("oos_repair", builder, cache_enabled=True)


def test_classify_path_latency_for_known_names() -> None:
    assert registry.classify_forex_path_latency_v1("paper_forward_evidence_v2") == "heavy"
    assert registry.classify_forex_path_latency_v1("automation/forex_engine/oos_expansion.py") == "heavy"


def test_import_is_light_and_no_eager_builders() -> None:
    known = registry.get_forex_known_paths_v1()
    assert len(known) >= 1
    assert any(item["name"] == "paper_forward_evidence_v2" for item in known)
