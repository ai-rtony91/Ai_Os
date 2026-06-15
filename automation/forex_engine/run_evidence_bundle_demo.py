from __future__ import annotations

import argparse

from automation.forex_engine import evidence_bundle_runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local AIOS forex evidence bundle demo.")
    parser.add_argument("--fixture-id", default=evidence_bundle_runner.DEFAULT_FIXTURE_ID)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bundle = evidence_bundle_runner.build_local_evidence_bundle(args.fixture_id)
    print("\n".join(evidence_bundle_runner.evidence_bundle_demo_lines(bundle)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
