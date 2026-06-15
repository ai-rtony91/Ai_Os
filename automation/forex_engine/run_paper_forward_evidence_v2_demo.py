from __future__ import annotations

from automation.forex_engine import paper_forward_evidence_v2


def main(_argv: list[str] | None = None) -> int:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    for line in paper_forward_evidence_v2.evidence_v2_demo_lines(bundle):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
