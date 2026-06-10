from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "AIOS_GOAL_INTAKE_BRIDGE_PREVIEW.v1"
DEFAULT_FORBIDDEN_ACTIONS = [
    "apply",
    "dispatch",
    "mutate",
    "approve",
    "merge",
    "push",
    "commit",
]
SAFETY_FLAGS = (
    "approvals_performed",
    "approval_inbox_mutated",
    "work_packets_mutated",
    "relay_goals_mutated",
    "relay_inbox_mutated",
    "dispatch_performed",
    "apply_performed",
    "commit_performed",
    "push_performed",
    "merge_performed",
    "live_trading_performed",
    "broker_connection_performed",
    "scheduler_created",
    "service_created",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_output_paths(root: Path | None = None) -> dict[str, Path]:
    base = (root or repo_root()) / "Reports" / "goal_intake"
    return {
        "json": base / "goal_intake_bridge_preview.json",
        "md": base / "goal_intake_bridge_preview.md",
    }


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _safe_slug(value: Any, fallback: str = "goal-proposal") -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in _safe_text(value, fallback))
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or fallback


def _detect_source_type(payload: Any) -> str:
    if payload is None:
        return "no_input"
    if isinstance(payload, list):
        return "candidate_list"
    if not isinstance(payload, dict):
        return "unstructured"

    goals = payload.get("goals")
    candidates = payload.get("candidates")
    evidence_bundle = payload.get("evidence_bundle")
    gap_candidates = evidence_bundle.get("gap_candidates") if isinstance(evidence_bundle, dict) else None
    goal_ids = gap_candidates.get("goal_ids") if isinstance(gap_candidates, dict) else None

    if isinstance(goals, list):
        return "classifier_output"
    if isinstance(candidates, list):
        return "candidate_list"
    if isinstance(goal_ids, list):
        return "self_build_evidence"
    if any(key in payload for key in ("goal_id", "id", "title", "summary", "reason")):
        return "single_candidate"
    return "unstructured"


def _claimed_candidate_count(payload: Any) -> int:
    if payload is None:
        return 0
    if isinstance(payload, list):
        return len(payload)
    if not isinstance(payload, dict):
        return 0

    counts = []
    candidate_count = payload.get("candidate_count")
    if isinstance(candidate_count, int) and candidate_count >= 0:
        counts.append(candidate_count)

    goals = payload.get("goals")
    if isinstance(goals, list):
        counts.append(len(goals))

    candidates = payload.get("candidates")
    if isinstance(candidates, list):
        counts.append(len(candidates))

    evidence_bundle = payload.get("evidence_bundle")
    gap_candidates = evidence_bundle.get("gap_candidates") if isinstance(evidence_bundle, dict) else None
    if isinstance(gap_candidates, dict):
        gap_count = gap_candidates.get("candidate_count")
        if isinstance(gap_count, int) and gap_count >= 0:
            counts.append(gap_count)
        goal_ids = gap_candidates.get("goal_ids")
        if isinstance(goal_ids, list):
            counts.append(len(goal_ids))

    return max(counts) if counts else 0


