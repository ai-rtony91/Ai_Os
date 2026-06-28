from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "forex_delivery" / "Invoke-AiOsForexBirthdayFinishCampaign.ps1"
BOARD = "Reports/forex_delivery/AIOS_FOREX_BIRTHDAY_FINISH_BOARD_V1.json"
REPORT = "Reports/forex_delivery/AIOS_FOREX_BIRTHDAY_FINISH_CAMPAIGN_V1_REPORT.md"
FINAL_OWNER_SENTENCE = (
    "AIOS Forex repo build work remaining is 0; boundary work remaining is "
    "owner-protected 3, external-evidence 1, broker/live 1750, safety-blocked "
    "25, deferred/stale 74; exact human session count is not stored unless a "
    "session ledger exists."
)


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_powershell_script_exists() -> None:
    assert SCRIPT.exists()


def test_script_contains_dry_run_and_apply_modes() -> None:
    text = script_text()
    assert "DRY_RUN" in text
    assert "APPLY" in text


def test_forbidden_action_text_is_present() -> None:
    text = script_text()
    required_phrases = [
        "No Git mutation.",
        "No network.",
        "No broker/API.",
        "No credentials.",
        "No account access.",
        "No trading.",
        "git add",
        "git commit",
        "git push",
        "broker/API access",
        "order placement",
        "money movement",
        "scheduler activation",
        "daemon activation",
        "webhook activation",
        "production activation",
        "autonomous trading",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_target_date_and_required_output_paths_are_present() -> None:
    text = script_text()
    assert "2026-07-06" in text
    assert BOARD in text
    assert REPORT in text


def test_exact_counts_are_present() -> None:
    text = script_text()
    required_counts = {
        "raw_goal_count": 1998,
        "repo_actionable_forex_lanes": 0,
        "repo_actionable_open_count": 0,
        "owner_protected_count": 3,
        "external_evidence_required_count": 1,
        "broker_live_boundary_count": 1750,
        "safety_blocked_count": 25,
        "deferred_or_stale_count": 74,
    }
    for key, value in required_counts.items():
        assert key in text
        assert str(value) in text
    assert "DEFERRED_OWNER_VALIDATION" in text


def test_final_owner_sentence_is_present() -> None:
    assert FINAL_OWNER_SENTENCE in script_text()


def test_script_contains_no_banned_placeholder_text() -> None:
    text = script_text()
    banned_tokens = [
        "TODO",
        "TBD",
        "@filename",
        "probably",
        "roughly",
        "approximately",
        "I estimate",
        "live ready",
        "profitable trading readiness: true",
        "autonomous trading readiness: true",
    ]
    for token in banned_tokens:
        assert token not in text
