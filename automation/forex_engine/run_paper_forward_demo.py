from __future__ import annotations

import argparse

from automation.forex_engine import paper_forward_runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local AIOS forex paper-forward demo.")
    parser.add_argument("--fixture-id", default=paper_forward_runner.DEFAULT_FIXTURE_ID)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bundle = paper_forward_runner.run_paper_forward_demo_bundle(args.fixture_id)
    print("\n".join(paper_forward_runner.paper_forward_demo_lines(bundle)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