def _extract_candidates_from_payload(payload: Any) -> tuple[list[dict[str, Any]], str]:
    source_type = _detect_source_type(payload)
    candidates: list[dict[str, Any]] = []

    if payload is None:
        return candidates, source_type

    if isinstance(payload, list):
        source = "candidate_list"
        for index, item in enumerate(payload):
            if isinstance(item, dict):
                candidate = dict(item)
            else:
                candidate = {
                    "goal_id": _safe_text(item, f"goal-{index + 1}"),
                    "title": _safe_text(item, f"Candidate {index + 1}"),
                    "summary": "Candidate supplied as a non-dict value.",
                }
            candidate["_source_bucket"] = source
            candidate["_source_index"] = index
            candidates.append(candidate)
        return candidates, source

    if not isinstance(payload, dict):
        return candidates, source_type

    if isinstance(payload.get("goals"), list):
        source = "classifier_output"
        for index, item in enumerate(payload["goals"]):
            candidate = dict(item) if isinstance(item, dict) else {
                "goal_id": _safe_text(item, f"goal-{index + 1}"),
                "title": _safe_text(item, f"Goal {index + 1}"),
            }
            candidate["_source_bucket"] = source
            candidate["_source_index"] = index
            candidates.append(candidate)
        return candidates, source

    if isinstance(payload.get("candidates"), list):
        source = "candidate_list"
        for index, item in enumerate(payload["candidates"]):
            candidate = dict(item) if isinstance(item, dict) else {
                "goal_id": _safe_text(item, f"goal-{index + 1}"),
                "title": _safe_text(item, f"Candidate {index + 1}"),
            }
            candidate["_source_bucket"] = source
            candidate["_source_index"] = index
            candidates.append(candidate)
        return candidates, source

    evidence_bundle = payload.get("evidence_bundle")
    gap_candidates = evidence_bundle.get("gap_candidates") if isinstance(evidence_bundle, dict) else None
    goal_ids = gap_candidates.get("goal_ids") if isinstance(gap_candidates, dict) else None
    if isinstance(goal_ids, list):
        seen: set[str] = set()
        source = "self_build_evidence"
        for index, item in enumerate(goal_ids):
            goal_id = _safe_text(item, f"goal-{index + 1}")
            if goal_id in seen:
                continue
            seen.add(goal_id)
            candidates.append(
                {
                    "goal_id": goal_id,
                    "title": f"Goal candidate {goal_id}",
                    "summary": "Derived from self-build evidence gap_candidates.goal_ids.",
                    "_source_bucket": source,
                    "_source_index": index,
                }
            )
        return candidates, source

    if any(key in payload for key in ("goal_id", "id", "title", "summary", "reason")):
        candidate = dict(payload)
        candidate["_source_bucket"] = "single_candidate"
        candidate["_source_index"] = 0
        candidates.append(candidate)
        return candidates, "single_candidate"

    return candidates, source_type


def _risk_level(candidate: dict[str, Any]) -> str:
    explicit = _safe_text(
        candidate.get("risk_level") or candidate.get("risk") or candidate.get("urgency"),
        "",
    ).upper()
    protected = bool(candidate.get("protected_action_expected"))
    if explicit in {"LOW", "GREEN", "READ_ONLY", "READ-ONLY", "SAFE"} and not protected:
        return "LOW"
    return "REVIEW_REQUIRED"


def _provenance(candidate: dict[str, Any], source_path: str | None) -> dict[str, Any]:
    keys = sorted(
        key for key in candidate.keys()
        if not str(key).startswith("_")
    )
    return {
        "source_type": candidate.get("_source_bucket", "candidate_list"),
        "source_path": source_path,
        "source_index": candidate.get("_source_index", 0),
        "source_schema": candidate.get("schema"),
        "source_keys": keys,
    }


def _normalize_candidate(candidate: dict[str, Any], index: int, source_path: str | None) -> dict[str, Any]:
    source_goal_id = _safe_text(
        candidate.get("goal_id") or candidate.get("id") or candidate.get("source_goal_id"),
        f"goal-{index + 1}",
    )
    title = _safe_text(
        candidate.get("title")
        or candidate.get("objective")
        or candidate.get("name")
        or candidate.get("label"),
        f"Goal candidate {index + 1}",
    )
    summary = _safe_text(
        candidate.get("summary")
        or candidate.get("description")
        or candidate.get("notes"),
        "",
    )
    reason = _safe_text(
        candidate.get("reason")
        or candidate.get("why")
        or candidate.get("source_gap")
        or candidate.get("gap")
        or summary,
        "Source candidate requires human review.",
    )

    if not summary:
        summary = "Minimal proposal derived from source goal identifier only."
        reason = "Source payload did not include enough detail to normalize a richer proposal."

    priority = candidate.get("priority") or candidate.get("rank") or candidate.get("urgency")
    if priority is not None:
        priority = _safe_text(priority, "")

    risk_level = _risk_level(candidate)
    recommended_lane = "PROPOSAL_REVIEW" if risk_level == "LOW" else "HUMAN_REVIEW"

    return {
        "proposal_id": f"goal-proposal-{_safe_slug(source_goal_id or title or index + 1)}",
        "source_goal_id": source_goal_id,
        "title": title,
        "summary": summary,
        "reason": reason,
        "priority": priority,
        "risk_level": risk_level,
        "recommended_lane": recommended_lane,
        "requires_human_review": True,
        "allowed_next_step": "Review proposal and decide whether to draft a governed packet.",
        "forbidden_actions": DEFAULT_FORBIDDEN_ACTIONS,
        "provenance": _provenance(candidate, source_path),
    }


