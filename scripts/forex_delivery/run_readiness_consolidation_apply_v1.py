#!/usr/bin/env python
"""Write the sanitized Forex readiness consolidation report."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.readiness_consolidation import (
    write_readiness_consolidation_report,
)

if __name__ == "__main__":
    result = write_readiness_consolidation_report()
    print(result["report_path"])
