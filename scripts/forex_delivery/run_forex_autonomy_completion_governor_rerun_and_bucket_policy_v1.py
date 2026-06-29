"""CLI runner for the Forex autonomy completion governor rerun + bucket policy layer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_autonomy_completion_governor_rerun_and_bucket_policy_v1 import (
    DEFAULT_GOVERNOR_INPUT_JSON_PATH,
    DEFAULT_STATE_JSON_PATH,
    run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1,
)


FORBIDDEN_INPUT_PATH_FRAGMENTS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "account",
    "oanda",
    "broker",
    "runtime",
    "scheduler",
    "daemon",
    "webhook",
    "production",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Forex autonomy completion governor rerun and bucket policy controller."
    )
    parser.add_argument(
        "--state-json",
        type=Path,
        default=DEFAULT_STATE_JSON_PATH,
        help="Path to sanitized autonomy completion state JSON.",
    )
    parser.add_argument(
        "--governor-input-json",
        type=Path,
        default=DEFAULT_GOVERNOR_INPUT_JSON_PATH,
        help="Path to sanitized governor input JSON.",
    )
    parser.add_argument(
        "--write-state",
        action="store_true",
        help=(
            "Write controller output into "
            "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
        ),
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=(
            "Write controller output report into "
            "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_REPORT.md"
        ),
    )
    args = parser.parse_args(argv)

    _reject_forbidden_input_path(args.state_json)
    _reject_forbidden_input_path(args.governor_input_json)
    result = run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        state_json=args.state_json,
        governor_input_json=args.governor_input_json,
        write_state=args.write_state,
        write_report=args.write_report,
    )
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


def _reject_forbidden_input_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_INPUT_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local input path: {path}")


if __name__ == "__main__":
    raise SystemExit(main())
