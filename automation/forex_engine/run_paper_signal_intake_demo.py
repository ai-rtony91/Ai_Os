"""Run deterministic paper signal intake ledger demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.paper_signal_intake import (
    build_demo_local_signal,
    evaluate_local_signal_for_ledger,
)


def main() -> int:
    record = evaluate_local_signal_for_ledger(build_demo_local_signal())
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0 if record["accepted_for_paper"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
