from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_post_closure_local_residue_cleanup_apply_v1 import (  # noqa: E402
    REPORT_NAME,
    STATE_NAME,
    run_forex_110_post_closure_local_residue_cleanup_apply_v1,
)
from scripts.forex_delivery.run_forex_110_post_closure_local_residue_cleanup_apply_v1 import (  # noqa: E402
    main,
)


def test_run_applies_required_output_schema_and_safety_flags() -> None:
    result = run_forex_110_post_closure_local_residue_cleanup_apply_v1(
        ROOT / "Reports" / "forex_delivery",
        repo_root=ROOT,
        dry_run=True,
    )

    assert result["packet_id"] == "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1"
    assert result["cleanup_apply_status"] == "DRY_RUN_COMPLETE"
    assert result["deletion_performed"] is False
    assert result["deleted_count"] == 0
    assert result["git_clean_performed"] is False
    assert result["gitignore_modified"] is False
    assert result["broker_api_used"] is False
    assert result["credentials_used"] is False
    assert result["env_read"] is False
    assert result["account_identifiers_used"] is False
    assert result["order_execution"] is False
    assert result["demo_authorized"] is False
    assert result["live_authorized"] is False
    assert result["scheduler_started"] is False
    assert result["daemon_started"] is False
    assert result["webhook_started"] is False
    assert result["background_loop_started"] is False
    assert result["bitwarden_started"] is False
    assert set(result["safe_delete_categories"]) >= {
        "apps/dashboard/node_modules/",
        "Python __pycache__ directories",
        "Python .pyc files inside __pycache__",
        "apps/dashboard/dist/",
        ".pytest_cache/",
    }

    required_keys = {
        "packet_id",
        "cleanup_apply_status",
        "dry_run_manifest",
        "deleted_targets",
        "skipped_targets",
        "forbidden_targets_detected",
        "deletion_performed",
        "git_clean_performed",
        "gitignore_modified",
        "safe_delete_categories",
        "protected_do_not_touch",
        "before_counts",
        "after_counts",
        "deleted_count",
        "deleted_bytes_estimate",
        "non_ignored_untracked_count_before",
        "non_ignored_untracked_count_after",
        "ignored_local_generated_count_before",
        "ignored_local_generated_count_after",
        "forex_110_closure_landed",
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
        "next_safe_action",
        "ATTACK_TO_FINISH",
    }
    assert required_keys.issubset(result.keys())


def test_report_contains_safe_targets_and_next_action() -> None:
    result = run_forex_110_post_closure_local_residue_cleanup_apply_v1(
        ROOT / "Reports" / "forex_delivery",
        repo_root=ROOT,
        dry_run=True,
    )
    assert result["cleanup_apply_status"] in {
        "DRY_RUN_COMPLETE",
        "APPLY_NO_TARGETS",
        "APPLY_COMPLETED",
        "APPLY_BLOCKED",
    }
    assert "AIOS Forex 110 Post-Closure Local Residue Cleanup Apply V1" in _build_report_text(result)
    assert result["cleanup_apply_status"] in {
        "DRY_RUN_COMPLETE",
        "APPLY_NO_TARGETS",
        "APPLY_COMPLETED",
        "APPLY_BLOCKED",
    }


def test_runner_writes_state_and_report(tmp_path: Path) -> None:
    output_root = tmp_path / "out"
    exit_code = main(
        [
            "--report-root",
            str(ROOT / "Reports" / "forex_delivery"),
            "--output-root",
            str(output_root),
            "--dry-run",
            "--write-state",
            "--write-report",
        ],
    )
    assert exit_code == 0

    state_file = output_root / STATE_NAME
    report_file = output_root / REPORT_NAME
    assert state_file.exists()
    assert report_file.exists()

    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["packet_id"] == "PKT-FOREX-110-POST-CLOSURE-LOCAL-RESIDUE-CLEANUP-APPLY-V1"
    assert state["cleanup_apply_status"] in {
        "DRY_RUN_COMPLETE",
        "APPLY_BLOCKED",
        "APPLY_NO_TARGETS",
        "APPLY_COMPLETED",
    }
    assert "Apply" in report_file.read_text(encoding="utf-8")


def _build_report_text(result: dict) -> str:
    from automation.forex_engine.forex_110_post_closure_local_residue_cleanup_apply_v1 import build_report_markdown  # noqa: PLC0415

    return build_report_markdown(result)
