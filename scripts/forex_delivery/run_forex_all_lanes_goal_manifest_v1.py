"""CLI runner for the Forex all-lanes goal manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_all_lanes_goal_manifest_v1 as manifest_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Forex all-lanes goal manifest")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--report-path",
        default="Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOAL_MANIFEST_V1_REPORT.md",
    )
    parser.add_argument(
        "--manifest-path",
        default="Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_MANIFEST_V1.md",
    )
    parser.add_argument(
        "--json-path",
        default="Reports/forex_delivery/AIOS_FOREX_ALL_LANES_GOALS_MANIFEST_V1.json",
    )
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    result = manifest_lib.build_all_lanes_goal_manifest(repo_root=repo_root, strict=args.strict)
    output = (
        json.dumps(manifest_lib.manifest_to_jsonable_dict(result), indent=2, sort_keys=True)
        if args.json
        else manifest_lib.manifest_to_markdown(result)
    )
    if args.write_report:
        for path_value, content in (
            (args.report_path, manifest_lib.manifest_to_markdown(result)),
            (args.manifest_path, manifest_lib.manifest_to_markdown(result)),
            (
                args.json_path,
                json.dumps(manifest_lib.manifest_to_jsonable_dict(result), indent=2, sort_keys=True),
            ),
        ):
            path = Path(path_value)
            if not path.is_absolute():
                path = repo_root / path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
