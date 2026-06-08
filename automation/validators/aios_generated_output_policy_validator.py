from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


REQUIRED_IGNORE_RULES = [
    "Reports/generated/",
    "Reports/runtime/",
    "telemetry/generated/",
    "telemetry/runtime/",
]

LEGACY_CURRENT_OUTPUTS = [
    "Reports/phase_0_to_4_bridge/phase0_infrastructure_inventory.json",
    "Reports/phase_0_to_4_bridge/phase1_wiring_map.json",
    "Reports/phase_0_to_4_bridge/phase4_self_build_inspection.json",
    "Reports/phase_0_to_4_bridge/AIOS_PHASE_0_TO_4_BRIDGE_RESULT.json",
    "Reports/phase_0_to_4_bridge/AIOS_PHASE_0_TO_4_BRIDGE_RESULT.md",
    "Reports/phase_0_to_4_bridge/PHASE0_INFRASTRUCTURE_INVENTORY.md",
    "Reports/phase_0_to_4_bridge/PHASE4_SELF_BUILD_INSPECTION.md",
    "telemetry/validator_results/AIOS_VALIDATOR_REGISTRY.current.json",
]

MILESTONE_EVIDENCE_PATHS = [
    "Reports/phase_0_to_4_bridge/app_service_bridge_v0_design_dry_run.md",
    "Reports/phase_0_to_4_bridge/app_service_bridge_v0_endpoint_contract.example.json",
    "Reports/phase_0_to_4_bridge/app_service_bridge_v0_validator_result.example.json",
]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _git_check_ignore(repo_root: Path, path_text: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", path_text],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def validate(repo_root: Path) -> dict[str, object]:
    gitignore_text = _read_text(repo_root / ".gitignore")
    bridge_text = _read_text(repo_root / "automation/bridge/aios_phase_bridge.py")
    self_build_text = _read_text(repo_root / "automation/self_build/aios_self_build_inspector.py")
    policy_text = _read_text(repo_root / "docs/AI_OS/generated_output_policy.md")

    failures: list[str] = []
    warnings: list[str] = []

    missing_rules = [rule for rule in REQUIRED_IGNORE_RULES if rule not in gitignore_text]
    if missing_rules:
        failures.append(f"Missing .gitignore rules: {', '.join(missing_rules)}")

    ignore_probe_paths = [
        "Reports/generated/phase_0_to_4_bridge/AIOS_PHASE_0_TO_4_BRIDGE_RESULT.json",
        "Reports/runtime/example.json",
        "telemetry/generated/validator_results/AIOS_VALIDATOR_REGISTRY.current.json",
        "telemetry/runtime/example.json",
    ]
    not_ignored = [path for path in ignore_probe_paths if not _git_check_ignore(repo_root, path)]
    if not_ignored:
        failures.append(f"Generated output probes are not ignored: {', '.join(not_ignored)}")

    source_text = f"{bridge_text}\n{self_build_text}"
    legacy_defaults = [path for path in LEGACY_CURRENT_OUTPUTS if path in source_text]
    if legacy_defaults:
        failures.append(f"Legacy current output paths still appear in generator defaults: {', '.join(legacy_defaults)}")

    if "Reports/generated/phase_0_to_4_bridge" not in source_text:
        failures.append("Bridge/self-build generator defaults do not include Reports/generated/phase_0_to_4_bridge")
    if "telemetry/generated/validator_results" not in bridge_text:
        failures.append("Bridge validator telemetry default does not include telemetry/generated/validator_results")

    ignored_milestones = [path for path in MILESTONE_EVIDENCE_PATHS if _git_check_ignore(repo_root, path)]
    if ignored_milestones:
        failures.append(f"Milestone evidence paths are blanket ignored: {', '.join(ignored_milestones)}")

    if not policy_text:
        failures.append("Generated output policy doc is missing")
    elif "Routine DRY_RUN current projections are generated output" not in policy_text:
        warnings.append("Generated output policy doc is present but missing expected routine projection language")

    status = "PASS" if not failures else "FAIL"
    return {
        "status": status,
        "validator": "aios_generated_output_policy_validator",
        "repo_root": repo_root.as_posix(),
        "required_ignore_rules": REQUIRED_IGNORE_RULES,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS generated-output policy boundaries.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.sample_check:
        payload = {"status": "BLOCKED", "reason": "--sample-check required"}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    payload = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['validator']}: {payload['status']}")
        for failure in payload["failures"]:
            print(f"FAIL: {failure}")
        for warning in payload["warnings"]:
            print(f"WARN: {warning}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
