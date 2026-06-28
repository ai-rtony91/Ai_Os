"""CLI runner for the final owner review packet composer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_closure_gap_router_v1 as router_lib
from automation.forex_engine import forex_final_owner_review_packet_composer_v1 as composer_lib
from automation.forex_engine import forex_owner_evidence_return_intake_v1 as intake_lib
from automation.forex_engine import forex_owner_evidence_return_orchestrator_v1 as orchestrator_lib
from automation.forex_engine import forex_owner_evidence_return_validator_v1 as validator_lib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose Forex owner review packets")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--intake-path",
        default=None,
        help="Optional JSON intake payload",
    )
    parser.add_argument(
        "--validator-path",
        default=None,
        help="Optional JSON validator payload",
    )
    parser.add_argument(
        "--report-path",
        default="Reports\\forex_delivery\\AIOS_FOREX_FINAL_OWNER_REVIEW_PACKET_COMPOSER_V1_REPORT.md",
    )
    return parser.parse_args()


def _default_route_payload(repo_root: Path, strict: bool) -> dict:
    orchestration = orchestrator_lib.orchestrate_owner_evidence_return(
        repo_root=repo_root,
        strict=strict,
    )
    return orchestration["route_payload"]


def _default_intake_payload(repo_root: Path, strict: bool) -> dict:
    catalog_path = repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1"
    return intake_lib.build_owner_evidence_return_intake(
        catalog_payload=None,
        catalog_paths=(str(catalog_path),),
        strict=strict,
    )


def _default_validator_payload(repo_root: Path, strict: bool) -> dict:
    evidence_paths = sorted((repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1").glob("*.md"))[:8]
    return validator_lib.validate_owner_evidence_return_files(evidence_paths, strict=strict)


def _load_json_payload(path: str | None) -> dict | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo_root)
    intake_payload = _load_json_payload(args.intake_path) or _default_intake_payload(repo_root, args.strict)
    validator_payload = _load_json_payload(args.validator_path) or _default_validator_payload(repo_root, args.strict)
    route_payload = _default_route_payload(repo_root, args.strict)
    if route_payload.get("route") == router_lib.ROUTE_INVALID_STATE:
        route_payload = router_lib.route_owner_evidence_closure(intake_payload, validator_payload, strict=args.strict)
    packet = composer_lib.compose_final_owner_review_packet(
        intake_payload,
        validator_payload,
        route_payload,
        strict=args.strict,
    )
    output = (
        json.dumps(composer_lib.packet_to_jsonable_dict(packet), indent=2, sort_keys=True)
        if args.json
        else composer_lib.packet_to_markdown(packet)
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