def _safety_block() -> dict[str, str]:
    return {flag: "NO" for flag in SAFETY_FLAGS}


def _next_safe_action(status: str, has_proposals: bool, candidate_count: int) -> str:
    if status == "BLOCKED_MALFORMED_INPUT":
        return "Fix the malformed JSON input and rerun the goal-intake bridge."
    if status == "NO_INPUT":
        return "Provide inventory or classifier output to generate goal proposals."
    if candidate_count > 0 and not has_proposals:
        return "Provide goal IDs, titles, or classifier output so proposals can be normalized."
    if candidate_count > has_proposals:
        return "Review partial proposals and supply the missing goal details before drafting packets."
    if has_proposals:
        return "Review proposals and decide whether to draft a governed packet."
    return "Provide inventory or classifier output to generate goal proposals."


def build_goal_proposals(candidates: list[dict[str, Any]], source_path: str | None) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        normalized.append(_normalize_candidate(candidate, index, source_path))

    source_type = candidates[0].get("_source_bucket", "candidate_list") if candidates else "no_input"
    candidate_count = len(candidates)
    proposal_count = len(normalized)
    status = "OK" if proposal_count else "NO_INPUT"
    preview = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "mode": "DRY_RUN",
        "observe_only": True,
        "report_only": True,
        "status": status,
        "source_type": source_type,
        "source_path": source_path,
        "candidate_count": candidate_count,
        "proposal_count": proposal_count,
        "proposals": normalized,
        "safety": _safety_block(),
    }
    preview["next_safe_action"] = _next_safe_action(status, bool(normalized), candidate_count)
    preview.update(preview["safety"])
    return preview


def build_goal_intake_preview(payload: Any, source_path: str | None = None, source_type: str | None = None) -> dict[str, Any]:
    candidates, detected_source = _extract_candidates_from_payload(payload)
    claimed_count = _claimed_candidate_count(payload)
    preview = build_goal_proposals(candidates, source_path)

    preview["source_type"] = source_type or detected_source
    preview["candidate_count"] = max(int(preview["candidate_count"]), int(claimed_count))
    preview["proposal_count"] = len(preview["proposals"])

    if payload is None:
        preview["status"] = "NO_INPUT"
        preview["next_safe_action"] = _next_safe_action("NO_INPUT", False, 0)
    elif source_type == "malformed_json":
        preview["status"] = "BLOCKED_MALFORMED_INPUT"
        preview["next_safe_action"] = _next_safe_action("BLOCKED_MALFORMED_INPUT", False, preview["candidate_count"])
    elif preview["proposal_count"] == 0 and preview["candidate_count"] > 0:
        preview["status"] = "PARTIAL"
        preview["next_safe_action"] = _next_safe_action("PARTIAL", False, preview["candidate_count"])
    elif preview["proposal_count"] == 0:
        preview["status"] = "NO_INPUT" if payload is None else "EMPTY_INPUT"
        preview["next_safe_action"] = _next_safe_action(preview["status"], False, preview["candidate_count"])
    else:
        preview["status"] = "OK"
        preview["next_safe_action"] = _next_safe_action("OK", True, preview["candidate_count"])

    return preview


def _atomic_write_text(path: Path, text: str, overwrite: bool) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        return "SKIPPED_EXISTS"

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent), prefix=f".{path.name}.") as handle:
        handle.write(text)
        temp_path = Path(handle.name)

    temp_path.replace(path)
    return "WRITTEN"


