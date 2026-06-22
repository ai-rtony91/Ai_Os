from __future__ import annotations

import time

import pytest

from tests.forex_engine import forex_evidence_cache as cache
from automation.forex_engine import low_vol_edge_redesign
from automation.forex_engine import oos_expansion


def test_cached_bundle_is_deep_copied() -> None:
    first = cache.get_paper_forward_v2_bundle()
    second = cache.get_paper_forward_v2_bundle()

    assert first is not second
    second["blockers"].append("mutated_by_test")
    assert "mutated_by_test" not in first["blockers"]


def test_paper_forward_bundle_cached_once(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.clear_cache()
    calls = {"count": 0}

    def fake_builder(*_args, **_kwargs):
        calls["count"] += 1
        return {"mode": "PAPER_ONLY", "blockers": [], "opportunity_capture": {"aggregate_paper_pnl": 0.0}}

    monkeypatch.setattr(cache.paper_forward_evidence_v2, "build_paper_forward_evidence_v2", fake_builder)

    assert cache.get_paper_forward_v2_bundle()["mode"] == "PAPER_ONLY"
    assert cache.get_paper_forward_v2_bundle()["mode"] == "PAPER_ONLY"
    assert calls["count"] == 1


def test_oos_expanded_and_low_vol_cached_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.clear_cache()
    calls = {"oos": 0, "low_vol": 0}

    def fake_oos(*_args, **_kwargs):
        calls["oos"] += 1
        return {"mode": "PAPER_ONLY", "split_results": [], "blockers": [], "classification": "PAPER_FORWARD_READY"}

    def fake_low_vol(*_args, **_kwargs):
        calls["low_vol"] += 1
        return {"mode": "PAPER_ONLY", "classification": "WATCHLIST"}

    monkeypatch.setattr(oos_expansion, "run_expanded_oos_validation", fake_oos)
    monkeypatch.setattr(low_vol_edge_redesign, "apply_low_vol_edge_redesign", fake_low_vol)

    assert cache.get_expanded_oos_validation()["mode"] == "PAPER_ONLY"
    assert cache.get_expanded_oos_validation()["mode"] == "PAPER_ONLY"
    assert cache.get_low_vol_edge_redesign()["mode"] == "PAPER_ONLY"
    assert cache.get_low_vol_edge_redesign()["mode"] == "PAPER_ONLY"

    assert calls["oos"] == 1
    assert calls["low_vol"] == 1


def test_opportunity_capture_cache_path_is_registered(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.clear_cache()
    def fake_builder(*_args, **_kwargs):
        return {
            "mode": "PAPER_ONLY",
            "blockers": [],
            "opportunity_capture": {"aggregate_paper_pnl": 0.0},
            "combined_stress_oos_gate": {
                "stress_classification": "PAPER_FORWARD_READY",
                "oos_classification": "PAPER_FORWARD_READY",
                "combined_classification": "PAPER_FORWARD_READY",
                "blockers": [],
            },
            "risk_governor": {"classification": "PAPER_FORWARD_READY", "blockers": []},
            "expanded_oos": {"classification": "PAPER_FORWARD_READY", "blockers": [], "live_ready": False},
            "oos_repair": {"repaired_classification": "PAPER_FORWARD_READY"},
            "stress_repair": {"stress_repair_status": "PAPER_FORWARD_READY"},
        }

    monkeypatch.setattr(
        cache.paper_forward_evidence_v2,
        "build_paper_forward_evidence_v2",
        fake_builder,
    )

    input_bundle = cache.get_paper_forward_v2_bundle()
    assert cache.get_opportunity_capture(input_bundle)["mode"] == "PAPER_ONLY"
    assert cache.get_opportunity_capture(input_bundle)["mode"] == "PAPER_ONLY"
    cache.clear_cache()


def test_known_evidence_paths() -> None:
    assert cache.KNOWN_EVIDENCE_PATHS["paper_forward_v2"].endswith("paper_forward_evidence_v2.py")
    assert cache.KNOWN_EVIDENCE_PATHS["oos_expansion"].endswith("oos_expansion.py")
    assert cache.KNOWN_EVIDENCE_PATHS["low_vol_edge_redesign"].endswith("low_vol_edge_redesign.py")
    assert cache.KNOWN_EVIDENCE_PATHS["opportunity_capture"].endswith("opportunity_capture.py")


def test_cache_speed_smoke_for_default_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    cache.clear_cache()
    calls = {"count": 0}

    def fake_builder(*_args, **_kwargs):
        calls["count"] += 1
        return {
            "mode": "PAPER_ONLY",
            "fixture_count": 10,
            "fixture_ids": [],
            "combined_stress_oos_gate": {
                "stress_classification": "PAPER_FORWARD_READY",
                "oos_classification": "PAPER_FORWARD_READY",
                "combined_classification": "PAPER_FORWARD_READY",
                "blockers": [],
            },
            "risk_governor": {"classification": "PAPER_FORWARD_READY", "blockers": []},
            "expanded_oos": {"classification": "PAPER_FORWARD_READY", "blockers": [], "live_ready": False},
            "oos_repair": {"repaired_classification": "PAPER_FORWARD_READY"},
            "stress_repair": {"stress_repair_status": "PAPER_FORWARD_READY"},
            "blockers": [],
            "opportunity_capture": {"aggregate_paper_pnl": 0.0},
        }

    monkeypatch.setattr(cache.paper_forward_evidence_v2, "build_paper_forward_evidence_v2", fake_builder)

    start = time.perf_counter()
    _ = cache.get_paper_forward_v2_bundle()
    first_ms = (time.perf_counter() - start) * 1000.0

    start = time.perf_counter()
    _ = cache.get_paper_forward_v2_bundle()
    second_ms = (time.perf_counter() - start) * 1000.0
    assert calls["count"] == 1
    assert second_ms <= first_ms + 5.0
    cache.clear_cache()
