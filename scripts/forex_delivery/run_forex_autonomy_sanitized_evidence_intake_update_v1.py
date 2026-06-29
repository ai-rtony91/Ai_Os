"""CLI runner for sanitized evidence intake into the Forex autonomy completion lane."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_autonomy_sanitized_evidence_intake_update_v1 import (
    DEFAULT_GOVERNOR_INPUT_JSON_PATH,
    DEFAULT_INPUT_TEMPLATE_PATH,
    DEFAULT_STATE_JSON_PATH,
    DEFAULT_STATE_OUTPUT_PATH,
    DEFAULT_REPORT_OUTPUT_PATH,
    FORBIDDEN_INPUT_PATH_FRAGMENTS,
    build_safe_output_result_payload,
    run_forex_autonomy_sanitized_evidence_intake_update_v1,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run sanitized Forex autonomy completion evidence intake update."
    )
    parser.add_argument(
        "--state-json",
        type=Path,
        default=DEFAULT_STATE_JSON_PATH,
        help="Path to controller state JSON.",
    )
    parser.add_argument(
        "--governor-input-json",
        type=Path,
        default=DEFAULT_GOVERNOR_INPUT_JSON_PATH,
        help="Path to live micro governor input JSON.",
    )
    parser.add_argument(
        "--evidence-json",
        type=Path,
        help="Optional explicit sanitized evidence JSON.",
    )
    parser.add_argument(
        "--write-state",
        action="store_true",
        help=(
            "Write controller intake output to "
            "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json"
        ),
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Write controller intake report to "
            "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md"
        ),
    )
    parser.add_argument(
        "--write-input-template",
        action="store_true",
        help=(
            "Write template input file to "
            "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json"
        ),
    )
    args = parser.parse_args(argv)

    _reject_forbidden_input_path(args.state_json)
    _reject_forbidden_input_path(args.governor_input_json)
    if args.evidence_json is not None:
        _reject_forbidden_input_path(args.evidence_json)

    result = run_forex_autonomy_sanitized_evidence_intake_update_v1(
        state_json=args.state_json,
        governor_input_json=args.governor_input_json,
        evidence_json=args.evidence_json,
        write_state=args.write_state,
        write_state_path=DEFAULT_STATE_OUTPUT_PATH,
        write_report=args.write_report,
        write_report_path=DEFAULT_REPORT_OUTPUT_PATH,
        write_input_template=args.write_input_template,
        write_input_template_path=DEFAULT_INPUT_TEMPLATE_PATH,
    )
    sys.stdout.write(
        json.dumps(
            build_safe_output_result_payload(result, include_safety_boundary=False),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return 0


def _reject_forbidden_input_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_INPUT_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local input path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
