from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_IMPORT_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_IMPORT_ROOT))

from automation.bridge.aios_self_build_model import build_recommendations
from automation.bridge.aios_status_model import capture_repo_snapshot, read_json_if_exists, utc_now, write_json, write_markdown


REPORT_ROOT = Path("Reports/phase_0_to_4_bridge")


def inspect_self_build(repo_root: Path) -> dict[str, object]:
    now = utc_now()
    snapshot = capture_repo_snapshot(repo_root)
    phase0 = read_json_if_exists(repo_root / REPORT_ROOT / "phase0_infrastructure_inventory.json") or {}
    phase1 = read_json_if_exists(repo_root / REPORT_ROOT / "phase1_wiring_map.json") or {}
    phase2 = read_json_if_exists(repo_root / REPORT_ROOT / "phase2_approval_compressor_result.json") or {}
    phase3 = read_json_if_exists(repo_root / REPORT_ROOT / "phase3_governance_enforcement.json") or {}
    recommendations = build_recommendations(now, phase0 if isinstance(phase0, dict) else {})
    payload = {
        "timestamp_utc": now,
        "repo_root": snapshot.repo_root,
        "branch": snapshot.branch,
        "inputs_loaded": {
            "phase0": bool(phase0),
            "phase1": bool(phase1),
            "phase2": bool(phase2),
            "phase3": bool(phase3),
        },
        "recommendations": [item.to_dict() for item in recommendations],
        "status": "COMPLETE",
        "safe_next_action": "Review recommendations; do not execute automatically.",
    }
    write_json(repo_root / REPORT_ROOT / "phase4_self_build_inspection.json", payload)
    write_markdown(
        repo_root / REPORT_ROOT / "PHASE4_SELF_BUILD_INSPECTION.md",
        "Phase 4 Self-Build Inspection",
        {
            "SUMMARY": "Self-build inspection generated bounded recommendations only.",
            "INPUTS LOADED": payload["inputs_loaded"],
            "RECOMMENDATION COUNT": len(recommendations),
            "SAFE NEXT ACTION": payload["safe_next_action"],
        },
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run read-only AI_OS self-build inspection.")
    parser.add_argument("--mode", choices=["DRY_RUN"], default="DRY_RUN")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    payload = inspect_self_build(Path(args.repo_root).resolve())
    print(json.dumps({"status": payload["status"], "recommendation_count": len(payload["recommendations"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
