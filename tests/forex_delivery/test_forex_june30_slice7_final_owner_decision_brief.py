import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECISION_PATH = ROOT / "Reports/forex_delivery/AIOS_FOREX_JUNE30_SLICE7_FINAL_OWNER_DECISION_BRIEF_V1.json"
REPORT_PATH = ROOT / "Reports/forex_delivery/AIOS_FOREX_JUNE30_SLICE7_FINAL_OWNER_DECISION_BRIEF_V1_REPORT.md"
LEDGER_PATH = ROOT / "Reports/forex_delivery/AIOS_FOREX_JUNE30_FINAL_SLICE_CLOSURE_LEDGER_V1.md"
PROFIT_PATH = ROOT / "Reports/forex_delivery/AIOS_FOREX_PROFIT_TRACK_HANDOFF_V1.md"

FINAL_OWNER_SENTENCE = (
    "AIOS Forex June 30 boundary campaign is complete: repo-actionable Forex work "
    "remaining is 0, Slices 1-7 are closed for boundary decision, and the next "
    "allowed lane is supervised paper/demo profit-track review only; live trading, "
    "broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, "
    "and 100-120 percent return claims remain blocked until separately proven and approved."
)


def _read_outputs():
    data = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    report = REPORT_PATH.read_text(encoding="utf-8")
    ledger = LEDGER_PATH.read_text(encoding="utf-8")
    profit = PROFIT_PATH.read_text(encoding="utf-8")
    all_text = json.dumps(data, sort_keys=True) + "\n" + report + "\n" + ledger + "\n" + profit
    return data, report, ledger, profit, all_text


def test_slice7_final_owner_decision_artifacts_exist():
    assert DECISION_PATH.exists()
    assert REPORT_PATH.exists()
    assert LEDGER_PATH.exists()
    assert PROFIT_PATH.exists()


def test_slice7_final_owner_decision_json_values():
    data, _, _, _, _ = _read_outputs()

    expected = {
        "target_date": "2026-06-30",
        "raw_goal_count": 1998,
        "repo_actionable_open_count": 0,
        "owner_protected_count": 3,
        "external_evidence_required_count": 1,
        "broker_live_boundary_count": 1750,
        "safety_blocked_count": 25,
        "deferred_or_stale_count": 74,
        "june30_boundary_campaign_status": "COMPLETE_FOR_BOUNDARY_CLOSURE",
        "repo_actionable_forex_work_remaining": 0,
        "operational_trading_status": "NOT_LIVE_APPROVED",
        "profit_track_status": "READY_FOR_SUPERVISED_PAPER_DEMO_REVIEW_ONLY",
        "live_micro_exception_status": "NOT_APPROVED_REQUIRES_SEPARATE_OWNER_DECISION",
        "autonomous_22_6_status": "TARGET_NOT_APPROVED",
        "return_objective_status": "TARGET_NOT_VERIFIED",
        "vacation_luxury_mode_status": "VISION_NOT_ACTIVE",
        "next_required_lane": "PROFIT_TRACK_P1_STRATEGY_PROFIT_EVIDENCE",
    }

    for key, value in expected.items():
        assert data.get(key) == value


def test_slice7_slices_verified_and_content_present():
    data, report, ledger, profit, all_text = _read_outputs()
    verified = {entry["slice_number"] for entry in data["slices_verified"]}
    assert verified == {f"Slice {number}" for number in range(1, 7)}

    required_text = [
        "# AIOS Forex June 30 Slice 7 Final Owner Decision Brief V1 Report",
        "# AIOS Forex June 30 Final Slice Closure Ledger V1",
        "# AIOS Forex Profit Track Handoff V1",
        "Slice 1: COMPLETE_PUBLISHED",
        "Slice 2: COMPLETE_PUBLISHED",
        "Slice 3: COMPLETE_PUBLISHED",
        "Slice 4: COMPLETE_PUBLISHED",
        "Slice 5: COMPLETE_PUBLISHED",
        "Slice 6: COMPLETE_PUBLISHED",
        "Slice 7: COMPLETE_FOR_PUBLICATION",
        "P1 Strategy Profit Evidence",
        "P2 Walk-Forward / OOS Profit Proof",
        "P3 Trade Candidate Selector",
        "P4 Risk / Position Sizing For Profit",
        "P5 Supervised Demo Profit Execution Review",
        "P6 Profit Loop",
        "100-120 percent return is a profit objective",
        "vacation/luxury mode is the vision",
        "22/6 is a target",
        "live trading is not approved",
        "AIOS Forex June 30 boundary campaign is complete",
    ]

    for expected in required_text:
        assert expected in all_text

    assert "Slice 7 status: COMPLETE_FOR_BOUNDARY_CLOSURE" in report
    assert "profit_track_status: READY_FOR_SUPERVISED_PAPER_DEMO_REVIEW_ONLY" in profit
    assert "operational_trading_status: NOT_LIVE_APPROVED" in ledger


def test_slice7_forbidden_actions_and_final_sentence():
    data, _, _, _, all_text = _read_outputs()
    required_forbidden_actions = [
        "broker/API access",
        "credentials",
        "account access",
        "demo trade without evidence gate",
        "live trade",
        "order placement",
        "order closure",
        "money movement",
        "scheduler activation",
        "daemon activation",
        "webhook activation",
        "production activation",
        "autonomous trading",
        "safety gate bypass",
        "safety gate weakening",
        "safety gate deletion",
        "claiming 100-120 percent returns as verified",
        "claiming vacation/luxury mode as active",
        "claiming 22/6 autonomy as approved",
    ]

    for action in required_forbidden_actions:
        assert action in data["forbidden_actions"]
        assert action in all_text

    assert data["final_owner_sentence"] == FINAL_OWNER_SENTENCE
    assert FINAL_OWNER_SENTENCE in all_text


def test_slice7_no_banned_placeholder_or_claim_tokens():
    _, _, _, _, all_text = _read_outputs()
    banned_tokens = [
        "TO" + "DO",
        "T" + "BD",
        "@" + "filename",
        "pro" + "bably",
        "rough" + "ly",
        "approx" + "imately",
        "I " + "estimate",
        "live " + "ready",
        "profitable trading readiness" + ": true",
        "autonomous trading readiness" + ": true",
    ]

    for token in banned_tokens:
        assert token not in all_text
