from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.replay_evidence_intake_v1 import (  # noqa: E402
    intake_replay_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
)
from automation.forex_engine.replay_proof_evidence_v1 import (  # noqa: E402
    REPLAY_PROOF_INCOMPLETE,
    REPLAY_PROOF_READY,
)


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def test_replay_intake_normalizes_readiness_json(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    payload = {
        "candidate_id": "candidate-001",
        "safety": {"is_safe": True},
        "bridge_payload": {
            "canonical_review_bundle": {
                "candidate_id": "candidate-001",
                "candidate": {
                    "candidate_id": "candidate-001",
                    "replay_proof": True,
                    "reconciliation_proof": True,
                    "rollback_proof": True,
                    "demo_validation_proof": True,
                    "freshness_proof": {"age_hours": 12},
                },
            }
        },
        "journey_payload": {
            "review_bundle": {
                "thresholds": {"max_freshness_age_hours": 48},
            }
        },
    }
    (report_root / "readiness_state_recalculation_v1_report.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    result = intake_replay_evidence(report_root)

    assert result["status"] == REPLAY_PROOF_READY
    assert result["normalized_summary"]["mismatch_count"] == 0
    assert result["normalized_summary"]["event_count"] == 4
    assert result["sanitized"] is True
    assert_permissions_false(result)


def test_replay_intake_stays_incomplete_without_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()

    result = intake_replay_evidence(report_root)

    assert result["status"] == REPLAY_PROOF_INCOMPLETE
    assert result["evidence_found"] is False
    assert "replay_id" in result["missing_fields"]
    assert_permissions_false(result)


def test_replay_intake_direct_markdown_fields_are_deterministic(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md").write_text(
        "\n".join(
            [
                "- replay_id: replay-direct-001",
                "- run_count: 2",
                "- event_count: 30",
                "- mismatch_count: 0",
                "- deterministic_replay: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_replay_evidence(report_root)

    assert result_to_jsonable_dict(result)["status"] == REPLAY_PROOF_READY
    assert "AIOS Forex Replay Evidence Intake V1" in result_to_operator_text(result)
    assert_permissions_false(result)


def test_replay_intake_discovers_matching_report_by_content(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    (report_root / "AIOS_FOREX_CUSTOM_REPLAY_SOURCE_V1.md").write_text(
        "\n".join(
            [
                "Deterministic replay proof summary.",
                "- replay_id: replay-discovered-001",
                "- run_count: 2",
                "- event_count: 30",
                "- mismatch_count: 0",
                "- deterministic_replay: true",
                "- sanitized: true",
                "- evidence_age_days: 1",
                "- max_evidence_age_days: 7",
            ]
        ),
        encoding="utf-8",
    )

    result = intake_replay_evidence(report_root)

    assert result["status"] == REPLAY_PROOF_READY
    assert any("AIOS_FOREX_CUSTOM_REPLAY_SOURCE_V1.md" in item for item in result["source_files"])
    assert result["normalized_summary"]["replay_id"] == "replay-discovered-001"
    assert_permissions_false(result)


def test_replay_intake_consumes_proof_bundle_json(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir()
    payload = {
        "enriched_candidate": {
            "candidate_id": "c1-eur-buy",
            "replay_proof": True,
            "reconciliation_proof": True,
            "rollback_proof": True,
            "demo_validation_proof": True,
            "freshness_proof": {"age_hours": 6},
        },
        "canonical_review_bundle": {
            "thresholds": {"max_freshness_age_hours": 48},
        },
        "safety": {
            "is_safe": True,
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
            "live_trading_authorized": False,
        },
    }
    (report_root / "proof_bundle_to_candidate_bridge_report.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    result = intake_replay_evidence(report_root)

    assert result["status"] == REPLAY_PROOF_READY
    assert result["normalized_summary"]["event_count"] == 4
    assert result["normalized_summary"]["mismatch_count"] == 0
    assert result["normalized_summary"]["evidence_age_days"] == 0.25
    assert result["normalized_summary"]["max_evidence_age_days"] == 2
    assert result["sanitized"] is True
    assert_permissions_false(result)