def _render_markdown(preview: dict[str, Any]) -> str:
    lines = [
        "# AIOS Goal Intake Bridge Preview",
        "",
        f"- schema: `{preview['schema']}`",
        f"- generated_at: `{preview['generated_at']}`",
        f"- mode: `{preview['mode']}`",
        f"- observe_only: `{preview['observe_only']}`",
        f"- status: `{preview['status']}`",
        f"- source_type: `{preview['source_type']}`",
        f"- source_path: `{preview['source_path']}`",
        f"- candidate_count: `{preview['candidate_count']}`",
        f"- proposal_count: `{preview['proposal_count']}`",
        "",
        "## Proposals",
    ]

    if preview["proposals"]:
        lines.extend(
            [
                "",
                "| proposal_id | source_goal_id | title | risk_level | recommended_lane | requires_human_review |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for proposal in preview["proposals"]:
            lines.append(
                "| {proposal_id} | {source_goal_id} | {title} | {risk_level} | {recommended_lane} | {requires_human_review} |".format(
                    proposal_id=proposal["proposal_id"],
                    source_goal_id=proposal["source_goal_id"],
                    title=proposal["title"].replace("|", "\\|"),
                    risk_level=proposal["risk_level"],
                    recommended_lane=proposal["recommended_lane"],
                    requires_human_review=proposal["requires_human_review"],
                )
            )
    else:
        lines.extend(["", "_No proposals normalized._"])

    lines.extend(
        [
            "",
            "## Safety",
        ]
    )
    for key, value in preview["safety"].items():
        lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Next Safe Action",
            "",
            preview["next_safe_action"],
            "",
        ]
    )
    return "\n".join(lines)


def write_preview(payload: dict[str, Any], output_json: Path | None, output_md: Path | None, overwrite: bool = False) -> dict[str, Any]:
    result = {
        "json_status": "SKIPPED",
        "md_status": "SKIPPED",
        "output_json": str(output_json) if output_json else None,
        "output_md": str(output_md) if output_md else None,
    }
    if output_json is not None:
        result["json_status"] = _atomic_write_text(output_json, json.dumps(payload, indent=2, sort_keys=False) + "\n", overwrite)
    if output_md is not None:
        result["md_status"] = _atomic_write_text(output_md, _render_markdown(payload), overwrite)
    return result


def _stdout_preview(preview: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(preview, indent=2, sort_keys=False))
    sys.stdout.write("\n")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI_OS goal intake bridge preview (observe-only).")
    parser.add_argument("--input", type=Path, help="Path to classifier or evidence JSON input.", default=None)
    parser.add_argument("--output-json", type=Path, help="Write preview JSON to this path.", default=None)
    parser.add_argument("--output-md", type=Path, help="Write preview markdown to this path.", default=None)
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing output files.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    exit_code = 0
    payload: Any = None
    source_type: str | None = None

    if args.input is not None:
        try:
            payload = load_json(args.input)
            source_type = _detect_source_type(payload)
        except FileNotFoundError:
            payload = None
            source_type = "missing_input"
            exit_code = 3
        except json.JSONDecodeError as exc:
            payload = None
            source_type = "malformed_json"
            exit_code = 3
            malformed_note = f"{exc.msg} at line {exc.lineno} column {exc.colno}"
        except Exception as exc:  # defensive fallback for unexpected read failures
            payload = None
            source_type = "malformed_json"
            exit_code = 3
            malformed_note = str(exc)
    else:
        malformed_note = None

    if payload is None and args.input is not None and source_type == "malformed_json":
        preview = build_goal_intake_preview(None, source_path=str(args.input), source_type="malformed_json")
        preview["status"] = "BLOCKED_MALFORMED_INPUT"
        preview["next_safe_action"] = _next_safe_action("BLOCKED_MALFORMED_INPUT", False, 0)
        preview["reasons"] = [malformed_note] if malformed_note else ["Malformed JSON input."]
    elif payload is None and args.input is not None and source_type == "missing_input":
        preview = build_goal_intake_preview(None, source_path=str(args.input), source_type="missing_input")
        preview["status"] = "BLOCKED_MISSING_INPUT"
        preview["next_safe_action"] = "Provide the missing input file or rerun without --input."
        preview["reasons"] = [f"Missing input file: {args.input}"]
    else:
        preview = build_goal_intake_preview(payload, source_path=str(args.input) if args.input else None, source_type=source_type)

    if args.output_json is not None or args.output_md is not None:
        write_preview(preview, args.output_json, args.output_md, overwrite=args.overwrite)

    _stdout_preview(preview)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
