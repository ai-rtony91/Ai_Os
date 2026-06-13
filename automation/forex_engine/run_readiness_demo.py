"""Run the deterministic Forex Engine PAPER_ONLY readiness demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.readiness import (
    build_valid_mock_signal,
    evaluate_paper_readiness,
)


def main() -> int:
    result = evaluate_paper_readiness(build_valid_mock_signal())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["accepted_for_paper"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
