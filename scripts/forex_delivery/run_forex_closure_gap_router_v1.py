"""CLI runner for the owner evidence closure gap router."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_closure_gap_router_v1 as router_lib
from automation.forex_engine import forex_owner_evidence_return_intake_v1 as intake_lib
from automation.forex_engine import forex_owner_evidence_return_validator_v1 as validator_lib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route owner evidence return gaps")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--intake-path",
        action="append",
        default=None,
        help="JSON intake payload path; optional",
    )
    parser.add_argument(
        "--validator-path",
        action="append",
        default=None,
        help="JSON validator payload path; optional",
    )
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_CLOSURE_GAP_ROUTER_V1_REPORT.md",
    )
    return parser.parse_args()


def _default_intake_payload(repo_root: Path) -> dict:
    catalog_path = repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1"
    return intake_lib.build_owner_evidence_return_intake(
        catalog_payload=None,
        catalog_paths=(str(catalog_path),),
        strict=False,
    )


def _default_validator_payload(repo_root: Path) -> dict:
    evidence_paths = sorted((repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1").glob("*.md"))[:8]
    return validator_lib.validate_owner_evidence_return_files(evidence_paths, strict=False)


def _load_json_payload(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    if args.intake_path:
        intake_path = Path(args.intake_path[0])
        intake_payload = _load_json_payload(intake_path)
    else:
        intake_payload = _default_intake_payload(repo_root)
    if args.validator_path:
        validator_payload = _load_json_payload(args.validator_path[0])
    else:
        validator_payload = _default_validator_payload(repo_root)
    payload = router_lib.route_owner_evidence_closure(
        intake_payload,
        validator_payload,
        strict=args.strict,
    )
    output = (
        json.dumps(router_lib.router_to_jsonable_dict(payload), indent=2, sort_keys=True)
        if args.json
        else router_lib.router_to_markdown(payload)
    )
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
