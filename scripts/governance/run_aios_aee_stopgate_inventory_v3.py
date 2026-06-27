from __future__ import annotations

"""CLI runner for AEE stopgate inventory V3."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automation.governance.aios_aee_stopgate_inventory_v3 import (
    _allow_strict_exit,
    _parse_args,
    build_stopgate_inventory,
    result_to_jsonable_dict,
    result_to_markdown,
    result_to_operator_text,
)


def main() -> int:
    args = _parse_args()
    result = build_stopgate_inventory(
        Path(args.repo_root),
        branch=args.branch,
        dirty_files=args.dirty_file,
        strict=args.strict,
        continue_plan=args.continue_plan,
        simulate_1312=args.simulate_1312,
        simulate_targeted_tests_passed=args.simulate_targeted_tests_passed,
    )
    if args.json:
        from json import dumps

        print(dumps(result_to_jsonable_dict(result), sort_keys=True))
    else:
        print(result_to_operator_text(result))

    if args.write_report:
        path = Path(args.report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(result_to_markdown(result), encoding="utf-8")

    return 0 if (not args.strict or _allow_strict_exit(result.continuation_status)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
