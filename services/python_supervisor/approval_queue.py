"""AI_OS Night Supervisor approval queue projection.

Reads local Relay approval evidence and builds a dashboard-safe operator review
queue. This module is standard-library-only and projection-only. It does not
run shell commands, call the network, mutate approvals, stage files, commit,
push, merge, open PRs, touch secrets, or enable live trading.
"""

from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_NIGHT_SUPERVISOR_APPROVAL_QUEUE.v1"
OUTPUTS = {
    "queue_state": Path("telemetry/night_supervisor/APPROVAL_QUEUE_STATE.json"),
    "summary": Path("telemetry/morning_digest/APPROVAL_QUEUE_SUMMARY.md"),
}
STATUS_VALUES = (
    "WAITING_REVIEW",
    "APPROVED",
    "REJECTED",
    "STALE",
    "UNSAFE_BLOCKED",
    "ALREADY_HANDLED",
    "NEEDS_MORE_CONTEXT",
    "UNKNOWN",
)
RISK_VALUES = ("LOW", "MEDIUM", "HIGH", "BLOCKED", "UNKNOWN")
UNSAFE_TERMS = (
    "live trading",
    "live now",
    "broker",
    "oanda",
    "api key",
    "api_key",
    "webhook",
    "real order",
    "buy order",
    "sell order",
    "place a buy",
    "place a sell",
    "secret",
    "credential",
)
PROTECTED_REVIEW_TERMS = (
    "commit",
    "push",
    "merge",
    "pull request",
    "open pr",
    "pr creation",
    "git add",
    "git commit",
)
TEMPLATE_TERMS = ("example", "template", "sample", ".keep")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def read_text_safely(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def read_json_safely(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def compact_text(value: str, limit: int = 240) -> str:
    return " ".join(value.split())[:limit]


def get_repo_status(repo_root: str | Path, branch: str = "UNKNOWN", git_status: str = "") -> dict[str, Any]:
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
    return {
        "branch": branch or "UNKNOWN",
        "repo_dirty": bool(changed or untracked),
        "changed_files": changed,
        "untracked_files": untracked,
        "status_summary": "Repo has local changed or untracked files." if changed or untracked else "Repo tree is clean.",
    }


def list_approval_files(repo_root: str | Path) -> list[Path]:
    root = Path(repo_root).resolve()
    approvals_root = root / "relay" / "approvals"
    if not approvals_root.exists():
        return []
    files = [
        path
        for path in approvals_root.rglob("*")
        if path.is_file() and path.name.lower() != ".keep" and path.suffix.lower() in {".json", ".md", ".txt"}
    ]
    return sorted(files, key=lambda path: repo_relative(path, root))


def _folder_projection(path: Path) -> str | None:
    normalized = path.as_posix().lower()
    if "/approvals/approved/" in normalized:
        return "APPROVED"
    if "/approvals/rejected/" in normalized:
        return "REJECTED"
    return None


def _extract_title(path: Path, payload: dict[str, Any], text: str) -> str:
    if payload.get("title"):
        return str(payload["title"])
    first_line = next((line.strip("# ").strip() for line in text.splitlines() if line.strip()), "")
    return first_line or path.stem.replace("_", " ").replace("-", " ").title()


def _extract_requested_action(path: Path, payload: dict[str, Any], text: str) -> str:
    for key in ("requested_action", "proposed", "request_type", "needs"):
        if payload.get(key):
            return compact_text(str(payload[key]), 160)
    lowered = text.lower()
    if any(term in lowered for term in ("buy order", "sell order", "real order")):
        return "Unsafe live-order-style request"
    if "git add" in lowered or "git commit" in lowered:
        return "Git stage/commit request"
    if "push" in lowered:
        return "Git push request"
    if "merge" in lowered:
        return "Git merge request"
    return "Review approval evidence"


def _extract_risk(text: str, payload: dict[str, Any]) -> str:
    raw = str(payload.get("risk_level", "") or payload.get("risk", "")).upper()
    source = f"{raw} {text}".lower()
    if "risk level:** blocker" in source or "blocker" in source:
        return "BLOCKED"
    if "high" in source:
        return "HIGH"
    if "medium" in source:
        return "MEDIUM"
    if "low" in source:
        return "LOW"
    return "UNKNOWN"


def _status_reason(status: str, text: str, repo_status: dict[str, Any], folder_status: str | None) -> str:
    clean = not repo_status.get("repo_dirty", False)
    if status == "UNSAFE_BLOCKED":
        return "Approval evidence contains live trading, broker, webhook, API key, real order, or secret language."
    if status == "STALE" and clean:
        return "Approval refers to a dirty repo state, but current git status is clean."
    if status == "ALREADY_HANDLED":
        return "Approval is in the approved folder and current evidence suggests the requested source action has already been handled."
    if status == "APPROVED" or folder_status == "APPROVED":
        return "Approval evidence is filed under relay/approvals/approved/."
    if status == "REJECTED" or folder_status == "REJECTED":
        return "Approval evidence is filed under relay/approvals/rejected/."
    if status == "NEEDS_MORE_CONTEXT":
        return "Approval appears to be an example or template-like item, not active approval authority."
    if status == "WAITING_REVIEW":
        return "Protected action requires Anthony review before any APPLY, commit, push, merge, PR, or worker launch."
    return "Approval state could not be determined safely from available evidence."


def _recommended_action(status: str) -> str:
    return {
        "WAITING_REVIEW": "Anthony reviews the request and decides whether to create a separate exact APPLY or commit packet.",
        "APPROVED": "Keep as approval evidence; do not mutate Relay folders from this projection.",
        "REJECTED": "No action unless Anthony reopens the request in a separate packet.",
        "STALE": "Treat as historical runtime evidence; do not act on it without a fresh approval request.",
        "UNSAFE_BLOCKED": "Leave blocked. Do not approve into execution.",
        "ALREADY_HANDLED": "Leave as evidence and continue with source-only commit preparation if separately approved.",
        "NEEDS_MORE_CONTEXT": "Review whether this should become a source-controlled template in a separate promotion pack.",
        "UNKNOWN": "Inspect the source evidence before taking any protected action.",
    }[status]


def classify_approval_file(path: Path, repo_status: dict[str, Any], repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve() if repo_root else path.parents[0]
    rel = repo_relative(path, root)
    text = read_text_safely(path)
    payload = read_json_safely(path) if path.suffix.lower() == ".json" else {}
    combined = f"{path.name} {json.dumps(payload, sort_keys=True)} {text}".lower()
    folder_status = _folder_projection(path)
    status = folder_status or "WAITING_REVIEW"

    if any(term in combined for term in UNSAFE_TERMS):
        status = "UNSAFE_BLOCKED"
    elif "dirty-repo" in combined and not repo_status.get("changed_files"):
        status = "STALE"
    elif any(term in path.name.lower() for term in TEMPLATE_TERMS) or "example approval" in combined:
        status = "NEEDS_MORE_CONTEXT"
    elif folder_status == "APPROVED" and any(term in combined for term in PROTECTED_REVIEW_TERMS):
        status = "ALREADY_HANDLED"
    elif any(term in combined for term in PROTECTED_REVIEW_TERMS):
        status = "WAITING_REVIEW"
    elif not text and not payload:
        status = "UNKNOWN"

    risk = _extract_risk(text, payload)
    if status == "UNSAFE_BLOCKED":
        risk = "BLOCKED"
    elif status == "STALE" and risk == "UNKNOWN":
        risk = "BLOCKED"

    item = {
        "id": str(payload.get("id") or path.stem),
        "source_path": rel,
        "title": _extract_title(path, payload, text),
        "requested_action": _extract_requested_action(path, payload, text),
        "risk_level": risk if risk in RISK_VALUES else "UNKNOWN",
        "status": status if status in STATUS_VALUES else "UNKNOWN",
        "reason": _status_reason(status, combined, repo_status, folder_status),
        "evidence_refs": [rel],
        "recommended_operator_action": _recommended_action(status if status in STATUS_VALUES else "UNKNOWN"),
    }
    return item


def _approval_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status.lower(): 0 for status in STATUS_VALUES}
    counts["total"] = len(items)
    for item in items:
        key = str(item.get("status", "UNKNOWN")).lower()
        counts[key] = counts.get(key, 0) + 1
    if counts.get("already_handled", 0):
        counts["approved"] += counts["already_handled"]
    return counts


def build_dashboard_card(queue_state: dict[str, Any]) -> dict[str, Any]:
    counts = queue_state["approval_counts"]
    status = "BLOCKED" if counts["unsafe_blocked"] else "WARN" if counts["waiting_review"] or counts["stale"] else "PASS"
    return {
        "title": "Approval Queue",
        "status": status,
        "waiting_count": counts["waiting_review"],
        "stale_count": counts["stale"],
        "unsafe_blocked_count": counts["unsafe_blocked"],
        "approved_count": counts["approved"],
        "rejected_count": counts["rejected"],
        "next_safe_action": queue_state["next_safe_action"],
        "details_ref": OUTPUTS["summary"].as_posix(),
    }


def build_approval_queue(repo_root: str | Path, branch: str = "UNKNOWN", git_status: str = "") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    generated_at = utc_now()
    repo_status = get_repo_status(root, branch=branch, git_status=git_status)
    files = list_approval_files(root)
    items = [classify_approval_file(path, repo_status, root) for path in files]
    counts = _approval_counts(items)
    next_safe_action = (
        "Review unsafe and waiting approval items before any APPLY, commit, push, merge, PR, or worker launch."
        if counts["unsafe_blocked"] or counts["waiting_review"]
        else "Review stale or context-needed approval evidence before relying on overnight status."
    )
    state: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "queue_id": f"night-supervisor-approval-queue-{generated_at[:10]}",
        "repo_status": repo_status,
        "approval_counts": counts,
        "approval_items": items,
        "stale_items": [item for item in items if item["status"] == "STALE"],
        "unsafe_items": [item for item in items if item["status"] == "UNSAFE_BLOCKED"],
        "next_safe_action": next_safe_action,
        "dashboard_cards": [],
        "raw_evidence_refs": [item["source_path"] for item in items],
        "safety_flags": {
            "projection_only": True,
            "does_not_mutate_approvals": True,
            "no_live_trading": True,
            "no_broker_execution": True,
            "no_oanda": True,
            "no_api_keys": True,
            "no_real_webhooks": True,
            "no_real_orders": True,
            "no_secrets": True,
            "no_stage": True,
            "no_commit": True,
            "no_push": True,
            "no_merge": True,
            "no_pr": True,
        },
    }
    state["dashboard_cards"] = [build_dashboard_card(state)]
    return state


def build_markdown_summary(queue_state: dict[str, Any]) -> str:
    counts = queue_state["approval_counts"]

    def lines_for(status: str) -> list[str]:
        rows = [item for item in queue_state["approval_items"] if item["status"] == status]
        return [f"- {item['title']}: {item['recommended_operator_action']} ({item['source_path']})" for item in rows] or ["- None found."]

    lines = [
        f"# Approval Queue Summary - {queue_state['generated_at'][:10]}",
        "",
        "Status:",
        f"- {'BLOCKED' if counts['unsafe_blocked'] else 'WARN' if counts['waiting_review'] or counts['stale'] else 'PASS'}",
        "",
        "Counts:",
        f"- waiting review: {counts['waiting_review']}",
        f"- stale: {counts['stale']}",
        f"- unsafe blocked: {counts['unsafe_blocked']}",
        f"- approved: {counts['approved']}",
        f"- rejected: {counts['rejected']}",
        f"- needs more context: {counts['needs_more_context']}",
        "",
        "Unsafe Blocked:",
        *lines_for("UNSAFE_BLOCKED"),
        "",
        "Waiting Review:",
        *lines_for("WAITING_REVIEW"),
        "",
        "Stale:",
        *lines_for("STALE"),
        "",
        "Next Safe Action:",
        f"- {queue_state['next_safe_action']}",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(repo_root: str | Path, queue_state: dict[str, Any], apply: bool = False) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    planned = [root / path for path in OUTPUTS.values()]
    if not apply:
        return {"mode": "DRY_RUN", "planned": [repo_relative(path, root) for path in planned], "written": [], "errors": []}
    outputs: dict[Path, Any] = {
        OUTPUTS["queue_state"]: queue_state,
        OUTPUTS["summary"]: build_markdown_summary(queue_state),
    }
    written: list[str] = []
    errors: list[str] = []
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
    return {"mode": "APPLY", "planned": [repo_relative(path, root) for path in planned], "written": written, "errors": errors}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build AI_OS Night Supervisor approval queue projection.")
    parser.add_argument("--repo-root", default=".", help="Repository root.")
    parser.add_argument("--repo-branch", default="UNKNOWN", help="Branch captured by the runner.")
    parser.add_argument("--git-status", default="", help="git status --short --branch output captured by the runner.")
    parser.add_argument("--git-status-base64", default="", help="Base64-encoded git status output captured by the runner.")
    parser.add_argument("--apply", action="store_true", help="Write generated queue state. Default is DRY_RUN.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON result.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    git_status = args.git_status
    if args.git_status_base64:
        try:
            git_status = base64.b64decode(args.git_status_base64).decode("utf-8", errors="replace")
        except ValueError:
            git_status = args.git_status
    state = build_approval_queue(args.repo_root, branch=args.repo_branch, git_status=git_status)
    receipt = write_outputs(args.repo_root, state, apply=args.apply)
    status = "BLOCKED" if receipt["errors"] else state["dashboard_cards"][0]["status"]
    result = {
        "schema": "AIOS_NIGHT_SUPERVISOR_APPROVAL_QUEUE_RUN_RECEIPT.v1",
        "mode": "APPLY" if args.apply else "DRY_RUN",
        "status": status,
        "planned_output_paths": receipt["planned"],
        "written_output_paths": receipt["written"],
        "errors": receipt["errors"],
        "queue_state": state,
    }
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 1 if receipt["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
