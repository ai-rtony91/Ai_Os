"""AI_OS Autonomy Bridge v1.

Connects local Relay evidence, Night Supervisor evidence, Morning Digest output,
and dashboard-readable state. This module is local-only, standard-library-only,
and evidence-only. It does not run shell commands, call the network, mutate Git,
read secrets, touch broker systems, or approve protected actions.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_AUTONOMY_BRIDGE_STATE.v1"
OUTPUTS = {
    "bridge_state": Path("telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json"),
    "morning_state": Path("telemetry/morning_digest/MORNING_DIGEST_STATE.json"),
    "morning_digest": Path("telemetry/morning_digest/MORNING_DIGEST_LATEST.md"),
}
BLOCKED_CAPABILITIES = [
    "live_trading",
    "broker_execution",
    "oanda_integration",
    "api_key_handling",
    "real_webhook_execution",
    "real_order_routing",
    "secret_handling",
    "worker_launch",
    "packet_mutation",
    "approval_mutation",
    "git_stage_commit_push",
]
FORBIDDEN_PATH_TERMS = (
    ".env",
    "secrets/",
    "credentials/",
    "private key",
    "broker",
    "oanda",
    "live webhook",
    "real order",
)
STATUS_ORDER = {"BLOCKED": 4, "NEEDS_APPROVAL": 3, "WARN": 2, "UNKNOWN": 1, "PASS": 0}
EXPLICIT_STATUS_MAP = {
    "BLOCKED": "BLOCKED",
    "UNSAFE_BLOCKED": "BLOCKED",
    "FAILED": "BLOCKED",
    "FAIL": "BLOCKED",
    "ERROR": "BLOCKED",
    "NEEDS_APPROVAL": "NEEDS_APPROVAL",
    "WAITING_APPROVAL": "NEEDS_APPROVAL",
    "WAITING_REVIEW": "NEEDS_APPROVAL",
    "APPROVAL_REQUIRED": "NEEDS_APPROVAL",
    "PENDING_APPROVAL": "NEEDS_APPROVAL",
    "WAITING": "NEEDS_APPROVAL",
    "WARN": "WARN",
    "WARNING": "WARN",
    "REVIEW": "WARN",
    "STALE": "WARN",
    "UNKNOWN": "UNKNOWN",
    "PASS": "PASS",
    "READY": "PASS",
    "COMPLETE": "PASS",
    "DONE": "PASS",
    "READY_FOR_NEXT_SAFE_ACTION": "PASS",
}
RISK_STATUS_MAP = {
    "BLOCKED": "BLOCKED",
    "BLOCKER": "BLOCKED",
    "HIGH": "NEEDS_APPROVAL",
    "MEDIUM": "NEEDS_APPROVAL",
    "LOW": "WARN",
}
BLOCKER_FALLBACK_TERMS = (
    "risk level: blocker",
    "risk level:** blocker",
    "live now",
    "real order",
    "buy order",
    "sell order",
    "place a buy",
    "place a sell",
    "broker execution",
    "live trading",
    "oanda",
    "api key",
    "secret",
    "credential",
    "webhook",
)
APPROVAL_FALLBACK_TERMS = (
    "approval required",
    "needs approval",
    "waiting approval",
    "waiting_approval",
    "approval_required",
    "human approval",
    "human_review_required",
)
WARN_FALLBACK_TERMS = ("warn", "review", "stale", "unknown")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json_safely(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except FileNotFoundError:
        return {"source_path": str(path), "status": "UNKNOWN", "error": "File missing."}
    except json.JSONDecodeError as exc:
        return {"source_path": str(path), "status": "BLOCKED", "error": f"JSON parse failed: {exc}"}
    except OSError as exc:
        return {"source_path": str(path), "status": "UNKNOWN", "error": str(exc)}
    if isinstance(payload, dict):
        payload.setdefault("source_path", str(path))
        return payload
    return {"source_path": str(path), "status": "BLOCKED", "error": "JSON root is not an object."}


def read_text_preview(path: Path, limit: int = 900) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""
    return " ".join(text.split())[:limit]


def _normalize_token(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _iter_explicit_values(item: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in (
        "status",
        "state",
        "supervisor_status",
        "night_supervisor_status",
        "classification",
        "result",
    ):
        if item.get(key) is not None:
            values.append(_normalize_token(item.get(key)))
    for key in ("risk_level", "risk"):
        if item.get(key) is not None:
            values.append(_normalize_token(item.get(key)))
    for key in ("gate_flags", "flags"):
        raw_flags = item.get(key)
        if isinstance(raw_flags, list):
            values.extend(_normalize_token(flag) for flag in raw_flags)
        elif raw_flags is not None:
            values.append(_normalize_token(raw_flags))
    return values


def _status_category(status: str, path: str, text: str) -> str:
    if status == "BLOCKED":
        return "blocked_action"
    if status == "NEEDS_APPROVAL":
        return "approval_request"
    if status == "WARN":
        return "validator_output" if "validator" in text or "validator" in path else "worker_output"
    if status == "PASS":
        return "worker_output"
    if path.startswith("relay/"):
        return "relay_input"
    return "unknown"


def _max_status(*statuses: str) -> str:
    known = [status for status in statuses if status in STATUS_ORDER]
    if not known:
        return "UNKNOWN"
    return max(known, key=lambda status: STATUS_ORDER[status])


def _explicit_status(item: dict[str, Any]) -> str | None:
    status: str | None = None
    for value in _iter_explicit_values(item):
        if value in EXPLICIT_STATUS_MAP:
            status = _max_status(status or "PASS", EXPLICIT_STATUS_MAP[value])
        if value in RISK_STATUS_MAP:
            status = _max_status(status or "PASS", RISK_STATUS_MAP[value])
        if "APPROVAL" in value or "HUMAN_REVIEW" in value:
            status = _max_status(status or "PASS", "NEEDS_APPROVAL")
        if any(term in value for term in ("BLOCK", "UNSAFE", "PROTECTED_ACTION")):
            status = _max_status(status or "PASS", "BLOCKED")
    return status


def _fallback_status(path: str, text: str, raw_status: str) -> str:
    if "/error/" in path or any(term in text for term in BLOCKER_FALLBACK_TERMS):
        return "BLOCKED"
    if "approval" in path or any(term in text for term in APPROVAL_FALLBACK_TERMS):
        return "NEEDS_APPROVAL"
    if raw_status in {"PASS", "READY", "COMPLETE", "DONE"} or any(term in path for term in ("/done/", "/processed/")):
        return "PASS"
    if any(term in text for term in WARN_FALLBACK_TERMS):
        return "NEEDS_APPROVAL"
    return "NEEDS_APPROVAL"


def classify_item(item: dict[str, Any]) -> dict[str, str]:
    text = " ".join(str(value) for value in item.values()).lower()
    path = str(item.get("source_path", "")).lower().replace("\\", "/")
    raw_status = str(item.get("status") or item.get("state") or item.get("supervisor_status") or "").upper()

    explicit = _explicit_status(item)
    fallback = _fallback_status(path, text, _normalize_token(raw_status))
    status = _max_status(explicit or "PASS", fallback)
    category = _status_category(status, path, text)

    if "dashboard" in path:
        category = "dashboard_note"
    if "morning" in path:
        category = "morning_digest"
    if "validator" in path:
        category = "validator_output"
    if "relay/" in path and category == "unknown":
        category = "relay_input"

    return {"status": status, "category": category}


def _item_from_path(path: Path, repo_root: Path) -> dict[str, Any]:
    rel = repo_relative(path, repo_root)
    payload = load_json_safely(path) if path.suffix.lower() == ".json" else {}
    text = json.dumps(payload, sort_keys=True) if payload else read_text_preview(path)
    classification = classify_item({"source_path": rel, "status": payload.get("status", ""), "text": text})
    title = path.stem.replace("_", " ").replace("-", " ").strip().title() or rel
    summary = payload.get("summary") or payload.get("plain_summary") or payload.get("next_safe_action") or text
    if not summary:
        summary = "Evidence found, but no readable summary was available."
    return {
        "title": str(title)[:90],
        "status": classification["status"],
        "category": classification["category"],
        "summary": str(summary)[:220],
        "source_path": rel,
        "next_safe_action": str(payload.get("next_safe_action") or "Review this evidence before protected action."),
    }


def collect_source_files(repo_root: str | Path) -> list[Path]:
    root = Path(repo_root).resolve()
    candidates: list[Path] = []
    patterns = [
        ("relay", "**/*"),
        ("telemetry/night_supervisor", "*.json"),
        ("telemetry/supervisor_briefs", "*.json"),
        ("telemetry/morning_digest", "*.json"),
        ("control/operation_glue", "**/*.json"),
        ("telemetry/operation_glue", "**/*.json"),
        ("automation/orchestration/night_supervisor", "*.json"),
        ("automation/orchestration/night_supervisor", "*.md"),
    ]
    for folder, pattern in patterns:
        base = root / folder
        if not base.exists():
            continue
        for path in sorted(base.glob(pattern)):
            if path.is_file() and path.suffix.lower() in {".json", ".jsonl", ".md", ".txt"}:
                candidates.append(path)
    return sorted(dict.fromkeys(candidates), key=lambda value: repo_relative(value, root))


def build_repo_state(branch: str = "UNKNOWN", git_status: str = "") -> dict[str, Any]:
    changed: list[str] = []
    untracked: list[str] = []
    for raw_line in git_status.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("## "):
            continue
        path = line[3:].strip() if len(line) > 3 else line
        if line.startswith("?? "):
            untracked.append(path)
        else:
            changed.append(path)
    repo_dirty = bool(changed or untracked)
    return {
        "branch": branch or "UNKNOWN",
        "repo_dirty": repo_dirty,
        "changed_files": changed,
        "untracked_files": untracked,
        "status_summary": "Repo has local changed or untracked files." if repo_dirty else "Repo tree is clean.",
    }


def build_dashboard_cards(bridge_state: dict[str, Any]) -> list[dict[str, Any]]:
    metrics = {
        "wins": bridge_state["wins_count"],
        "blocked": bridge_state["blocked_count"],
        "approval_needed": bridge_state["approval_needed_count"],
        "worker_notes": bridge_state["worker_notes_count"],
    }
    return [
        {
            "title": "Night Supervisor Brief",
            "status": bridge_state["night_supervisor_status"],
            "summary": bridge_state["plain_summary"],
            "metrics": metrics,
            "next_action": bridge_state["next_safe_action"],
            "details_ref": bridge_state["morning_digest_path"],
        }
    ]


def build_bridge_state(repo_root: str | Path, branch: str = "UNKNOWN", git_status: str = "") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    generated_at = utc_now()
    cycle_id = f"autonomy-bridge-{generated_at[:10]}"
    source_files = collect_source_files(root)
    items = [_item_from_path(path, root) for path in source_files]

    completed = [item for item in items if item["status"] == "PASS"]
    blocked = [item for item in items if item["status"] == "BLOCKED"]
    approvals = [item for item in items if item["status"] == "NEEDS_APPROVAL"]
    worker_notes = [item for item in items if item["category"] in {"worker_output", "validator_output", "relay_input"}]
    repo_state = build_repo_state(branch, git_status)

    if blocked:
        status = "BLOCKED"
    elif approvals or repo_state["repo_dirty"]:
        status = "WARN"
    elif completed:
        status = "PASS"
    else:
        status = "UNKNOWN"

    source_count = len(items)
    plain_summary = (
        f"{len(completed)} items completed, {len(blocked)} blocked, "
        f"{len(approvals)} need approval, {source_count} evidence items seen."
    )
    must_see: list[str] = []
    must_see.extend(item["summary"] for item in blocked[:3])
    must_see.extend(item["summary"] for item in approvals[:3])
    if repo_state["repo_dirty"]:
        must_see.append(repo_state["status_summary"])
    if not must_see:
        must_see.append("No blockers found in available bridge evidence; review raw evidence before APPLY.")

    bridge_state: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "cycle_id": cycle_id,
        "source_paths": [repo_relative(path, root) for path in source_files],
        "supervisor_status": status,
        "night_supervisor_status": status,
        "plain_summary": plain_summary,
        "must_see": must_see,
        "relay_items_seen": [item for item in items if item["source_path"].startswith("relay/")],
        "items_completed": completed,
        "items_blocked": blocked,
        "items_needing_approval": approvals,
        "repo_state": repo_state,
        "wins_count": len(completed),
        "blocked_count": len(blocked),
        "approval_needed_count": len(approvals),
        "worker_notes_count": len(worker_notes),
        "next_safe_action": "Review blocked and approval-needed items before any APPLY, commit, push, merge, or worker launch.",
        "dashboard_cards": [],
        "morning_digest_path": OUTPUTS["morning_digest"].as_posix(),
        "raw_evidence": [
            {
                "source_path": item["source_path"],
                "evidence_type": item["category"],
                "status": item["status"],
            }
            for item in items
        ],
        "safety_flags": {
            "no_live_trading": True,
            "no_broker_execution": True,
            "no_oanda": True,
            "no_api_keys": True,
            "no_real_webhooks": True,
            "no_real_orders": True,
            "no_secrets": True,
            "no_commit": True,
            "no_push": True,
            "writes_within_allowed_paths_only": True,
        },
        "authority_boundary": {
            "evidence_only": True,
            "approval_authority": "Anthony Meza",
            "blocked_capabilities": BLOCKED_CAPABILITIES,
        },
    }
    bridge_state["dashboard_cards"] = build_dashboard_cards(bridge_state)
    return bridge_state


def build_markdown_digest(bridge_state: dict[str, Any]) -> str:
    date_key = str(bridge_state["generated_at"])[:10]
    repo = bridge_state["repo_state"]

    def bullet(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- None found."

    def item_lines(items: list[dict[str, Any]]) -> list[str]:
        return [f"{item['title']}: {item['summary']} ({item['source_path']})" for item in items[:8]]

    changed = list(repo.get("changed_files", []))
    untracked = list(repo.get("untracked_files", []))
    lines = [
        f"# Morning Digest - {date_key}",
        "",
        "Status:",
        f"- {bridge_state['night_supervisor_status']}",
        "",
        "Plain summary:",
        f"- {bridge_state['plain_summary']}",
        "",
        "Must See:",
        bullet(list(bridge_state["must_see"])),
        "",
        "Completed Overnight:",
        bullet(item_lines(list(bridge_state["items_completed"]))),
        "",
        "Blocked:",
        bullet(item_lines(list(bridge_state["items_blocked"]))),
        "",
        "Approval Needed:",
        bullet(item_lines(list(bridge_state["items_needing_approval"]))),
        "",
        "Repo State:",
        f"- branch: {repo.get('branch', 'UNKNOWN')}",
        f"- clean/dirty: {'dirty' if repo.get('repo_dirty') else 'clean'}",
        f"- changed files: {', '.join(changed) if changed else 'None'}",
        f"- untracked files: {', '.join(untracked) if untracked else 'None'}",
        "",
        "Next Safe Action:",
        f"- {bridge_state['next_safe_action']}",
        "",
        "Raw Evidence:",
        bullet([item["source_path"] for item in bridge_state["raw_evidence"][:12]]),
        "",
        "Safety:",
        "- No live trading, broker execution, OANDA, API keys, real webhooks, real orders, secrets, commit, or push.",
    ]
    return "\n".join(lines) + "\n"


def planned_output_paths(repo_root: str | Path) -> list[str]:
    root = Path(repo_root).resolve()
    return [repo_relative(root / path, root) for path in OUTPUTS.values()]


def _blocked_output_path(path: Path) -> str | None:
    normalized = path.as_posix().lower()
    for term in FORBIDDEN_PATH_TERMS:
        if term in normalized:
            return term
    return None


def write_outputs(repo_root: str | Path, bridge_state: dict[str, Any], apply: bool = False) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    planned = [root / path for path in OUTPUTS.values()]
    blocked_terms = [term for path in planned if (term := _blocked_output_path(path))]
    if blocked_terms:
        return {
            "mode": "BLOCKED",
            "written": [],
            "planned": [repo_relative(path, root) for path in planned],
            "errors": [f"Forbidden output path term detected: {term}" for term in blocked_terms],
        }
    if not apply:
        return {
            "mode": "DRY_RUN",
            "written": [],
            "planned": [repo_relative(path, root) for path in planned],
            "errors": [],
        }

    written: list[str] = []
    errors: list[str] = []
    outputs = {
        OUTPUTS["bridge_state"]: bridge_state,
        OUTPUTS["morning_state"]: bridge_state,
        OUTPUTS["morning_digest"]: build_markdown_digest(bridge_state),
    }
    for rel_path, content in outputs.items():
        path = root / rel_path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, str):
                path.write_text(content, encoding="utf-8", newline="\n")
            else:
                path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8", newline="\n")
            written.append(repo_relative(path, root))
        except OSError as exc:
            errors.append(f"{repo_relative(path, root)}: {exc}")
    return {
        "mode": "APPLY",
        "written": written,
        "planned": [repo_relative(path, root) for path in planned],
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build AI_OS Autonomy Bridge state.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--repo-branch", default="UNKNOWN", help="Branch captured by the runner.")
    parser.add_argument("--git-status", default="", help="git status --short --branch output captured by the runner.")
    parser.add_argument("--apply", action="store_true", help="Write telemetry outputs. Default is DRY_RUN preview.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON result.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = build_bridge_state(args.repo_root, branch=args.repo_branch, git_status=args.git_status)
    receipt = write_outputs(args.repo_root, state, apply=args.apply)
    result = {
        "schema": "AIOS_AUTONOMY_BRIDGE_RUN_RECEIPT.v1",
        "mode": "APPLY" if args.apply else "DRY_RUN",
        "status": "BLOCKED" if receipt["errors"] else state["night_supervisor_status"],
        "planned_output_paths": receipt["planned"],
        "written_output_paths": receipt["written"],
        "errors": receipt["errors"],
        "bridge_state": state,
    }
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 1 if receipt["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
