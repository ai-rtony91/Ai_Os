"""Parser for Codex final response text."""

from __future__ import annotations

import re

from .models import ParsedResult

SECTION_RE = re.compile(r"^[A-Z][A-Z0-9_ /-]*:$")

KNOWN_SECTIONS = {
    "SUMMARY",
    "WHAT CHANGED",
    "FILES CHANGED",
    "VALIDATION",
    "REMAINING DIRTY FILES",
    "SAFE NEXT COMMAND",
    "STATUS",
    "WHAT WAS TESTED",
    "FINDINGS",
    "RECOMMENDATION",
    "WHAT FAILED",
    "WHY IT FAILED",
    "WHAT NEEDS TO HAPPEN NEXT",
    "WHERE TO REFERENCE",
    "SAFE NEXT COMMAND OR PROMPT",
}


def parse_result(raw_text: str) -> ParsedResult:
    sections: dict[str, str] = {}
    line_index: dict[str, int] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        buffer = []

    for index, line in enumerate(raw_text.splitlines()):
        stripped = line.strip()
        if SECTION_RE.match(stripped) and stripped[:-1] in KNOWN_SECTIONS:
            flush()
            current = stripped[:-1]
            line_index[current] = index + 1
            continue
        if current is not None:
            buffer.append(line)

    flush()
    warnings = [] if raw_text.strip() else ["EMPTY_RESULT"]
    if "STATUS" not in sections:
        warnings.append("MISSING_STATUS_SECTION")
    return ParsedResult(raw_text=raw_text, sections=sections, line_index=line_index, parse_warnings=warnings)
