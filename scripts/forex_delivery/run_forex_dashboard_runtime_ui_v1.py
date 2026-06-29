from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_dashboard_runtime_ui_v1 import (  # noqa: E402
    DOCS_HTML_PATH,
    DOCS_PATH,
    PREVIEW_PATH,
    REPORT_PATH,
    STATE_PATH,
    build_dashboard_html,
    build_docs_markdown,
    build_report_markdown,
    run_forex_dashboard_runtime_ui_v1,
)


def _write(relative_path: Path, content: str) -> None:
    path = REPO_ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the repo-safe Forex dashboard runtime UI preview.")
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-docs", action="store_true")
    parser.add_argument("--write-html", action="store_true")
    parser.add_argument("--write-preview", action="store_true")
    args = parser.parse_args()

    result = run_forex_dashboard_runtime_ui_v1()

    if args.write_state:
        _write(STATE_PATH, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    if args.write_report:
        _write(REPORT_PATH, build_report_markdown(result))
    if args.write_docs:
        _write(DOCS_PATH, build_docs_markdown(result))
    if args.write_html or args.write_preview:
        html = build_dashboard_html(result)
        _write(PREVIEW_PATH, html)
        _write(DOCS_HTML_PATH, html)

    print(json.dumps(result, indent=2, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
