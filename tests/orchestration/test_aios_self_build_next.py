from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_self_build_next.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_self_build_next", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_module_imports() -> None:
    module = load_module()

    assert hasattr(module, "build_report")
    assert hasattr(module, "select_next_stage")


def test_output_is_json_compatible() -> None:
    module = load_module()

    report = module.build_report(REPO_ROOT)
    encoded = json.dumps(report, sort_keys=True)

    assert json.loads(encoded)["schema"] == "AIOS_SELF_BUILD_NEXT.v1"


def test_selected_stage_is_production_readiness_review() -> None:
    module = load_module()

    report = module.build_report(REPO_ROOT)

    assert report["selected_stage"]["stage_id"] == "STAGE-PRODUCTION-READINESS-REVIEW"
    assert report["packet_preview"]["packet_id"] == "PKT-PRODUCTION-READINESS-REVIEW-DRYRUN"


def test_packet_preview_has_required_fields() -> None:
    module = load_module()

    preview = module.build_report(REPO_ROOT)["packet_preview"]
    required_fields = {
        "packet_id",
        "mission",
        "worker",
        "lane",
        "branch",
        "worktree",
        "allowed_paths",
        "forbidden_paths",
        "validators",
        "stop_point",
        "final_report_format",
    }

    assert required_fields.issubset(preview)
    assert preview["worker"] == "EAST_OCC_01"
    assert preview["lane"] == "production-hardening-review"
    assert preview["branch"] == "main"
    assert preview["worktree"] == r"C:\Dev\Ai.Os"
    assert preview["preview_only"] is True


def test_safety_booleans_block_execution_and_mutation() -> None:
    module = load_module()

    safety = module.build_report(REPO_ROOT)["safety"]
    required_flags = {
        "execution",
        "mutation",
        "queue_mutation",
        "approval_mutation",
        "worker_launch",
        "runtime_launch",
        "broker_live_trading",
        "commits",
        "pushes",
    }

    assert required_flags == set(safety)
    assert all(value is False for value in safety.values())
