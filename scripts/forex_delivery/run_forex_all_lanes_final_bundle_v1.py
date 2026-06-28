"""CLI runner for the Forex all-lanes final bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_all_lanes_completion_router_v1 as router_lib
from automation.forex_engine import forex_all_lanes_final_bundle_v1 as final_bundle_lib
from automation.forex_engine import forex_all_lanes_gap_classifier_v1 as classifier_lib
from automation.forex_engine import forex_all_lanes_goal_manifest_v1 as manifest_lib
from automation.forex_engine import forex_all_lanes_operating_readiness_projector_v1 as projector_lib
from automation.forex_engine import forex_all_lanes_owner_boundary_gate_v1 as owner_gate_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Forex all-lanes final bundle")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports/forex_delivery/AIOS_FOREX_ALL_LANES_FINAL_BUNDLE_V1_REPORT.md",
    )
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    manifest = manifest_lib.build_all_lanes_goal_manifest(repo_root=repo_root, strict=args.strict)
    classifier = classifier_lib.classify_all_lanes_gaps(manifest)
    router = router_lib.route_all_lanes_completion(manifest, classifier)
    projector = projector_lib.project_all_lanes_operating_readiness(router)
    owner_boundary = owner_gate_lib.evaluate_all_lanes_owner_boundary(projector)
    result = final_bundle_lib.build_all_lanes_final_bundle(
        manifest,
        classifier,
        router,
        projector,
        owner_boundary,
    )
    output = (
        json.dumps(final_bundle_lib.final_bundle_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else final_bundle_lib.final_bundle_to_markdown(result)
    )
    if args.write_report:
        report_path = Path(args.report_path)
        if not report_path.is_absolute():
            report_path = repo_root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(final_bundle_lib.final_bundle_to_markdown(result), encoding="utf-8")
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
