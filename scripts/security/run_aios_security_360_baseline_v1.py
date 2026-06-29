from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.security.aios_security_360_baseline_v1 import build_security_360_baseline


STATE_PATH = REPO_ROOT / "Reports" / "security" / "AIOS_SECURITY_360_BASELINE_V1_STATE.json"
REPORT_PATH = REPO_ROOT / "Reports" / "security" / "AIOS_SECURITY_360_BASELINE_V1_REPORT.md"


def _finding_lines(findings: list[dict[str, str]]) -> list[str]:
    if not findings:
        return ["- None."]
    return [
        f"- `{item['id']}` ({item['severity']}): {item['summary']} Required action: {item['required_action']}"
        for item in findings
    ]


def render_report(state: dict) -> str:
    lines: list[str] = [
        "# AIOS Security 360 Baseline V1 Report",
        "",
        "## Summary",
        "",
        f"- Packet ID: `{state['packet_id']}`",
        f"- Security baseline status: `{state['security_baseline_status']}`",
        f"- Overall security posture: `{state['overall_security_posture']}`",
        f"- Bank-style security target: `{state['bank_style_security_target']}`",
        f"- Certification claim: `{state['certification_claim']}`",
        "",
        "This is an internal defense-in-depth engineering baseline. It does not claim legal bank certification or external compliance certification.",
        "",
        "## Current Rule",
        "",
        "Remote dashboard, broker, real-money, Bitwarden, credential, demo, live, scheduler, daemon, webhook, tunnel, deployment, and autonomous execution work remains blocked until the required gates pass and the Human Owner approves the exact path.",
        "",
        "## Critical Blockers",
        "",
        *_finding_lines(state["critical_blockers"]),
        "",
        "## High Priority Findings",
        "",
        *_finding_lines(state["high_priority_findings"]),
        "",
        "## Medium Priority Findings",
        "",
        *_finding_lines(state["medium_priority_findings"]),
        "",
        "## Low Priority Findings",
        "",
        *_finding_lines(state["low_priority_findings"]),
        "",
        "## Required Gates",
        "",
    ]
    for key in (
        "required_gates_before_remote_dashboard",
        "required_gates_before_broker_readonly",
        "required_gates_before_bitwarden",
        "required_gates_before_demo",
        "required_gates_before_live",
        "required_gates_before_scheduler_daemon_webhook",
    ):
        gate = state[key]
        lines.extend(
            [
                f"### {gate['name']}",
                "",
                f"- Status: `{gate['status']}`",
                f"- Owner approval required: `{gate['owner_approval_required']}`",
                "- Required controls:",
            ]
        )
        lines.extend([f"  - {control}" for control in gate["required_controls"]])
        lines.append("")
    lines.extend(
        [
            "## Security Domains",
            "",
        ]
    )
    for domain in state["security_domains"]:
        lines.append(f"- {domain['id']}. {domain['name']}: `{domain['status']}` - {domain['notes']}")
    lines.extend(
        [
            "",
            "## Protected Actions",
            "",
        ]
    )
    for action, detail in state["protected_actions"].items():
        lines.append(f"- `{action}`: `{detail['status']}`")
    lines.extend(
        [
            "",
            "## Safe Next Actions",
            "",
        ]
    )
    lines.extend([f"- {action}" for action in state["safe_next_actions"]])
    lines.extend(
        [
            "",
            "## Tool Behavior",
            "",
            "- Static repo checks only.",
            "- No environment-file reads.",
            "- No credential, token, or API key reads.",
            "- No network calls.",
            "- No broker calls.",
            "- No file mutation in the baseline engine.",
            "",
            "Status: `BASELINE_CREATED_REVIEW_REQUIRED`",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build AIOS Security 360 Baseline V1.")
    parser.add_argument("--write-state", action="store_true", help="Write JSON state to Reports/security.")
    parser.add_argument("--write-report", action="store_true", help="Write Markdown report to Reports/security.")
    args = parser.parse_args(argv)

    state = build_security_360_baseline(REPO_ROOT)

    if args.write_state:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.write_report:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(render_report(state), encoding="utf-8")

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
