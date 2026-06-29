"""Deterministic Forex 110 vacation-grade truth engine.

This module is evidence-scanning only. It does not read environment variables,
credentials, broker accounts, network resources, or runtime processes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "aios.forex_110_vacation_grade_profit_engine.v1"
PACKET_ID = "PKT-FOREX-110-VACATION-GRADE-PROFIT-ENGINE-V1"

PROVEN = "PROVEN"
PARTIAL = "PARTIAL"
NOT_PROVEN = "NOT_PROVEN"
BLOCKED = "BLOCKED"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
READINESS_VALUES = {PROVEN, PARTIAL, NOT_PROVEN, BLOCKED, REVIEW_REQUIRED}

OWNER_CORRECTED_DEFINITION = (
    "FOREX 110 means vacation-grade Forex readiness: the owner could "
    "eventually deposit real money, step away, and return to an "
    "evidence-backed expected profit outcome, while AIOS operates under "
    "strict risk controls, broker gates, audit logs, kill switches, and "
    "owner-approved escalation boundaries."
)
FOREX_110_DEFINITION = (
    "Forex 110 is not repo polish, dashboard polish, or theoretical "
    "readiness. Forex 110 means real-money-capable readiness after proof, "
    "safety, and owner approval, or the shortest exact packet chain required "
    "to reach that standard."
)
VACATION_GRADE_DEFINITION = (
    "Vacation-grade readiness requires persistent profitability proof, "
    "validated good-day return target of 25% to 100%, validated excellent / "
    "phenomenal-day target up to 120%, broker-read-only evidence, demo "
    "execution readiness, real-money gates, 22H/day 6D/week runtime "
    "readiness, risk controls, dashboard truth, auditability, and owner "
    "approval before real-money execution."
)

EVIDENCE_ROOTS = (
    "automation/forex_engine",
    "scripts/forex_delivery",
    "tests/forex_engine",
    "docs/trading_lab/forex",
    "Reports/forex_delivery",
    "apps/dashboard",
    "apps/trading_lab",
    "schemas",
)

SENSITIVE_NAME_FRAGMENTS = (
    ".env",
    "secret",
    "token",
    "password",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "private_key",
)

BLOCKED_ACTIONS = {
    "env_read": True,
    "credential_read": True,
    "broker_contact": True,
    "broker_account_inspection": True,
    "order_execution": True,
    "demo_trade_start": True,
    "live_trade_start": True,
    "scheduler_start": True,
    "daemon_start": True,
    "webhook_start": True,
    "background_loop_start": True,
    "server_start": True,
    "tunnel_start": True,
    "deployment": True,
    "bitwarden_start": True,
    "vaultwarden_start": True,
    "fake_profit_claim": True,
    "fake_return_expectancy_claim": True,
    "fake_vacation_grade_claim": True,
}

CRITICAL_PROVEN_FIELDS = (
    "profitability_status",
    "good_day_return_target_status",
    "phenomenal_day_return_target_status",
    "twenty_two_hour_six_day_status",
    "broker_readonly_evidence_status",
    "demo_execution_status",
    "live_real_money_status",
    "risk_control_status",
    "dashboard_truth_status",
)


def run_forex_110_vacation_grade_profit_engine_v1(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    evidence = scan_repo_evidence(root)

    statuses = {
        "profitability_status": _profitability_status(evidence),
        "good_day_return_target_status": _return_target_status(evidence, "good_day"),
        "phenomenal_day_return_target_status": _return_target_status(
            evidence, "phenomenal_day"
        ),
        "twenty_two_hour_six_day_status": _runtime_status(evidence),
        "broker_readonly_evidence_status": _broker_readonly_status(evidence),
        "demo_execution_status": _demo_status(evidence),
        "live_real_money_status": _live_real_money_status(evidence),
        "risk_control_status": _risk_control_status(evidence),
        "dashboard_truth_status": _dashboard_truth_status(evidence),
    }
    vacation_grade_status = (
        PROVEN
        if all(statuses[field] == PROVEN for field in CRITICAL_PROVEN_FIELDS)
        else BLOCKED
    )

    five_lane_completion_map = _five_lane_completion_map(evidence, statuses)
    state = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "owner_corrected_definition": OWNER_CORRECTED_DEFINITION,
        "forex_110_definition": FOREX_110_DEFINITION,
        "vacation_grade_definition": VACATION_GRADE_DEFINITION,
        "one_man_operator_mode": {
            "status": REVIEW_REQUIRED,
            "lanes": [lane["lane_name"] for lane in five_lane_completion_map],
            "rule": "Exactly five lanes; no corporate sprawl; owner approval gates remain required.",
        },
        "current_truth_summary": _current_truth_summary(statuses, vacation_grade_status),
        "vacation_grade_status": vacation_grade_status,
        **statuses,
        "already_built": evidence["already_built"],
        "actually_proven": _actually_proven(statuses),
        "not_yet_proven": _not_yet_proven(statuses),
        "five_lane_completion_map": five_lane_completion_map,
        "blockers_by_lane": {
            lane["lane_name"]: lane["blockers"] for lane in five_lane_completion_map
        },
        "required_evidence_by_lane": {
            lane["lane_name"]: lane["evidence_missing"]
            for lane in five_lane_completion_map
        },
        "shortest_packet_chain": _shortest_packet_chain(),
        "next_best_packet": _shortest_packet_chain()[0],
        "blocked_actions": dict(BLOCKED_ACTIONS),
        "safe_next_action": (
            "Run Profit Evidence Truth Lock next. Do not trade, do not start "
            "demo/live execution, do not contact broker APIs, and do not claim "
            "vacation-grade readiness until evidence closes all blockers."
        ),
    }
    _assert_readiness_values(state)
    return state


def scan_repo_evidence(repo_root: Path) -> dict[str, Any]:
    files = sorted(_iter_evidence_files(repo_root), key=lambda path: path.as_posix())
    relative_files = [_rel(repo_root, path) for path in files]
    selected_text = _read_selected_text(repo_root, files)
    normalized_text = selected_text.lower()

    return {
        "scanned_roots": list(EVIDENCE_ROOTS),
        "file_count": len(relative_files),
        "selected_text_size": len(selected_text),
        "already_built": _already_built(relative_files),
        "paths": relative_files,
        "text": normalized_text,
        "evidence_found": {
            "real_completion_refocus": _exists(
                relative_files,
                "docs/trading_lab/forex/FOREX_110_REAL_COMPLETION_REFOCUS_V1.md",
            ),
            "vacation_mode_decision": _contains_path(
                relative_files, "VACATION_MODE_FINAL_READINESS_DECISION"
            ),
            "statistical_profit_gate": _contains_path(
                relative_files, "STATISTICAL_PROFIT_PROOF_GATE"
            ),
            "walk_forward_oos": _contains_path(relative_files, "WALKFORWARD")
            or _contains_path(relative_files, "WALK_FORWARD"),
            "broker_readonly": _contains_path(relative_files, "BROKER")
            and _contains_path(relative_files, "READ"),
            "runtime_22h6d": _contains_any(
                relative_files,
                ("22H6D", "22_6", "UPTIME_RANGE", "TRUSTED_PROFIT_22_6"),
            ),
            "risk_controls": _contains_any(
                relative_files,
                ("KILL_SWITCH", "MAX_LOSS", "DAILY_STOP", "RISK"),
            ),
            "dashboard_truth": _contains_path(relative_files, "DASHBOARD_TRUTH")
            or "dashboard truth" in normalized_text,
            "owner_approval_gate": "owner approval" in normalized_text,
            "auditability": _contains_any(relative_files, ("EVIDENCE", "LEDGER", "AUDIT")),
        },
        "explicit_not_proven_signals": {
            "profitability": "persistent_profitability_status\": \"not_proven"
            in normalized_text
            or "profitability claim: `not_proven`" in normalized_text,
            "return_targets": "return expectancy claim: `not_proven`"
            in normalized_text
            or "25% to 100%" not in normalized_text,
            "runtime_22h6d": "22h/6d readiness: `not_proven`" in normalized_text
            or "twenty_two_hour_six_day_status\": \"not_proven" in normalized_text,
            "live": "live execution: `blocked`" in normalized_text
            or "live_execution_status\": \"blocked" in normalized_text,
            "risk": "risk_control_status\": \"blocked" in normalized_text
            or "safety/risk final gate: `blocked`" in normalized_text,
        },
    }


def build_report_markdown(state: dict[str, Any]) -> str:
    lanes = state["five_lane_completion_map"]
    chain = state["shortest_packet_chain"]
    operator = _one_man_operator_view(state)
    lines = [
        "# AIOS Forex 110 Vacation-Grade Profit Engine V1",
        "",
        f"- Packet ID: `{state['packet_id']}`",
        f"- Schema version: `{state['schema_version']}`",
        f"- Vacation-grade status: `{state['vacation_grade_status']}`",
        f"- Profitability status: `{state['profitability_status']}`",
        f"- Good day return target status: `{state['good_day_return_target_status']}`",
        f"- Phenomenal day return target status: `{state['phenomenal_day_return_target_status']}`",
        f"- 22H/day 6D/week status: `{state['twenty_two_hour_six_day_status']}`",
        f"- Broker-read-only evidence status: `{state['broker_readonly_evidence_status']}`",
        f"- Demo execution status: `{state['demo_execution_status']}`",
        f"- Live real-money status: `{state['live_real_money_status']}`",
        f"- Risk control status: `{state['risk_control_status']}`",
        f"- Dashboard truth status: `{state['dashboard_truth_status']}`",
        "",
        "## Owner-Corrected Forex 110 Definition",
        state["owner_corrected_definition"],
        "",
        "## Vacation-Grade Readiness Definition",
        state["vacation_grade_definition"],
        "",
        "## Exact Return Target Language",
        "- Good day: 25% to 100%",
        "- Excellent / phenomenal day: up to 120%",
        "",
        "## Current Truth Summary",
        state["current_truth_summary"],
        "",
        "## Five-Lane Completion Map",
    ]
    for lane in lanes:
        lines.extend(
            [
                f"### {lane['lane_name']}",
                f"- Current status: `{lane['current_status']}`",
                f"- Completion definition: {lane['completion_definition']}",
                f"- Next packet: `{lane['next_packet']}`",
                "- Evidence found:",
                *[f"  - {item}" for item in lane["evidence_found"]],
                "- Evidence missing:",
                *[f"  - {item}" for item in lane["evidence_missing"]],
                "- Blockers:",
                *[f"  - {item}" for item in lane["blockers"]],
                "- Required artifacts:",
                *[f"  - {item}" for item in lane["required_artifacts"]],
                "- Required tests:",
                *[f"  - {item}" for item in lane["required_tests"]],
                "",
            ]
        )
    lines.extend(
        [
            "## Shortest Packet Chain",
            *[
                f"{item['order']}. {item['packet_name']} - {item['goal']}"
                for item in chain
            ],
            "",
            "## Next Best Packet",
            f"`{state['next_best_packet']['packet_name']}`",
            "",
            "## One-Man Operator View",
        ]
    )
    lines.extend(f"- {key}: {value}" for key, value in operator.items())
    lines.extend(
        [
            "",
            "## Blocked Actions",
            *[
                f"- `{name}`: `{str(blocked).lower()}`"
                for name, blocked in state["blocked_actions"].items()
            ],
            "",
            "## Safe Next Action",
            state["safe_next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def _iter_evidence_files(repo_root: Path) -> Iterable[Path]:
    for root_name in EVIDENCE_ROOTS:
        root = repo_root / root_name
        if not root.exists():
            continue
        if root.is_file():
            if _safe_to_scan(root):
                yield root
            continue
        for path in root.rglob("*"):
            if path.is_file() and _safe_to_scan(path):
                yield path


def _safe_to_scan(path: Path) -> bool:
    text = path.as_posix().lower()
    if any(fragment in text for fragment in SENSITIVE_NAME_FRAGMENTS):
        return False
    if "__pycache__" in path.parts or "node_modules" in path.parts:
        return False
    return path.suffix.lower() in {".py", ".md", ".json", ".jsx", ".js", ".html"}


def _read_selected_text(repo_root: Path, files: list[Path]) -> str:
    priority_terms = (
        "FOREX_110",
        "VACATION",
        "PROFIT",
        "RETURN",
        "WALK",
        "BROKER",
        "DEMO",
        "LIVE",
        "RISK",
        "DASHBOARD",
        "22H",
        "22_6",
    )
    chunks: list[str] = []
    for path in files:
        rel = _rel(repo_root, path)
        if not any(term.lower() in rel.lower() for term in priority_terms):
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore")[:12000])
        except OSError:
            continue
    return "\n".join(chunks)


def _already_built(paths: list[str]) -> list[str]:
    important = (
        "FOREX_110_REAL_COMPLETION_REFOCUS_V1",
        "VACATION_MODE_FINAL_READINESS_DECISION",
        "STATISTICAL_PROFIT_PROOF_GATE",
        "EVIDENCE_DEPTH_WALKFORWARD_SUFFICIENCY",
        "BROKER_CONNECTION_PROOF_BOUNDARY_READINESS",
        "DASHBOARD_TRUTH",
        "CRITICAL_SAFETY_EVIDENCE_CLOSURE",
        "UPTIME_RANGE",
        "TRUSTED_PROFIT_22_6",
    )
    return [
        path
        for path in paths
        if any(marker.lower() in path.lower() for marker in important)
    ][:80]


def _profitability_status(evidence: dict[str, Any]) -> str:
    found = evidence["evidence_found"]
    not_proven = evidence["explicit_not_proven_signals"]["profitability"]
    if not_proven:
        return NOT_PROVEN
    if found["statistical_profit_gate"] and found["walk_forward_oos"]:
        return PARTIAL
    return NOT_PROVEN


def _return_target_status(evidence: dict[str, Any], target: str) -> str:
    text = evidence["text"]
    if target == "good_day":
        has_target_language = "25% to 100%" in text or "25% to 100% return" in text
    else:
        has_target_language = "up to 120%" in text or "120% return" in text
    if has_target_language and "not_proven" not in text:
        return REVIEW_REQUIRED
    return NOT_PROVEN


def _runtime_status(evidence: dict[str, Any]) -> str:
    if evidence["explicit_not_proven_signals"]["runtime_22h6d"]:
        return NOT_PROVEN
    return PARTIAL if evidence["evidence_found"]["runtime_22h6d"] else NOT_PROVEN


def _broker_readonly_status(evidence: dict[str, Any]) -> str:
    return PARTIAL if evidence["evidence_found"]["broker_readonly"] else NOT_PROVEN


def _demo_status(evidence: dict[str, Any]) -> str:
    text = evidence["text"]
    if "demo execution: `blocked`" in text or "demo_execution_status\": \"blocked" in text:
        return BLOCKED
    if evidence["evidence_found"]["vacation_mode_decision"]:
        return REVIEW_REQUIRED
    return BLOCKED


def _live_real_money_status(evidence: dict[str, Any]) -> str:
    if evidence["explicit_not_proven_signals"]["live"]:
        return BLOCKED
    return BLOCKED


def _risk_control_status(evidence: dict[str, Any]) -> str:
    if evidence["explicit_not_proven_signals"]["risk"]:
        return BLOCKED
    return PARTIAL if evidence["evidence_found"]["risk_controls"] else BLOCKED


def _dashboard_truth_status(evidence: dict[str, Any]) -> str:
    return PARTIAL if evidence["evidence_found"]["dashboard_truth"] else NOT_PROVEN


def _five_lane_completion_map(
    evidence: dict[str, Any], statuses: dict[str, str]
) -> list[dict[str, Any]]:
    return [
        _lane(
            "Profit Proof",
            statuses["profitability_status"],
            ["statistical profit proof gate", "walk-forward/OOS evidence files"],
            [
                "persistent positive expectancy after costs",
                "sufficient independent sample size",
                "drawdown-aware profit proof",
            ],
            [
                "Persistent profitability is not proven to vacation-grade standard.",
                "Profit proof is not enough to support real-money step-away operation.",
            ],
            [
                "current profit proof ledger",
                "walk-forward/OOS summary",
                "after-cost expectancy report",
            ],
            ["pytest profit proof gate", "JSON schema validation", "diff check"],
            "Persistent positive expectancy is proven across sufficient out-of-sample evidence after costs and drawdown controls.",
            "PKT-FOREX-110-PROFIT-EVIDENCE-TRUTH-LOCK-V1",
            evidence,
        ),
        _lane(
            "Return Target Validation",
            statuses["good_day_return_target_status"],
            ["owner target language captured"],
            [
                "25% to 100% good-day return validation",
                "up to 120% phenomenal-day validation",
                "risk-adjusted target realism proof",
            ],
            [
                "25% to 100% return target is not proven by repo evidence.",
                "120% return target is not proven by repo evidence.",
            ],
            [
                "return target validation harness",
                "candidate-by-candidate return distribution",
                "failure analysis for unmet target bands",
            ],
            ["target harness unit tests", "state JSON parse", "report readback"],
            "Good-day and phenomenal-day targets are validated or explicitly rejected by deterministic evidence.",
            "PKT-FOREX-110-RETURN-TARGET-VALIDATION-HARNESS-V1",
            evidence,
        ),
        _lane(
            "Broker + Runtime Evidence",
            _worst(
                statuses["broker_readonly_evidence_status"],
                statuses["twenty_two_hour_six_day_status"],
            ),
            ["broker-read-only evidence artifacts", "22H/6D planning artifacts"],
            [
                "complete sanitized broker-read-only evidence",
                "sustained 22H/day 6D/week runtime proof",
                "fresh runtime observation metrics",
            ],
            [
                "Broker-read-only evidence is partial, not complete.",
                "22H/day 6D/week operation is not proven.",
            ],
            [
                "sanitized broker-read-only bundle",
                "runtime observation ledger",
                "freshness and interruption summary",
            ],
            ["broker-read-only fixture tests", "runtime readiness tests", "no network checks"],
            "Broker-read-only evidence is complete and 22H/6D runtime readiness is proven without credential reads or broker contact.",
            "PKT-FOREX-110-WALK-FORWARD-OOS-SUFFICIENCY-CLOSURE-V1",
            evidence,
        ),
        _lane(
            "Safety / Real-Money Gate",
            _worst(statuses["risk_control_status"], statuses["live_real_money_status"]),
            ["risk gate artifacts", "live exception authority remains blocked"],
            [
                "owner approval gate",
                "kill switch",
                "max loss",
                "daily stop",
                "one-order-only",
                "SLTP",
                "post-trade evidence",
                "emergency stop",
            ],
            [
                "Live real-money readiness remains blocked.",
                "Final risk-control closure is not proven.",
            ],
            [
                "risk budget final gate",
                "kill-switch evidence",
                "daily stop and max-loss evidence",
                "SLTP and one-order-only proof",
            ],
            ["risk gate unit tests", "protected action gate review", "RISK_POLICY readback"],
            "All real-money controls are proven fail-closed and owner approval is required before any execution.",
            "PKT-FOREX-110-RISK-BUDGET-KILL-SWITCH-MAX-LOSS-FINAL-GATE-V1",
            evidence,
        ),
        _lane(
            "Dashboard Truth / Owner Control",
            statuses["dashboard_truth_status"],
            ["dashboard truth summary artifacts", "display-only dashboard contracts"],
            [
                "single owner view",
                "truthful blocked/partial/proven state",
                "no execution controls",
                "one-man next action",
            ],
            [
                "Dashboard truth is partial and must not imply vacation-grade readiness.",
                "Owner control view needs exact blocker and next-packet display.",
            ],
            [
                "Forex 110 state JSON",
                "owner-facing dashboard truth projection",
                "blocked action display",
            ],
            ["dashboard truth tests", "state projection schema validation", "operator view readback"],
            "The dashboard tells the truth: can trade, profit proof, return targets, step-away status, blockers, and next action.",
            "PKT-FOREX-110-DEMO-TO-LIVE-OWNER-APPROVAL-FINAL-EVIDENCE-BUNDLE-V1",
            evidence,
        ),
    ]


def _lane(
    lane_name: str,
    status: str,
    found_labels: list[str],
    missing: list[str],
    blockers: list[str],
    artifacts: list[str],
    tests: list[str],
    completion: str,
    next_packet: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "lane_name": lane_name,
        "current_status": status,
        "evidence_found": found_labels,
        "evidence_missing": missing,
        "blockers": blockers,
        "required_artifacts": artifacts,
        "required_tests": tests,
        "completion_definition": completion,
        "next_packet": next_packet,
        "evidence_scan_file_count": evidence["file_count"],
    }


def _shortest_packet_chain() -> list[dict[str, Any]]:
    names = (
        (
            "Profit Evidence Truth Lock",
            "Prove or fail persistent profitability with current repo evidence.",
        ),
        (
            "Return Target Validation Harness",
            "Validate 25% to 100% good-day and up to 120% phenomenal-day return targets.",
        ),
        (
            "Walk-Forward / OOS Sufficiency Closure",
            "Close out-of-sample sample size, pass-count, and regime sufficiency.",
        ),
        (
            "Broker Read-Only Evidence Closure",
            "Complete sanitized broker-read-only evidence without credentials or account inspection.",
        ),
        (
            "22H/6D Runtime Readiness Harness",
            "Prove sustained 22H/day 6D/week operation readiness from local evidence.",
        ),
        (
            "Risk Budget / Kill Switch / Max-Loss Final Gate",
            "Prove kill switch, max loss, daily stop, one-order-only, SLTP, and audit controls.",
        ),
        (
            "Demo-to-Live Owner Approval + Final Forex 110 Evidence Bundle",
            "Assemble final owner approval and evidence bundle without starting demo/live.",
        ),
    )
    return [
        {
            "order": index,
            "packet_id": f"PKT-FOREX-110-{index:02d}-{_slug(name)}-V1",
            "packet_name": name,
            "goal": goal,
        }
        for index, (name, goal) in enumerate(names, start=1)
    ]


def _current_truth_summary(statuses: dict[str, str], vacation_status: str) -> str:
    return (
        f"Vacation-grade readiness is {vacation_status}. Profitability is "
        f"{statuses['profitability_status']}. The 25% to 100% good-day return "
        f"target is {statuses['good_day_return_target_status']}. The up to "
        f"120% phenomenal-day return target is "
        f"{statuses['phenomenal_day_return_target_status']}. 22H/day 6D/week "
        f"operation is {statuses['twenty_two_hour_six_day_status']}. "
        f"Broker-read-only evidence is {statuses['broker_readonly_evidence_status']}. "
        f"Demo execution is {statuses['demo_execution_status']}. Live "
        f"real-money readiness is {statuses['live_real_money_status']}. Risk "
        f"controls are {statuses['risk_control_status']}. Dashboard truth is "
        f"{statuses['dashboard_truth_status']}."
    )


def _one_man_operator_view(state: dict[str, Any]) -> dict[str, str]:
    return {
        "What is happening?": "AIOS is blocked from Forex 110 vacation-grade readiness and is compressing remaining work into five lanes.",
        "Is it safe?": "Safe for repo evidence review only; execution, broker contact, credentials, demo, and live actions remain blocked.",
        "Can it trade?": "No. Trading is blocked.",
        "Is profit proven?": state["profitability_status"],
        "Are return targets proven?": f"Good day {state['good_day_return_target_status']}; phenomenal day {state['phenomenal_day_return_target_status']}.",
        "Can I step away?": "No. Step-away vacation-grade operation is not proven.",
        "What is blocked?": "Profit proof, return target proof, 22H/6D proof, live real-money gate, final risk proof, and complete dashboard truth.",
        "What do I do next?": state["safe_next_action"],
    }


def _actually_proven(statuses: dict[str, str]) -> list[str]:
    return [name for name, status in statuses.items() if status == PROVEN]


def _not_yet_proven(statuses: dict[str, str]) -> list[str]:
    return [name for name, status in statuses.items() if status != PROVEN]


def _assert_readiness_values(state: dict[str, Any]) -> None:
    for key, value in state.items():
        if key.endswith("_status") and isinstance(value, str):
            if value not in READINESS_VALUES:
                raise ValueError(f"invalid readiness value for {key}: {value}")
    for lane in state["five_lane_completion_map"]:
        if lane["current_status"] not in READINESS_VALUES:
            raise ValueError(f"invalid lane status: {lane['current_status']}")


def _worst(left: str, right: str) -> str:
    order = {BLOCKED: 0, NOT_PROVEN: 1, REVIEW_REQUIRED: 2, PARTIAL: 3, PROVEN: 4}
    return left if order[left] <= order[right] else right


def _contains_path(paths: list[str], marker: str) -> bool:
    return any(marker.lower() in path.lower() for path in paths)


def _contains_any(paths: list[str], markers: tuple[str, ...]) -> bool:
    return any(_contains_path(paths, marker) for marker in markers)


def _exists(paths: list[str], expected: str) -> bool:
    expected_normal = expected.replace("\\", "/").lower()
    return any(path.lower() == expected_normal for path in paths)


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def _slug(value: str) -> str:
    return (
        value.upper()
        .replace(" / ", "-")
        .replace(" + ", "-")
        .replace(" ", "-")
        .replace("/", "-")
    )


__all__ = [
    "BLOCKED_ACTIONS",
    "PACKET_ID",
    "READINESS_VALUES",
    "SCHEMA_VERSION",
    "build_report_markdown",
    "run_forex_110_vacation_grade_profit_engine_v1",
    "scan_repo_evidence",
]
