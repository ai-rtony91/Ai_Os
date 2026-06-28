"""CLI runner for protected action boundary verifier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import forex_protected_action_boundary_verifier_v1 as verifier_lib


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify protected action boundaries")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--report-path", default="Reports\\forex_delivery\\AIOS_FOREX_PROTECTED_ACTION_BOUNDARY_VERIFIER_V1_REPORT.md")
    parser.add_argument("--path", action="append", default=None, help="Optional file path to verify")
    parser.add_argument("--text", default=None, help="Optional raw text to verify")
    parser.add_argument("--payload-path", default=None, help="Optional JSON payload path")
    return parser.parse_args(argv)


def run_cli(argv: list[str] | None = None) -> str:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    result: dict
    if args.payload_path:
        payload = json.loads(Path(args.payload_path).read_text(encoding="utf-8"))
        result = verifier_lib.verify_protected_action_boundaries_payload(payload, strict=args.strict)
    elif args.path:
        result = verifier_lib.verify_protected_action_boundaries_files(args.path, strict=args.strict)
    elif args.text is not None:
        result = verifier_lib.verify_protected_action_boundaries_text(args.text, strict=args.strict)
    else:
        result = verifier_lib.verify_protected_action_boundaries_payload({}, strict=args.strict)

    if args.json:
        output = json.dumps(verifier_lib.protected_boundary_result_to_jsonable_dict(result), indent=2, sort_keys=True)
    else:
        output = verifier_lib.protected_boundary_result_to_markdown(result)
    report_path = Path(args.report_path)
    if not report_path.is_absolute():
        report_path = (repo_root / report_path).resolve()
    if args.write_report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(output, encoding="utf-8")
    return output


def main() -> None:
    print(run_cli())


if __name__ == "__main__":
    main()
