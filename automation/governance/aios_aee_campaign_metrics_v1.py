from __future__ import annotations

"""Campaign metrics and work-intensity estimator for compound AEE tracks."""

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CampaignMetrics:
    files_created: int
    files_modified: int
    implementation_modules: int
    tests_written: int
    fixtures_written: int
    docs_written: int
    validation_commands_attempted: int
    validations_passed: int
    validations_blocked: int
    events_1312: int
    repair_loops: int
    estimated_work_units: int
    campaign_depth: str
    summary: dict[str, int]


def summarize_artifacts(paths: list[str]) -> dict[str, int]:
    counts = {
        "automation": 0,
        "scripts": 0,
        "tests": 0,
        "fixtures": 0,
        "docs": 0,
        "reports": 0,
        "other": 0,
    }
    for path in paths:
        normal = path.replace("\\", "/").lower()
        if normal.startswith("tests/fixtures/"):
            counts["fixtures"] += 1
        elif normal.startswith("automation/"):
            counts["automation"] += 1
        elif normal.startswith("scripts/"):
            counts["scripts"] += 1
        elif normal.startswith("tests/"):
            counts["tests"] += 1
        elif normal.startswith("docs/"):
            counts["docs"] += 1
        elif normal.startswith("reports/"):
            counts["reports"] += 1
        else:
            counts["other"] += 1
    return counts


def estimate_work_units(
    files_created: int,
    files_modified: int,
    implementation_modules: int,
    tests_written: int,
    fixtures_written: int,
    docs_written: int,
    validation_commands_attempted: int,
    validations_passed: int,
    validations_blocked: int,
    repair_loops: int,
) -> int:
    return (
        files_created * 5
        + files_modified * 3
        + implementation_modules * 12
        + tests_written * 1
        + fixtures_written * 1
        + docs_written * 5
        + validation_commands_attempted * 4
        + validations_passed * 2
        + validations_blocked * 3
        + repair_loops * 8
    )


def classify_campaign_depth(estimated_work_units: int) -> str:
    if estimated_work_units < 60:
        return "MICRO_PACKET"
    if estimated_work_units < 95:
        return "SHORT_PACKET"
    if estimated_work_units < 230:
        return "MEDIUM_PACKET"
    if estimated_work_units < 360:
        return "LONGRUN_PACKET"
    return "COMPOUND_LONGRUN_PACKET"


def build_campaign_metrics(
    *,
    created_files: list[str] | None = None,
    modified_files: list[str] | None = None,
    implementation_modules: list[str] | int = 0,
    tests_written: int = 0,
    fixtures_written: int = 0,
    docs_written: int = 0,
    validation_commands_attempted: int = 0,
    validations_passed: int = 0,
    validations_blocked: int = 0,
    events_1312: list[str] | int = 0,
    repair_loops: int = 0,
) -> CampaignMetrics:
    created = created_files or []
    modified = modified_files or []
    implementations = (
        len(implementation_modules)
        if isinstance(implementation_modules, list)
        else int(implementation_modules)
    )
    blocked = len(events_1312) if isinstance(events_1312, list) else int(events_1312)
    summary = summarize_artifacts(created + modified)
    work_units = estimate_work_units(
        files_created=len(created),
        files_modified=len(modified),
        implementation_modules=implementations,
        tests_written=tests_written,
        fixtures_written=fixtures_written,
        docs_written=docs_written,
        validation_commands_attempted=validation_commands_attempted,
        validations_passed=validations_passed,
        validations_blocked=validations_blocked,
        repair_loops=repair_loops,
    )
    return CampaignMetrics(
        files_created=len(created),
        files_modified=len(modified),
        implementation_modules=implementations,
        tests_written=tests_written,
        fixtures_written=fixtures_written,
        docs_written=docs_written,
        validation_commands_attempted=validation_commands_attempted,
        validations_passed=validations_passed,
        validations_blocked=validations_blocked,
        events_1312=blocked,
        repair_loops=repair_loops,
        estimated_work_units=work_units,
        campaign_depth=classify_campaign_depth(work_units),
        summary=summary,
    )


def result_to_markdown(result: CampaignMetrics) -> str:
    lines = [
        "# AIOS AEE Compound Campaign Metrics",
        "",
        f"- files_created: {result.files_created}",
        f"- files_modified: {result.files_modified}",
        f"- implementation_modules: {result.implementation_modules}",
        f"- tests_written: {result.tests_written}",
        f"- fixtures_written: {result.fixtures_written}",
        f"- docs_written: {result.docs_written}",
        f"- validation_commands_attempted: {result.validation_commands_attempted}",
        f"- validations_passed: {result.validations_passed}",
        f"- validations_blocked: {result.validations_blocked}",
        f"- events_1312: {result.events_1312}",
        f"- repair_loops: {result.repair_loops}",
        f"- estimated_work_units: {result.estimated_work_units}",
        f"- campaign_depth: {result.campaign_depth}",
        "",
        "## Summary",
        f"- automation: {result.summary['automation']}",
        f"- scripts: {result.summary['scripts']}",
        f"- tests: {result.summary['tests']}",
        f"- fixtures: {result.summary['fixtures']}",
        f"- docs: {result.summary['docs']}",
        f"- reports: {result.summary['reports']}",
    ]
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: CampaignMetrics) -> dict[str, object]:
    return asdict(result)


def result_to_operator_text(result: CampaignMetrics) -> str:
    return (
        f"work_units={result.estimated_work_units} "
        f"depth={result.campaign_depth} "
        f"files={result.files_created + result.files_modified} "
        f"tests={result.tests_written} "
        f"fixtures={result.fixtures_written}"
    )
