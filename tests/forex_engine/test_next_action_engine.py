from pathlib import Path

from automation.forex_engine import next_action_engine


def test_module_import():
    assert next_action_engine.NEXT_ACTION_MODE == "PAPER_ONLY"


def test_default_next_action_recommends_long_run_supervisor():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
                "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
            "docs": [
                "AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
        },
        completed_packets=[],
        evidence_summary={
            "sessions": 1,
            "trades": 1,
            "missing_evidence_warnings": [],
        },
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_ALLOWED
    assert result["next_packet_bucket"] == "FOREX-LONG-RUN-PAPER-SUPERVISOR"


def test_live_goal_requires_approval():
    result = next_action_engine.recommend_next_action(
        requested_goal="Move to live trading for OANDA",
        blockers=["api key"],
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
                "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
        },
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_REQUIRES_APPROVAL
    assert result["approval_required"] is True
    assert result["protected_action_detected"] is True
    assert result["no_live_action_stop"] is True


def test_broker_credential_account_id_action_requires_approval():
    result = next_action_engine.recommend_next_action(
        blockers=["credential", "account id", "broker"],
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
            ],
            "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
        },
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_REQUIRES_APPROVAL
    assert result["approval_required"]
    assert result["protected_action_detected"]


def test_missing_evidence_ledger_recommends_ledger():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [],
            "docs": [],
        }
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_BLOCKED
    assert result["next_packet_bucket"] == "FOREX-EVIDENCE-LEDGER"


def test_missing_session_replay_recommends_session_replay():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": ["automation/forex_engine/evidence_ledger.py"],
            "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
        }
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_BLOCKED
    assert result["next_packet_bucket"] == "FOREX-SESSION-REPLAY"


def test_missing_dashboard_truth_recommends_truth_wiring():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
            ],
            "docs": [],
        }
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_BLOCKED
    assert result["next_packet_bucket"] == "AIOS-FOREX-DASHBOARD-TRUTH-WIRING"


def test_mature_paper_evidence_recommends_demo_readonly():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
                "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
            "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
        },
        completed_packets=["FOREX-LONG-RUN-PAPER-SUPERVISOR"],
        evidence_summary={"paper_session_count": 5, "paper_trade_count": 4, "drawdown": 2, "missing_evidence_warnings": []},
    )
    assert result["next_packet_bucket"] == "FOREX-DEMO-CONNECTOR-READONLY"


def test_immature_paper_evidence_recommends_long_run():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
                "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
            "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
        },
        completed_packets=["FOREX-LONG-RUN-PAPER-SUPERVISOR"],
        evidence_summary={"paper_session_count": 0, "paper_trade_count": 0},
    )
    assert result["next_packet_bucket"] == "FOREX-LONG-RUN-PAPER-SUPERVISOR"


def test_demo_readonly_then_mapping_then_reconciliation():
    base_state = {
        "modules": [
            "automation/forex_engine/evidence_ledger.py",
            "automation/forex_engine/session_replay.py",
            "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
        ],
        "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
    }
    evidence = {"paper_session_count": 2, "paper_trade_count": 3, "drawdown": 1, "missing_evidence_warnings": []}
    result = next_action_engine.recommend_next_action(
        repo_state=base_state,
        completed_packets=["FOREX-LONG-RUN-PAPER-SUPERVISOR", "FOREX-DEMO-CONNECTOR-READONLY"],
        evidence_summary=evidence,
    )
    assert result["next_packet_bucket"] == "FOREX-DEMO-ORDER-MAPPING"

    result2 = next_action_engine.recommend_next_action(
        repo_state=base_state,
        completed_packets=["FOREX-LONG-RUN-PAPER-SUPERVISOR", "FOREX-DEMO-CONNECTOR-READONLY", "FOREX-DEMO-ORDER-MAPPING"],
        evidence_summary=evidence,
    )
    assert result2["next_packet_bucket"] == "FOREX-DEMO-RECONCILIATION"


def test_protected_blocker_order_is_deterministic():
    result = next_action_engine.recommend_next_action(
        blockers=["webhook", "live", "broker"],
        requested_goal="live paper demo",
    )
    assert result["decision"] == next_action_engine.NEXT_ACTION_REQUIRES_APPROVAL
    assert result["blockers"] == ["webhook", "live", "broker"]


def test_result_shape_and_safety_flags():
    result = next_action_engine.recommend_next_action(repo_state={
        "modules": [
            "automation/forex_engine/evidence_ledger.py",
            "automation/forex_engine/session_replay.py",
            "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
        ],
        "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
    })
    expected_fields = {
        "allowed",
        "decision",
        "mode",
        "next_packet_bucket",
        "priority",
        "reason",
        "blockers",
        "protected_action_detected",
        "approval_required",
        "approval_reason",
        "missing_prerequisites",
        "safe_to_auto_build",
        "no_live_action_stop",
        "evidence_used",
        "recommended_validator_scope",
        "safety",
        "next_safe_action",
        "metadata",
    }
    assert expected_fields.issubset(set(result.keys()))
    assert result["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_self_improvement_recommendation_after_supervision():
    result = next_action_engine.recommend_next_action(
        repo_state={
            "modules": [
                "automation/forex_engine/evidence_ledger.py",
                "automation/forex_engine/session_replay.py",
                "docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md",
            ],
            "docs": ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md"],
        },
        completed_packets=[
            "FOREX-LONG-RUN-PAPER-SUPERVISOR",
            "FOREX-DEMO-CONNECTOR-READONLY",
            "FOREX-DEMO-ORDER-MAPPING",
            "FOREX-DEMO-RECONCILIATION",
        ],
        evidence_summary={"paper_session_count": 3, "paper_trade_count": 4, "demo_ready": True, "missing_evidence_warnings": []},
    )
    assert result["next_packet_bucket"] in {"AIOS-FOREX-SELF-IMPROVEMENT"}


def test_source_safety_scan():
    source = Path("automation/forex_engine/next_action_engine.py").read_text(encoding="utf-8")
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "broker_sdk",
        "getenv",
        "environ",
    ]
    for token in forbidden:
        assert token not in source
