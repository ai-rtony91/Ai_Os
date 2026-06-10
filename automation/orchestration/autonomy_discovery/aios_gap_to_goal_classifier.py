"""AI_OS gap-to-goal classifier (closes the self-build detect -> goal arrow).

The autonomy inventory DETECTS gaps (missing components, known blockers). This
classifier turns those gaps into structured GOAL CANDIDATES shaped like the
goal_intake schema, so the existing goal -> packet generators can consume them.

Safety posture (deliberately conservative):
  * Output is CANDIDATES ONLY. Every goal carries candidate_status
    NEEDS_OPERATOR_CONFIRMATION, approval_required true, and mode_requested
    DRY_RUN. Nothing here generates a packet, runs a worker, or executes.
  * Always attaches the full safety blocked-paths set (broker/secrets/live/etc).
  * Flags protected_action_expected for risky gaps (scheduler/SOS/approval/
    dispatch-write/merge/push). It never marks a gap safe to auto-run.

Pure standard library. Read-only. No network. No mutation except an optional
explicit output report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_GAP_TO_GOAL_CANDIDATES.v1"

SAFETY_BLOCKED_PATHS = [
    "broker", "OANDA", "live_trading", "secrets", "credentials", ".env",
    "wallet", "webhooks", "git push", "git merge",
]

# Gaps touching these are protected/high-scrutiny: never auto-run, operator required.
PROTECTED_KEYWORDS = re.compile(
    r"(?i)(scheduler|autostart|cron|systemd|\bsos\b|broker|live|oanda|secret|"
    r"credential|approval|dispatch|night.?cycle|write.?path|\bmerge\b|\bpush\b|"
    r"arm|activate|mutate|schtasks)"
)

# Gaps that are likely Python-shaped (review/validator/classifier) -> West/Claude.
PYTHON_KEYWORDS = re.compile(r"(?i)(validat|classif|python|report|evidence|composer|index|inventory|router)")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:48] or "gap"


def _gap_fields(gap: Any) -> tuple[str, Optional[str], Optional[str]]:
    """Normalize a gap item (string or dict) to (text, area, evidence)."""
    if isinstance(gap, dict):
        text = str(gap.get("name") or gap.get("component") or gap.get("gap") or gap.get("text") or "")
        area = gap.get("area") or gap.get("target_area")
        evidence = gap.get("evidence") or gap.get("reason")
        return text, (str(area) if area else None), (str(evidence) if evidence else None)
    return str(gap), None, None


def _build_goal(text: str, area: Optional[str], evidence: Optional[str], urgency: str, operator: str, now: str) -> dict:
    protected = bool(PROTECTED_KEYWORDS.search(text)) or bool(area and PROTECTED_KEYWORDS.search(area))
    is_python = bool(PYTHON_KEYWORDS.search(text))
    target_area = area or _slug(text)
    goal_id = "goal-gap-" + _slug(text) + "-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    note = "Machine-generated GAP candidate. Requires operator confirmation before any packet generation."
    if evidence:
        note += " Evidence: " + evidence
    return {
        "goal_id": goal_id,
        "created_at": now,
        "operator": operator,
        "objective": "Close autonomy gap: " + text,
        "urgency": urgency,
        "target_area": target_area,
        "allowed_paths": [],  # operator/loop must scope; classifier never auto-scopes
        "blocked_paths": list(SAFETY_BLOCKED_PATHS),
        "mode_requested": "DRY_RUN",
        "worker_preference": "Claude Code West" if is_python else "Codex East",
        "approval_required": True,
        "protected_action_expected": protected,
        "notes": note,
        # candidate-only safety envelope (not part of goal_intake schema, but enforced here)
        "candidate_status": "NEEDS_OPERATOR_CONFIRMATION",
        "source_gap": text,
        "auto_executable": False,
    }


def classify_gaps_to_goals(inventory: Optional[dict], operator: str = "AI_OS gap classifier (machine)", now: Optional[str] = None) -> dict[str, object]:
    inventory = inventory or {}
    now = now or _now()
    goals: list[dict] = []
    seen: set[str] = set()

    # known_blockers are HIGH urgency; missing_components are MEDIUM.
    for gap in inventory.get("known_blockers", []) or []:
        text, area, evidence = _gap_fields(gap)
        if not text or text in seen:
            continue
        seen.add(text)
        goals.append(_build_goal(text, area, evidence, "HIGH", operator, now))

    for gap in inventory.get("missing_components", []) or []:
        text, area, evidence = _gap_fields(gap)
        if not text or text in seen:
            continue
        seen.add(text)
        goals.append(_build_goal(text, area, evidence, "MEDIUM", operator, now))

    protected_count = sum(1 for g in goals if g["protected_action_expected"])
    return {
        "schema": SCHEMA,
        "generated_at": now,
        "observe_only": True,
        "candidate_count": len(goals),
        "summary": {
            "high_urgency": sum(1 for g in goals if g["urgency"] == "HIGH"),
            "medium_urgency": sum(1 for g in goals if g["urgency"] == "MEDIUM"),
            "protected_action_expected": protected_count,
            "all_require_operator_confirmation": True,
            "any_auto_executable": False,
        },
        "goals": goals,
        "safe_next_action": (
            "Surface candidates to the operator. None are auto-executable; each needs "
            "operator confirmation and allowed-path scoping before packet generation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify autonomy inventory gaps into goal candidates (observe-only).")
    parser.add_argument("--inventory", help="path to an autonomy inventory JSON")
    parser.add_argument("--operator", default="AI_OS gap classifier (machine)")
    parser.add_argument("--output", help="optional: write candidates atomically to this path")
    args = parser.parse_args()

    inventory = None
    if args.inventory and Path(args.inventory).exists():
        try:
            inventory = json.loads(Path(args.inventory).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            inventory = None

    result = classify_gaps_to_goals(inventory, operator=args.operator)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=str(out.parent), delete=False, encoding="utf-8") as tmp:
            tmp.write(json.dumps(result, indent=2, sort_keys=True))
            Path(tmp.name).replace(out)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
