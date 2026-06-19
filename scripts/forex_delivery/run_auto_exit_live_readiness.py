"""Run auto-exit live readiness dry run."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.auto_exit_live_readiness import (  # noqa: E402
    build_auto_exit_live_readiness_model,
    cli_summary,
    write_auto_exit_live_readiness_report,
)


def main(argv: list[str] | None = None) -> int:
    del argv
    result = build_auto_exit_live_readiness_model(repo_root=REPO_ROOT)
    write_auto_exit_live_readiness_report(result, repo_root=REPO_ROOT)
    print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
