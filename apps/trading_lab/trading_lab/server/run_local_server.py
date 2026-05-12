from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> int:
    try:
        import uvicorn
    except ImportError:
        print("FAIL: Python package 'uvicorn' is missing. Install apps/trading_lab/requirements.txt.")
        return 1

    from trading_lab.ingest.paper_signal_api import app

    if app is None:
        print("FAIL: Python package 'fastapi' is missing. Install apps/trading_lab/requirements.txt.")
        return 1

    print("AI_OS Trading Lab Local Paper Runtime")
    print("Paper Only: YES")
    print("Live Trading: BLOCKED")
    print("URL: http://127.0.0.1:8765")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="127.0.0.1", port=8765, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
