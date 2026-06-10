"""AI_OS approval review compressor (observe-only).

Protected actions need a Human Owner decision, but reading a full packet plus raw
validator JSON is heavy. This module compresses a packet + its governance verdict
+ its completeness verdict + risk signals into ONE compact approval card: what it
does, why, the risk level, the exact scope, the gates that still apply, and a
recommended decision LABEL.

It compresses; it never decides. requires_human is always True and
approves_protected_action is always False. It emits decision LABELS, never commands.

Pure standard library. Read-only. No mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_APPROVAL_REVIEW_CARD.v1"

DECISION_LABELS = {
    "READY_FOR_HUMAN_APPROVAL",          # clean, non-protected; a human may approve DRY_RUN APPLY
    "HUMAN_REVIEW_REQUIRED_PROTECTED",   # touches a protected surface; extra scrutiny
    "HOLD_FOR_REWORK",                   # incomplete; send back before review
    "REJECT_OR_REWORK",                  # hazard block; do not promote
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _errors(verdict: Optional[dict]) -> list:
    return (verdict or {}).get("errors", []) or []


def build_approval_card(
    packet: dict,
    *,
    governance: Optional[dict] = None,
    completeness: Optional[dict] = None,
    risk_signals: Optional[list[str]] = None,
    now: Optional[str] = None,
) -> dict[str, object]:
    """Compress packet + verdicts + risk into one approval card. Observe-only."""
    now = now or _now()
    packet = packet or {}
    risk_signals = list(risk_signals or [])

    packet_id = str(packet.get("packet_id") or "UNKNOWN-PACKET")
    objective = str(packet.get("objective") or packet.get("mission") or "(no objective stated)")
    allowed = list(packet.get("allowed_paths") or [])
    protected = bool(packet.get("protected_action_expected"))

    gov_errors = _errors(governance)
    has_block = any(e.get("severity") == "BLOCK" for e in gov_errors)
    has_fail = any(e.get("severity") == "FAIL" for e in gov_errors)
    gov_status = (governance or {}).get("status", "UNAVAILABLE")

    comp_verdict = (completeness or {}).get("verdict", "UNKNOWN")
    promotion_ready = bool((completeness or {}).get("promotion_ready", False))

    # Risk level
    if has_block or comp_verdict == "PROMOTION_BLOCKED":
        risk_level = "HIGH"
    elif protected or comp_verdict == "INCOMPLETE" or has_fail or risk_signals:
        risk_level = "MEDIUM" if not protected else "HIGH"
    else:
        risk_level = "LOW"

    # Recommended decision LABEL (fail-closed: default to the more cautious option)
    if has_block or comp_verdict == "PROMOTION_BLOCKED":
        recommended = "REJECT_OR_REWORK"
    elif comp_verdict == "INCOMPLETE" or has_fail or not promotion_ready:
        recommended = "HOLD_FOR_REWORK"
    elif protected:
        recommended = "HUMAN_REVIEW_REQUIRED_PROTECTED"
    else:
        recommended = "READY_FOR_HUMAN_APPROVAL"

    blocking_reasons: list[str] = []
    if has_block:
        blocking_reasons += [f"governance BLOCK: {e.get('rule_id')}" for e in gov_errors if e.get("severity") == "BLOCK"]
    if comp_verdict in {"INCOMPLETE", "PROMOTION_BLOCKED"}:
        blocking_reasons += (completeness or {}).get("reasons", []) or [f"completeness verdict {comp_verdict}"]
    blocking_reasons += risk_signals

    card_id = "card-" + hashlib.sha1(f"{packet_id}{now}".encode("utf-8")).hexdigest()[:10]
    card = {
        "schema": SCHEMA,
        "card_id": card_id,
        "generated_at": now,
        "packet_id": packet_id,
        "summary_line": f"{packet_id}: {objective[:120]}",
        "why": objective,
        "risk_level": risk_level,
        "protected_action_expected": protected,
        "scope_allowed_paths": allowed,
        "gates_still_required": [
            "APPLY requires separate explicit Human Owner approval naming this packet.",
            "commit, push, and merge each require their own separate approval; approval does not transfer.",
            "merge / secrets / broker / live remain permanent human hard gates.",
        ],
        "validator_summary": {
            "governance_status": gov_status,
            "governance_block": has_block,
            "governance_fail": has_fail,
            "completeness_verdict": comp_verdict,
            "promotion_ready": promotion_ready,
        },
        "blocking_reasons": blocking_reasons,
        "decision_options": sorted(DECISION_LABELS),
        "recommended_decision": recommended,
        "requires_human": True,
        "approves_protected_action": False,
        "safe_next_action": "Human Owner reviews this card and issues an explicit decision. The card decides nothing.",
    }
    card["card_markdown"] = render_card(card)
    return card


def render_card(card: dict) -> str:
    vs = card["validator_summary"]
    lines = [
        f"# Approval Card — {card['packet_id']}",
        "",
        f"- risk: **{card['risk_level']}**   protected: **{card['protected_action_expected']}**",
        f"- recommended: **{card['recommended_decision']}**",
        f"- governance: `{vs['governance_status']}` (block={vs['governance_block']}, fail={vs['governance_fail']})",
        f"- completeness: `{vs['completeness_verdict']}` (promotion_ready={vs['promotion_ready']})",
        "",
        "## What / why",
        f"{card['why']}",
        "",
        "## Scope (allowed paths)",
    ]
    lines += [f"- `{p}`" for p in card["scope_allowed_paths"]] or ["- (none scoped)"]
    lines += ["", "## Blocking reasons"]
    lines += [f"- {r}" for r in card["blocking_reasons"]] or ["- none"]
    lines += ["", "## Gates still required"]
    lines += [f"- {g}" for g in card["gates_still_required"]]
    lines += ["", "_Compressed review card. It decides nothing; the Human Owner decides._"]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compress a packet + verdicts into one approval card (observe-only).")
    parser.add_argument("--packet-json", required=True, help="JSON with packet_id/objective/allowed_paths/protected_action_expected")
    parser.add_argument("--governance-json", default=None)
    parser.add_argument("--completeness-json", default=None)
    args = parser.parse_args()

    def _read(p):
        return json.loads(Path(p).read_text(encoding="utf-8")) if p else None

    card = build_approval_card(
        _read(args.packet_json) or {},
        governance=_read(args.governance_json),
        completeness=_read(args.completeness_json),
    )
    print(json.dumps({k: v for k, v in card.items() if k != "card_markdown"}, indent=2, sort_keys=True))
    print("\n" + card["card_markdown"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
