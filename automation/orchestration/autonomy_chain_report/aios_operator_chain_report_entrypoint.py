"""Manual stdout-only entrypoint for operator chain reports."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.orchestration.autonomy_chain_report.aios_operator_chain_report import (
    build_operator_chain_report,
)

FAILURE_SCHEMA = "AIOS_OPERATOR_CHAIN_REPORT_ENTRYPOINT_FAILURE.v1"
COMPONENT = "operator_chain_report_entrypoint"
SUPPORTED_FORMATS = {"json", "markdown"}


class ChainReportEntrypointError(ValueError):
    """Controlled entrypoint failure with a structured payload."""

    def __init__(self, verdict: str, error: str, next_safe_action: str) -> None:
        super().__init__(error)
        self.payload = _failure(verdict, error, next_safe_action)


def load_chain_result_from_text(text: str) -> dict[str, Any]:
    """Parse a caller-supplied JSON object without side effects."""

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ChainReportEntrypointError(
            "BLOCKED_INPUT_JSON_INVALID",
            "Input text is not valid JSON.",
            "Provide one M16 chain-result JSON object.",
        ) from exc
    if not isinstance(parsed, dict):
        raise ChainReportEntrypointError(
            "BLOCKED_INPUT_JSON_INVALID",
            "Input JSON root is not an object.",
            "Provide one M16 chain-result JSON object.",
        )
    return parsed


def render_operator_chain_report(
    chain_result: Mapping[str, Any],
    output_format: str = "json",
    now_utc: str | None = None,
) -> str:
    """Render M17 report JSON or Markdown from an injected chain result."""

    normalized_format = (output_format or "").lower()
    if normalized_format not in SUPPORTED_FORMATS:
        raise ChainReportEntrypointError(
            "BLOCKED_UNSUPPORTED_FORMAT",
            "Output format must be json or markdown.",
            "Use --format json or --format markdown.",
        )
    report = build_operator_chain_report(chain_result, now_utc=now_utc)
    if normalized_format == "json":
        return json.dumps(report, sort_keys=True, indent=2) + "\n"

    markdown = report.get("report_markdown")
    if not isinstance(markdown, str) or not markdown:
        raise ChainReportEntrypointError(
            "BLOCKED_REPORT_MARKDOWN_MISSING",
            "M17 report_markdown is missing.",
            "Render JSON output and inspect the blocked report.",
        )
    return markdown


def main(argv: Sequence[str] | None = None) -> int:
    """Read one chain-result object, render it to stdout, and stop."""

    parser = argparse.ArgumentParser(description="Render an AIOS operator chain report.")
    parser.add_argument("--input", dest="input_path")
    parser.add_argument("--format", dest="output_format", default="json")
    parser.add_argument("--stdin", action="store_true", dest="use_stdin")
    args = parser.parse_args(argv)

    try:
        _validate_format(args.output_format)
        if args.use_stdin and args.input_path:
            raise ChainReportEntrypointError(
                "BLOCKED_INPUT_SOURCE_CONFLICT",
                "Use either --stdin or --input, not both.",
                "Choose exactly one chain-result input source.",
            )
        if not args.use_stdin and not args.input_path:
            raise ChainReportEntrypointError(
                "BLOCKED_INPUT_SOURCE_MISSING",
                "No chain-result input source was supplied.",
                "Use --stdin or --input with one M16 chain-result JSON object.",
            )

        text = sys.stdin.read() if args.use_stdin else _read_input_file(args.input_path)
        chain_result = load_chain_result_from_text(text)
        rendered = render_operator_chain_report(chain_result, output_format=args.output_format)
        print(rendered, end="")
        report = json.loads(rendered) if args.output_format.lower() == "json" else build_operator_chain_report(chain_result)
        return 2 if _is_blocked_report_verdict(report.get("verdict")) else 0
    except ChainReportEntrypointError as exc:
        print(json.dumps(exc.payload, sort_keys=True, indent=2))
        return 2


def _validate_format(output_format: str) -> None:
    if (output_format or "").lower() not in SUPPORTED_FORMATS:
        raise ChainReportEntrypointError(
            "BLOCKED_UNSUPPORTED_FORMAT",
            "Output format must be json or markdown.",
            "Use --format json or --format markdown.",
        )


def _read_input_file(input_path: str | None) -> str:
    if not input_path:
        raise ChainReportEntrypointError(
            "BLOCKED_INPUT_SOURCE_MISSING",
            "No chain-result input source was supplied.",
            "Use --stdin or --input with one M16 chain-result JSON object.",
        )
    try:
        return Path(input_path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ChainReportEntrypointError(
            "BLOCKED_INPUT_FILE_READ_FAILED",
            "Input file could not be read.",
            "Provide a readable local M16 chain-result JSON file.",
        ) from exc


def _is_blocked_report_verdict(verdict: Any) -> bool:
    normalized = str(verdict or "")
    return normalized.startswith("BLOCKED") or normalized == "REPORT_BLOCKED_CHAIN"


def _failure(verdict: str, error: str, next_safe_action: str) -> dict[str, str]:
    return {
        "schema": FAILURE_SCHEMA,
        "component": COMPONENT,
        "verdict": verdict,
        "status": "blocked",
        "error": error,
        "next_safe_action": next_safe_action,
    }


if __name__ == "__main__":
    raise SystemExit(main())
