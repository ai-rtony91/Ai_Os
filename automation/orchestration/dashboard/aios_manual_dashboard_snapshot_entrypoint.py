from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from typing import Any

from automation.orchestration.dashboard.aios_manual_dashboard_snapshot import create_manual_dashboard_snapshot


SUCCESS_STATUS = "WROTE"


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    metadata = create_manual_dashboard_snapshot(
        evidence={},
        now_utc=args.now_utc,
        output_root=args.output_root,
        filename=args.filename,
        overwrite=args.overwrite,
        manual_trigger=True,
    )

    print(json.dumps(_json_safe(metadata), sort_keys=True))
    return 0 if metadata.get("status") == SUCCESS_STATUS else 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a manual dashboard state snapshot report.")
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--filename", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--now-utc", default=None)
    return parser


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


__all__ = ["main"]
