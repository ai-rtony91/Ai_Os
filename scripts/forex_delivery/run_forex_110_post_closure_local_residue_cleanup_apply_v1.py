"""Run the Forex 110 local residue cleanup APPLY packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_110_post_closure_local_residue_cleanup_apply_v1 import (  # noqa: E402
    STATE_NAME,
    REPORT_NAME,
    build_report_markdown,
    run_forex_110_post_closure_local_residue_cleanup_apply_v1,
)


DEFAULT_OUTPUT_ROOT = ROOT / "Reports" / "forex_delivery"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--write-state", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args(argv)

    if not args.dry_run and not args.apply:
        args.dry_run = True

    report_root = Path(args.report_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    result = run_forex_110_post_closure_local_residue_cleanup_apply_v1(
        report_root,
        repo_root=ROOT if report_root.resolve() == DEFAULT_OUTPUT_ROOT.resolve() else report_root.parent,
        dry_run=args.dry_run,
    )
    report = build_report_markdown(result)

    if args.write_state:
        (output_root / STATE_NAME).write_text(
            json.dumps(result, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    if args.write_report:
        (output_root / REPORT_NAME).write_text(report, encoding="utf-8")

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
