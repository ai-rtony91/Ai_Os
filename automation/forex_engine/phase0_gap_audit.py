import os
from pathlib import Path

ROOTS = [
    Path("automation/forex_engine/"),
    Path("tests/forex_engine/"),
    Path("Reports/forex_delivery/")
]

OUTPUT = Path("Reports/forex_delivery/AIOS_FOREX_PHASE0_GAP_AUDIT_V1.md")

KEYWORDS = [
    "expectancy",
    "profit_factor",
    "drawdown",
    "trade_count",
    "walk_forward"
]

PIPELINE = [
    "data",
    "strategy",
    "mitigation",
    "evaluation",
    "candidate",
    "gate",
    "decision"
]

CLASS_MISSING = "MISSING"
CLASS_PARTIAL = "PARTIAL"
CLASS_PRESENT = "PRESENT"
CLASS_UNVERIFIED = "UNVERIFIED"


def fail(msg):
    raise SystemExit(msg)


def assert_paths():
    for p in ROOTS:
        if not p.exists():
            fail(f"MISSING_PATH: {p}")


def scan_files():
    contents = {}
    for root in ROOTS:
        for file in root.rglob("*"):
            if file.is_file():
                try:
                    contents[file] = file.read_text(errors="ignore").lower()
                except Exception:
                    contents[file] = ""
    return contents


def classify_keyword(keyword, contents):
    hits = [f for f, c in contents.items() if keyword in c]
    if not hits:
        return CLASS_MISSING, []
    if len(hits) < 2:
        return CLASS_PARTIAL, hits
    return CLASS_PRESENT, hits


def validate_pipeline(contents):
    pipeline_hits = {}
    for step in PIPELINE:
        hits = [f for f, c in contents.items() if step in c]
        if not hits:
            pipeline_hits[step] = CLASS_MISSING
        elif len(hits) < 2:
            pipeline_hits[step] = CLASS_PARTIAL
        else:
            pipeline_hits[step] = CLASS_PRESENT
    return pipeline_hits


def generate_report(contents):
    lines = []
    lines.append("# AIOS FOREX PHASE 0 GAP AUDIT V1\n")

    lines.append("## METRIC COVERAGE\n")
    for k in KEYWORDS:
        cls, hits = classify_keyword(k, contents)
        lines.append(f"- {k}: {cls} ({len(hits)} files)")

    lines.append("\n## PIPELINE VALIDATION\n")
    pipeline = validate_pipeline(contents)
    for step, status in pipeline.items():
        lines.append(f"- {step}: {status}")

    lines.append("\n## CLASSIFICATION LEGEND\n")
    lines.append("- MISSING: not found")
    lines.append("- PARTIAL: limited presence")
    lines.append("- PRESENT: broad presence")
    lines.append("- UNVERIFIED: not executed")

    return "\n".join(lines)


def main():
    assert_paths()
    contents = scan_files()
    report = generate_report(contents)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(report)


if __name__ == "__main__":
    main()