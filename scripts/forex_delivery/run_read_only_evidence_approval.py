"""Run the read-only evidence approval and reconciliation dry run.

This script reads sanitized local evidence only. It never reads secrets, calls
brokers, places orders, or changes live execution permission.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.read_only_evidence_approval import (  # noqa: E402
    build_read_only_evidence_approval_model,
    cli_summary,
    write_read_only_evidence_approval_report,
)


def main(argv: list[str] | None = None) -> int:
    del argv
    result = build_read_only_evidence_approval_model(repo_root=REPO_ROOT)
    write_read_only_evidence_approval_report(result, repo_root=REPO_ROOT)
    print(json.dumps(cli_summary(result), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
