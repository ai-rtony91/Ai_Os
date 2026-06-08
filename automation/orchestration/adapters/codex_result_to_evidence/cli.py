"""Preview-only CLI for CodexResultToEvidenceAdapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .evidence import run_preview


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview Codex final response as AI_OS evidence.")
    parser.add_argument("--input-result", help="Path to Codex final response text. Reads stdin when omitted.")
    args = parser.parse_args(argv)

    raw_text = Path(args.input_result).read_text(encoding="utf-8") if args.input_result else sys.stdin.read()
    print(json.dumps(run_preview(raw_text), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
