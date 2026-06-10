"""AI_OS path-guard validator (enforcement-in-code).

The governance validator proves packet SHAPE; the completion validator proves a
finished mission stayed in scope. This guard runs BEFORE a write/commit: given the
changed files and the packet's allowed/forbidden paths, it returns PASS or BLOCK.
It is designed to be called from a pre-commit hook so the allowed-path rule stops
being documentation and becomes enforced code.

It is read-only and decides nothing beyond PASS/BLOCK. It never stages, commits,
or edits anything. A PASS is not an approval; it only means the change set is
inside the declared boundary.

Pure standard library. No network, no mutation.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


VALIDATOR_NAME = "aios_path_guard_validator"
SCHEMA = "AIOS_PATH_GUARD.v1"


def _norm(p: str) -> str:
    return p.strip().strip("-").strip().strip("`").replace("\\", "/").strip().rstrip("/")


def _under(path: str, prefix: str) -> bool:
    path = path.replace("\\", "/").strip().rstrip("/")
    prefix = prefix.replace("\\", "/").strip().rstrip("/")
    if not prefix:
        return False
    return path == prefix or path.startswith(prefix + "/")


def extract_path_list(packet_text: str, marker: str) -> list[str]:
    """Collect path entries under an ALL-CAPS marker until the next section header."""
    out: list[str] = []
    capturing = False
    for line in packet_text.splitlines():
        stripped = line.strip()
        if not capturing:
            if stripped.upper().startswith(marker):
                capturing = True
            continue
        if re.match(r"^[A-Z][A-Z _/-]{3,}:?\s*$", stripped) and stripped.upper() != marker:
            break
        if not stripped:
            continue
        cleaned = _norm(stripped)
        if cleaned and not cleaned.endswith(":") and ("/" in cleaned or "." in cleaned):
            out.append(cleaned)
    return out


def check_paths(
    changed_files: list[str],
    *,
    allowed_paths: Optional[list[str]] = None,
    forbidden_paths: Optional[list[str]] = None,
    input_path: str = "<path-guard>",
) -> dict[str, object]:
    """Return PASS/BLOCK for a change set against allowed/forbidden boundaries."""
    changed = [c.replace("\\", "/").strip() for c in (changed_files or []) if c.strip()]
    allowed = [_norm(a) for a in (allowed_paths or []) if _norm(a)]
    forbidden = [_norm(f) for f in (forbidden_paths or []) if _norm(f)]

    violations: list[dict] = []
    for c in changed:
        # forbidden takes precedence
        hit = next((f for f in forbidden if _under(c, f)), None)
        if hit is not None:
            violations.append({"file": c, "reason": "FORBIDDEN_PATH", "matched": hit})
            continue
        if allowed and not any(_under(c, a) for a in allowed):
            violations.append({"file": c, "reason": "OUT_OF_ALLOWED_SCOPE", "matched": None})

    status = "BLOCK" if violations else "PASS"
    return {
        "validator_name": VALIDATOR_NAME,
        "schema": SCHEMA,
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input_path": input_path,
        "status": status,
        "approves_protected_action": False,
        "changed_count": len(changed),
        "allowed_paths": allowed,
        "forbidden_paths": forbidden,
        "violations": violations,
        "safe_next_action": (
            "Within boundary. PASS is not an approval; protected actions still need their own gate."
            if status == "PASS"
            else "BLOCK: remove or rescope the listed files before writing/committing."
        ),
    }


def check_against_packet(changed_files: list[str], packet_text: str, input_path: str = "<packet>") -> dict[str, object]:
    return check_paths(
        changed_files,
        allowed_paths=extract_path_list(packet_text, "ALLOWED"),
        forbidden_paths=extract_path_list(packet_text, "FORBIDDEN"),
        input_path=input_path,
    )


def _git_staged_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            text=True, capture_output=True, check=False,
        )
        return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]
    except OSError:
        return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard a change set against allowed/forbidden paths (PASS/BLOCK).")
    parser.add_argument("--packet", help="packet .md to read ALLOWED/FORBIDDEN paths from")
    parser.add_argument("--allowed", action="append", default=[], help="explicit allowed path (repeatable)")
    parser.add_argument("--forbidden", action="append", default=[], help="explicit forbidden path (repeatable)")
    parser.add_argument("--changed", action="append", default=[], help="a changed file (repeatable)")
    parser.add_argument("--staged", action="store_true", help="use git staged files as the change set")
    args = parser.parse_args()

    changed = list(args.changed)
    if args.staged:
        changed += _git_staged_files()

    if args.packet:
        result = check_against_packet(changed, Path(args.packet).read_text(encoding="utf-8"), args.packet)
    else:
        result = check_paths(changed, allowed_paths=args.allowed, forbidden_paths=args.forbidden)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
