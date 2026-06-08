"""Packet text parser for the preview-only adapter."""

from __future__ import annotations

import re

from .models import ParsedPacket

SECTION_RE = re.compile(r"^[A-Z][A-Z0-9_ /-]*:$")

KNOWN_SECTIONS = {
    "IDENTITY MARKER",
    "SUPERVISOR IDENTITY",
    "PACKET ID",
    "LANE",
    "ZONE",
    "WORKER IDENTITY",
    "MODE",
    "BRANCH",
    "WORKTREE",
    "APPROVAL AUTHORITY",
    "READ-FIRST AUTHORITY FILES",
    "ALLOWED PATHS",
    "FORBIDDEN PATHS",
    "PROTECTED PATHS",
    "VALIDATOR CHAIN",
    "MISSION",
    "TASK",
    "IMPLEMENTATION RULES",
    "STRICT RULES",
    "SUCCESS CRITERIA",
    "STOP POINT",
    "FINAL RESPONSE FORMAT",
}

KNOWN_MARKERS = {
    "CODEX-ONLY PROMPT",
    "AI_OS EXECUTION TOKEN",
    "AI_OS BOOTSTRAP REQUIRED",
}


def parse_packet(raw_text: str) -> ParsedPacket:
    """Parse packet text into markers and uppercase colon-delimited sections."""
    lines = raw_text.splitlines()
    first_line = lines[0].strip() if lines else ""
    markers: set[str] = set()
    sections: dict[str, str] = {}
    line_index: dict[str, int] = {}
    current_section: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer, current_section
        if current_section is not None:
            sections[current_section] = "\n".join(buffer).strip()
        buffer = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped in KNOWN_MARKERS:
            markers.add(stripped)
            continue

        if SECTION_RE.match(stripped) and stripped[:-1] in KNOWN_SECTIONS:
            flush()
            current_section = stripped[:-1]
            line_index[current_section] = index + 1
            continue

        if current_section is not None:
            buffer.append(line)

    flush()
    warnings = [] if raw_text.strip() else ["EMPTY_PACKET"]
    return ParsedPacket(
        raw_text=raw_text,
        first_line=first_line,
        markers=markers,
        sections=sections,
        line_index=line_index,
        parse_warnings=warnings,
    )
