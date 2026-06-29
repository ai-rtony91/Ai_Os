from __future__ import annotations

import json
from pathlib import Path

import scripts.forex_delivery.run_forex_dashboard_runtime_ui_v1 as runner
from automation.forex_engine.forex_dashboard_runtime_ui_v1 import (
    BITWARDEN_STATUS,
    CANONICAL_DASHBOARD_ID,
    DASHBOARD_PACKAGE_FILES,
    DASHBOARD_VISUAL_HANDOFF_STATUS,
    DUPLICATE_DASHBOARD_POLICY,
    HIDDEN_DETAIL_RULES,
    PREVIEW_PATH,
    PROTECTED_BROKER_BOUNDARY_STATUS,
    REPORT_PATH,
    SOURCE_ARTIFACTS,
    STATE_PATH,
    build_dashboard_html,
    run_forex_dashboard_runtime_ui_v1,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation/forex_engine/forex_dashboard_runtime_ui_v1.py"

REQUIRED_LABELS = [
    "Command Center",
    "Safety Gate",
    "Candidate",
    "Evidence",
    "Broker Boundary",
    "Profit Readiness",
    "Reports",
    "SOS",
    "Settings",
    "Secrets Later",
]

PROTECTED_FALSE_KEYS = [
    "broker_api_used",
    "credentials_used",
    "env_read",
    "account_identifiers_used",
    "order_execution",
    "demo_authorized",
    "live_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_started",
    "background_loop_started",
    "bitwarden_started",
    "vaultwarden_started",
    "secrets_migration_started",
    "token_storage_started",
]

EXPECTED_PACKAGE_FILES = [
    "Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_PREVIEW.html",
    "Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json",
    "automation/forex_engine/forex_dashboard_runtime_ui_v1.py",
    "docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.html",
    "docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.md",
    "scripts/forex_delivery/run_forex_dashboard_runtime_ui_v1.py",
    "tests/forex_engine/test_forex_dashboard_runtime_ui_v1.py",
]


def test_output_is_deterministic_and_json_serializable() -> None:
    first = run_forex_dashboard_runtime_ui_v1()
    second = run_forex_dashboard_runtime_ui_v1()
    assert first == second
    json.dumps(first, sort_keys=True)


def test_all_required_source_artifacts_are_checked_and_present() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert set(result["source_artifacts_present"]) == {str(path) for path in SOURCE_ARTIFACTS}
    assert all(result["source_artifacts_present"].values())
    assert result["missing_source_artifacts"] == []


def test_dashboard_ready_and_forex_110_complete() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert result["dashboard_status"] == "FOREX_DASHBOARD_RUNTIME_UI_READY"
    assert result["forex_110_complete"] is True


def test_single_canonical_dashboard_surface_metadata() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert CANONICAL_DASHBOARD_ID == "FOREX_DASHBOARD_RUNTIME_UI_V1"
    assert result["canonical_dashboard_id"] == CANONICAL_DASHBOARD_ID
    assert result["canonical_dashboard_surfaces"] == [CANONICAL_DASHBOARD_ID]
    assert result["duplicate_dashboard_policy"] == DUPLICATE_DASHBOARD_POLICY
    assert result["no_alternate_dashboard_variants"] is True
    assert result["no_extra_dashboard_examples"] is True


def test_package_file_list_is_exactly_the_allowed_eight_files() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert DASHBOARD_PACKAGE_FILES == EXPECTED_PACKAGE_FILES
    assert result["dashboard_package_files"] == EXPECTED_PACKAGE_FILES
    assert len(result["dashboard_package_files"]) == 8


def test_dashboard_visual_handoff_remains_required() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert result["owner_visual_design_required"] is True
    assert result["dashboard_visual_handoff_status"] == DASHBOARD_VISUAL_HANDOFF_STATUS
    assert result["dashboard_visual_handoff_status"] == "HANDOFF_REQUIRED_BEFORE_FINAL_VISUAL_IMPLEMENTATION"


def test_all_ten_windows_exist_with_required_fields() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    windows = result["dashboard_windows"]
    assert [window["title"] for window in windows] == REQUIRED_LABELS
    assert len(windows) == 10
    for window in windows:
        assert set(window) == {
            "emoji",
            "title",
            "short_label",
            "default_summary",
            "detail_summary",
            "source_artifacts",
            "criticality",
            "hidden_by_default_fields",
        }
        assert window["emoji"]
        assert window["source_artifacts"]
        assert isinstance(window["hidden_by_default_fields"], list)


def test_html_contains_labels_buttons_and_detail_panels() -> None:
    html = build_dashboard_html(run_forex_dashboard_runtime_ui_v1())
    for label in REQUIRED_LABELS:
        assert label in html
    assert html.count('class="window-card"') == 10
    assert html.count('class="detail-panel"') == 10
    assert "data-panel=" in html
    assert "aria-controls=" in html


def test_html_is_static_local_and_has_no_external_references() -> None:
    html = build_dashboard_html(run_forex_dashboard_runtime_ui_v1()).lower()
    assert "http://" not in html
    assert "https://" not in html
    assert "<link" not in html
    assert "src=" not in html
    assert "fetch(" not in html
    assert "xmlhttprequest" not in html
    assert "websocket" not in html
    assert "localstorage" not in html


def test_html_does_not_include_secret_values() -> None:
    html = build_dashboard_html(run_forex_dashboard_runtime_ui_v1()).lower()
    forbidden_fragments = [
        "sk-",
        "api" + "_key",
        "password" + "=",
        "token" + "=",
        "secret" + "=",
    ]
    assert not any(fragment in html for fragment in forbidden_fragments)


def test_hidden_rules_and_boundaries_are_preserved() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    assert HIDDEN_DETAIL_RULES
    assert result["hidden_detail_rules"] == HIDDEN_DETAIL_RULES
    assert result["protected_boundary_summary"]["status"] == PROTECTED_BROKER_BOUNDARY_STATUS
    assert result["protected_broker_boundary_status"] == PROTECTED_BROKER_BOUNDARY_STATUS
    assert result["bitwarden_lock_summary"]["status"] == BITWARDEN_STATUS
    assert result["bitwarden_status"] == BITWARDEN_STATUS
    assert result["bitwarden_lock_summary"]["bitwarden_unlocked"] is False


def test_all_protected_booleans_are_false() -> None:
    result = run_forex_dashboard_runtime_ui_v1()
    for key in PROTECTED_FALSE_KEYS:
        assert result[key] is False


def test_runner_write_state_report_preview_stays_in_approved_outputs(monkeypatch) -> None:
    writes: list[str] = []

    def fake_write(relative_path: Path, content: str) -> None:
        assert content
        writes.append(str(relative_path).replace("\\", "/"))

    monkeypatch.setattr(runner, "_write", fake_write)
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_forex_dashboard_runtime_ui_v1.py",
            "--write-state",
            "--write-report",
            "--write-preview",
        ],
    )

    assert runner.main() == 0
    assert writes == [
        str(STATE_PATH).replace("\\", "/"),
        str(REPORT_PATH).replace("\\", "/"),
        str(PREVIEW_PATH).replace("\\", "/"),
        "docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.html",
    ]


def test_source_has_no_runtime_network_process_or_secret_access_code() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    forbidden_tokens = [
        "os.environ",
        "dotenv",
        "requests",
        "urllib",
        "subprocess",
        "socket",
        "create_connection",
        "startfile",
        "popen",
        "bitwarden implementation",
        "vaultwarden implementation",
    ]
    assert not any(token in source for token in forbidden_tokens)
