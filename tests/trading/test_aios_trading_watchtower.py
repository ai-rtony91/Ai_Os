from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "watchtower.py"
RESULT_SCHEMA = REPO_ROOT / "schemas" / "aios" / "trading" / "AIOS_TRADING_WATCHTOWER_RESULT.v1.schema.json"
CANDIDATE_SCHEMA = REPO_ROOT / "schemas" / "aios" / "trading" / "AIOS_TRADING_WATCHTOWER_CANDIDATE.v1.schema.json"


def load_watchtower_module():
    spec = importlib.util.spec_from_file_location("watchtower", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def candidate(symbol: str, confidence: float, risk_score: float, regime: str, direction: str = "LONG") -> dict:
    return {
        "symbol": symbol,
        "direction": direction,
        "confidence": confidence,
        "risk_score": risk_score,
        "regime": regime,
        "reason": f"{symbol} paper setup",
        "invalidation_level": 100.25,
        "evidence": ["trend", "volume", "structure"],
        "volatility_context": "normal",
    }


def test_module_imports_and_empty_payload_is_no_setup():
    watchtower = load_watchtower_module()
    result = watchtower.build_watchtower_result([], as_of_utc="2026-06-16T00:00:00Z")

    assert result["schema"] == "AIOS_TRADING_WATCHTOWER_RESULT.v1"
    assert result["watchtower_status"] == "NO_SETUP"
    assert result["execution_allowed"] is False
    assert result["broker_allowed"] is False
    assert result["order_submission_allowed"] is False
    assert result["live_trading_allowed"] is False
    assert result["next_best_setup"] is None


def test_ranks_highest_scoring_paper_candidate_first():
    watchtower = load_watchtower_module()
    payload = {
        "market_regime": "TREND_UP",
        "candidates": [
            candidate("GBPUSD", 0.54, 0.55, "RANGE"),
            candidate("EURUSD", 0.92, 0.18, "TREND_UP"),
            candidate("USDJPY", 0.70, 0.30, "LOW_VOL", direction="SHORT"),
        ],
    }
    result = watchtower.build_watchtower_result(payload, as_of_utc="2026-06-16T00:00:00Z")

    assert result["watchtower_status"] == "HIGH_PRIORITY"
    assert result["market_regime"] == "TREND_UP"
    assert [item["symbol"] for item in result["candidate_targets"]] == ["EURUSD", "USDJPY", "GBPUSD"]
    assert result["next_best_setup"]["symbol"] == "EURUSD"
    assert result["next_best_setup"]["priority_rank"] == 1
    assert result["priority_targets"][0]["symbol"] == "EURUSD"


def test_invalid_and_unsafe_candidates_are_dropped_from_ranking():
    watchtower = load_watchtower_module()
    payload = {
        "candidates": [
            candidate("EURUSD", 0.90, 0.20, "TREND_UP"),
            {**candidate("GBPUSD", 0.95, 0.10, "TREND_UP"), "invalidated": True},
            {**candidate("USDJPY", 0.99, 0.05, "TREND_UP"), "order_submission_allowed": True},
            {"symbol": "AUDUSD", "direction": "SIDEWAYS"},
        ]
    }
    result = watchtower.build_watchtower_result(payload, as_of_utc="2026-06-16T00:00:00Z")

    assert [item["symbol"] for item in result["candidate_targets"]] == ["EURUSD"]
    assert result["rejected_candidate_count"] == 3
    assert {item["reason_code"] for item in result["rejected_candidates"]} == {
        "invalidated",
        "order_submission_allowed_blocked",
        "unsupported_direction",
    }
    assert all(item["safe_to_rank"] is False for item in result["rejected_candidates"])


def test_security_stop_forces_review_required_and_suppresses_next_best_setup():
    watchtower = load_watchtower_module()
    security = {
        "preemptive_security": {
            "schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
            "component": "preemptive_security_layer",
            "overall_state": "STOP",
            "stop_required": True,
            "blocked_actions": ["APPLY", "git commit"],
        }
    }
    result = watchtower.build_watchtower_result(
        [candidate("EURUSD", 0.92, 0.18, "TREND_UP")],
        security_evidence=security,
        as_of_utc="2026-06-16T00:00:00Z",
    )

    assert result["watchtower_status"] == "REVIEW_REQUIRED"
    assert result["security_integration"]["review_required"] is True
    assert result["next_best_setup"] is None
    assert result["candidate_targets"][0]["symbol"] == "EURUSD"


def test_stale_missing_unknown_evidence_is_penalized_but_still_visible():
    watchtower = load_watchtower_module()
    strong = candidate("EURUSD", 0.75, 0.30, "TREND_UP")
    weak = {
        "symbol": "GBPUSD",
        "direction": "LONG",
        "confidence": 0.95,
        "risk_score": 0.10,
        "regime": "UNKNOWN",
        "reason": "stale paper setup",
        "stale": True,
    }
    result = watchtower.build_watchtower_result([weak, strong], as_of_utc="2026-06-16T00:00:00Z")

    assert result["ranking"]["penalizes_stale_missing_unknown_evidence"] is True
    assert result["candidate_targets"][0]["symbol"] == "EURUSD"
    stale_target = next(item for item in result["candidate_targets"] if item["symbol"] == "GBPUSD")
    assert "stale_evidence" in stale_target["penalties"]
    assert "unknown_regime" in stale_target["penalties"]
    assert "missing_invalidation_level" in stale_target["penalties"]


def test_all_invalidated_candidates_returns_invalidated_state():
    watchtower = load_watchtower_module()
    result = watchtower.build_watchtower_result(
        [{**candidate("EURUSD", 0.92, 0.18, "TREND_UP"), "invalidated": True}],
        as_of_utc="2026-06-16T00:00:00Z",
    )

    assert result["watchtower_status"] == "INVALIDATED"
    assert result["next_best_setup"] is None


def test_schemas_are_present_and_define_required_safety_fields():
    result_schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    candidate_schema = json.loads(CANDIDATE_SCHEMA.read_text(encoding="utf-8"))

    assert result_schema["properties"]["execution_allowed"]["const"] is False
    assert result_schema["properties"]["broker_allowed"]["const"] is False
    assert result_schema["properties"]["order_submission_allowed"]["const"] is False
    assert result_schema["properties"]["live_trading_allowed"]["const"] is False
    assert candidate_schema["properties"]["regime"]["enum"] == [
        "TREND_UP",
        "TREND_DOWN",
        "RANGE",
        "HIGH_VOL",
        "LOW_VOL",
        "UNKNOWN",
    ]


def test_source_does_not_import_execution_or_network_modules():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    forbidden = [
        "import requests",
        "from requests",
        "import socket",
        "paper_broker",
        "live_broker",
        ".submit_order(",
        ".create_order(",
    ]
    for token in forbidden:
        assert token not in source
