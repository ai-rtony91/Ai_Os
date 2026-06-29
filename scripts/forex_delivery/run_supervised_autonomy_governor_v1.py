"""CLI runner for the offline Forex supervised autonomy governor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine import supervised_autonomy_governor_v1 as governor  # noqa: E402


FORBIDDEN_INPUT_PATH_FRAGMENTS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "account",
    "runtime",
    "scheduler",
    "daemon",
    "webhook",
    "production",
)


def main(argv: list[str] | None = None, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate supervised Forex autonomy readiness."
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Local JSON file containing one candidate input object.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write the governor markdown output to the report path.",
    )
    args = parser.parse_args(argv)

    input_data = _load_input_json(args.input_json) if args.input_json else None
    result = governor.run_supervised_autonomy_governor(
        input_data=input_data,
        write_report=args.write_report,
    )

    out = stdout if stdout is not None else sys.stdout
    out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


def _load_input_json(path: Path) -> dict[str, Any]:
    _reject_forbidden_input_path(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("input JSON payload must be a JSON object")
    return payload


def _reject_forbidden_input_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_INPUT_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local input path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
