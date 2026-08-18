#!/usr/bin/env python3
"""Offline validation runner for the isolated all-pairs PAPER observer.

It deliberately has no credential loader, network client construction, daemon,
or launch command.  A separate owner-authorized runtime packet is required
before an observer can use configured Practice credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_persistent_all_pairs_m1_m2_observer_v1 import (  # noqa: E402
    OBSERVATION_SECONDS,
    RUNTIME_IDENTITY,
    SAFETY,
    SUPPORTED_GRANULARITIES,
    VERSION,
    eligible_forex_instruments,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instrument-payload", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = json.loads(args.instrument_payload.read_text(encoding="utf-8"))
    universe = eligible_forex_instruments(payload)
    print(json.dumps({
        "observer_version": VERSION,
        "runtime_identity": RUNTIME_IDENTITY,
        "target_observation_seconds": OBSERVATION_SECONDS,
        "completed_candle_timeframes": sorted(SUPPORTED_GRANULARITIES),
        "launch_status": "NOT_LAUNCHED_BY_OFFLINE_VALIDATOR",
        "universe": universe,
        **SAFETY,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
