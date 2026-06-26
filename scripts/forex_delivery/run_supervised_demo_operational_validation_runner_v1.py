"""CLI for the local AIOS Forex supervised demo validation runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.supervised_demo_operational_validation_runner_v1 import (  # noqa: E402
    run_supervised_demo_operational_validation,
)


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
        description="Run local PKT-FOREX-001 supervised demo validation."
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Local JSON file containing one validation input object.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write the local markdown packet report.",
    )
    args = parser.parse_args(argv)

    input_data = _load_input_json(args.input_json) if args.input_json else None
    result = run_supervised_demo_operational_validation(
        input_data=input_data, write_report=args.write_report
    )

    out = stdout if stdout is not None else sys.stdout
    out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


def _load_input_json(path: Path) -> dict[str, Any]:
    _reject_forbidden_input_path(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _reject_forbidden_input_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_INPUT_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local input path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
