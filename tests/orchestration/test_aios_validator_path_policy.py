from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation" / "orchestration" / "validators" / "Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
CONFIG = REPO_ROOT / "automation" / "orchestration" / "validators" / "VALIDATOR_CHAIN_CONFIG_001.json"

WATCHTOWER_PATH = "apps/trading_lab/trading_lab/watchtower.py"


def _copy_validator_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    validator_dir = repo / "automation" / "orchestration" / "validators"
    validator_dir.mkdir(parents=True)
    shutil.copy2(SCRIPT, validator_dir / SCRIPT.name)
    shutil.copy2(CONFIG, validator_dir / CONFIG.name)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    return repo, validator_dir / SCRIPT.name


def _extract_json(stdout: str) -> dict:
    start = stdout.rfind("\n{")
    if start >= 0:
        return json.loads(stdout[start + 1 :])
    start = stdout.find("{")
    assert start >= 0, stdout
    return json.loads(stdout[start:])


def _run_validator(repo: Path, script: Path, *args: str) -> dict:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return _extract_json(result.stdout)


def _validator_result(payload: dict, validator_id: str) -> dict:
    results = payload["orchestration_result_contract"]["validator_results"]
    return next(item for item in results if item["validator_id"] == validator_id)


def _fail_evidence(payload: dict) -> str:
    results = payload["orchestration_result_contract"]["validator_results"]
    return " | ".join(item["evidence"] for item in results if item["status"] == "FAIL")


def test_watchtower_path_requires_explicit_packet_allowed_path(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)

    payload = _run_validator(repo, script, "-ChangedPath", WATCHTOWER_PATH)

    assert payload["overall_result"] == "FAIL"
    assert _validator_result(payload, "blocked_paths")["status"] == "FAIL"
    assert WATCHTOWER_PATH in _fail_evidence(payload)


def test_exact_watchtower_path_passes_packet_scope_without_global_apps_allowance(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)

    payload = _run_validator(
        repo,
        script,
        "-ChangedPath",
        WATCHTOWER_PATH,
        "-AllowedPath",
        WATCHTOWER_PATH,
        "-ForbiddenPath",
        "apps/dashboard/",
    )

    assert payload["fail_count"] == 0
    assert _validator_result(payload, "packet_scope")["status"] == "PASS"
    assert _validator_result(payload, "allowed_paths")["status"] == "PASS"
    assert _validator_result(payload, "blocked_paths")["status"] == "PASS"
    assert payload["overall_result"] == "WARN"


def test_forbidden_path_wins_even_when_same_path_is_allowed(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)

    payload = _run_validator(
        repo,
        script,
        "-ChangedPath",
        WATCHTOWER_PATH,
        "-AllowedPath",
        WATCHTOWER_PATH,
        "-ForbiddenPath",
        WATCHTOWER_PATH,
    )

    assert payload["overall_result"] == "FAIL"
    assert _validator_result(payload, "blocked_paths")["status"] == "FAIL"
    assert WATCHTOWER_PATH in _fail_evidence(payload)


def test_broad_apps_allowed_scope_is_blocked(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)

    payload = _run_validator(
        repo,
        script,
        "-ChangedPath",
        WATCHTOWER_PATH,
        "-AllowedPath",
        "apps/",
    )

    assert payload["overall_result"] == "FAIL"
    assert _validator_result(payload, "packet_scope")["status"] == "FAIL"
    assert "Broad packet allowed paths are blocked" in _validator_result(payload, "packet_scope")["evidence"]


def test_unlisted_trading_lab_app_path_is_blocked_under_packet_scope(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)
    unlisted = "apps/trading_lab/trading_lab/other.py"

    payload = _run_validator(
        repo,
        script,
        "-ChangedPath",
        unlisted,
        "-AllowedPath",
        WATCHTOWER_PATH,
    )

    assert payload["overall_result"] == "FAIL"
    assert _validator_result(payload, "allowed_paths")["status"] == "FAIL"
    assert _validator_result(payload, "blocked_paths")["status"] == "FAIL"
    assert unlisted in _fail_evidence(payload)


def test_dashboard_secret_broker_and_live_paths_remain_blocked(tmp_path: Path):
    repo, script = _copy_validator_repo(tmp_path)
    dangerous_paths = [
        "apps/dashboard/js/panel.js",
        "secrets/local.json",
        ".env",
        "apps/trading_lab/broker/orders.py",
        "apps/trading_lab/OANDA/client.py",
        "apps/trading_lab/live_trading/router.py",
        "apps/trading_lab/real_orders/submit.py",
        "apps/trading_lab/webhook/server.py",
    ]

    for path in dangerous_paths:
        payload = _run_validator(
            repo,
            script,
            "-ChangedPath",
            path,
            "-AllowedPath",
            path,
            "-ForbiddenPath",
            "apps/dashboard/",
        )
        assert payload["overall_result"] == "FAIL", path
        assert path in _fail_evidence(payload), path
