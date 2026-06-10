"""AI_OS APPLY-counterpart inventory (observe-only scan).

Per the autonomy bridge map, dozens of DRY_RUN mutation scripts have no APPLY
twin, which is the human copy-paste bottleneck blocking the execute half of the
loop. This module SCANS (read-only) for every *.DRY_RUN.* script, classifies it
as mutation vs read-only, checks whether an APPLY counterpart exists, and ranks
the gaps. It builds the inventory; it does NOT create any APPLY file.

Pure standard library. Read-only over the filesystem. No mutation, no network.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


SCHEMA = "AIOS_APPLY_COUNTERPART_INVENTORY.v1"

DRY_RUN_NAME = re.compile(r"(?i)\.dry[_-]?run\.")

# PowerShell Verb-Noun read-only verbs (no APPLY twin needed).
READ_ONLY_VERBS = {"get", "read", "show", "test", "find", "measure", "inspect", "view", "summary", "preview", "report"}
# Verbs that mutate state (need an approval-gated APPLY twin).
MUTATION_VERBS = {"invoke", "update", "new", "write", "set", "move", "remove", "register",
                  "install", "resume", "start", "enable", "add", "clear", "rotate", "drain", "promote"}

# Directory names that are inert (examples, archives) — skip from priority ranking.
SKIP_DIR_PARTS = {"archive", "node_modules", ".git", "__pycache__", "fixtures", "mock-data"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _verb(name: str) -> Optional[str]:
    # PowerShell Verb-Noun: leading token before first '-'
    stem = name.split(".")[0]
    if "-" in stem:
        return stem.split("-", 1)[0].lower()
    return None


def _classify(name: str) -> tuple[str, Optional[str]]:
    verb = _verb(name)
    lower = name.lower()
    if verb in READ_ONLY_VERBS:
        return "READ_ONLY", verb
    if verb in MUTATION_VERBS:
        return "MUTATION", verb
    # keyword fallback for non Verb-Noun names
    if re.search(r"(?i)(runner|dispatch|executor|apply|resume|writer|register|scheduler)", lower):
        return "MUTATION", verb
    if re.search(r"(?i)(report|inventory|validator|summary|view|inspect|preview)", lower):
        return "READ_ONLY", verb
    return "UNKNOWN", verb


def _apply_twin(path: Path) -> Optional[Path]:
    name = path.name
    candidates = []
    # Name.DRY_RUN.ext -> Name.APPLY.ext
    candidates.append(re.sub(r"(?i)\.dry[_-]?run\.", ".APPLY.", name))
    # Name.DRY_RUN.ext -> Name.ext (twin without the marker)
    candidates.append(re.sub(r"(?i)\.dry[_-]?run\.", ".", name))
    for cand in candidates:
        if cand == name:
            continue
        twin = path.with_name(cand)
        if twin.exists():
            return twin
    return None


def _skip(path: Path, root: Path) -> bool:
    parts = set(p.lower() for p in path.relative_to(root).parts)
    return bool(parts & SKIP_DIR_PARTS)


def build_inventory(repo_root: Path, *, now: Optional[str] = None, include_skipped: bool = False) -> dict[str, object]:
    """Scan repo_root for DRY_RUN scripts and map APPLY-counterpart coverage."""
    repo_root = Path(repo_root)
    now = now or _now()
    items: list[dict] = []

    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if not DRY_RUN_NAME.search(path.name):
            continue
        skipped = _skip(path, repo_root)
        if skipped and not include_skipped:
            continue
        kind, verb = _classify(path.name)
        twin = _apply_twin(path)
        has_twin = twin is not None
        if kind == "MUTATION" and not has_twin:
            priority = "HIGH"
        elif kind == "UNKNOWN" and not has_twin:
            priority = "MEDIUM"
        else:
            priority = "NONE"
        items.append({
            "path": str(path.relative_to(repo_root)),
            "kind": kind,
            "verb": verb,
            "has_apply_twin": has_twin,
            "apply_twin": str(twin.relative_to(repo_root)) if twin else None,
            "priority": priority,
            "inert_dir": skipped,
        })

    mutation = [i for i in items if i["kind"] == "MUTATION"]
    needs_apply = [i for i in items if i["priority"] in {"HIGH", "MEDIUM"}]
    ranked = sorted(needs_apply, key=lambda i: (0 if i["priority"] == "HIGH" else 1, i["path"]))

    return {
        "schema": SCHEMA,
        "generated_at": now,
        "repo_root": str(repo_root),
        "total_dry_run_scripts": len(items),
        "counts": {
            "mutation_total": len(mutation),
            "mutation_without_apply": sum(1 for i in mutation if not i["has_apply_twin"]),
            "mutation_with_apply": sum(1 for i in mutation if i["has_apply_twin"]),
            "read_only": sum(1 for i in items if i["kind"] == "READ_ONLY"),
            "unknown": sum(1 for i in items if i["kind"] == "UNKNOWN"),
            "needs_apply_counterpart": len(needs_apply),
        },
        "ranked_needs_apply": ranked,
        "items": items,
        "observe_only": True,
        "safe_next_action": (
            "Inventory only. Building APPLY counterparts is a separate, approval-gated, "
            "Codex-East task — one twin at a time, each behind its own Human Owner approval. "
            "This scan creates no APPLY file."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory DRY_RUN scripts and APPLY-counterpart coverage (observe-only).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--include-skipped", action="store_true", help="include archive/fixture/mock dirs")
    parser.add_argument("--top", type=int, default=0, help="print only the top N ranked gaps")
    args = parser.parse_args()
    inv = build_inventory(Path(args.repo_root), include_skipped=args.include_skipped)
    if args.top:
        inv = {**inv, "ranked_needs_apply": inv["ranked_needs_apply"][: args.top], "items": "<omitted>"}
    print(json.dumps(inv, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
