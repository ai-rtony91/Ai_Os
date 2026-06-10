"""AI_OS autonomy control-plane runtime connector (Theme 1 CONNECT, observe-only).

This is the read-only seam that surfaces the autonomy control plane into the
runtime / night / coordination reporting path, and wires the completion evidence
validator in as the TRUST GATE.

It does not run the control plane (that is the PowerShell lane). It READS the
control-plane and router reports the control plane already produced, runs the
completion evidence validator on any claimed completion, and emits ONE unified
observe-only runtime view. It mutates no queue, lock, approval, or dispatch state,
and it will never surface an apply / merge / live / broker / secret command.

Pure standard library. Observe-only. No network. No mutation except an optional
explicit output report.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCHEMA = "AIOS_AUTONOMY_CONTROL_PLANE_RUNTIME_VIEW.v1"

# Commands that must never be auto-surfaced as runnable by an observe-only seam.
PROHIBITED_COMMAND = re.compile(
    r"(?i)("
    r"git\s+merge|gh\s+pr\s+merge|git\s+push\s+\S*\s*origin\s+main|--apply\b|-Apply\b|-ArmRestart\b|"
    r"\bplace_order\b|\breal_order\b|\blive_order\b|broker|OANDA|live_trading|"
    r"schtasks\s+/create|Register-ScheduledTask|New-Service|"
    r"\brm\s+-rf\b|Remove-Item|git\s+reset\s+--hard|git\s+clean|force.?push"
    r")"
)


def _toolchain_root() -> Path:
    """Repo root of THIS connector (the toolchain), independent of the workspace repo_root."""
    return Path(__file__).resolve().parents[3]


def _load_completion_validator():
    """Load the merged completion evidence validator (#512) from the toolchain location."""
    path = _toolchain_root() / "automation" / "validators" / "aios_completion_evidence_validator.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("aios_completion_evidence_validator", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # py3.11 dataclass/importlib gotcha
    spec.loader.exec_module(module)
    return module


def _g(d: Optional[dict], *keys: str, default: Any = None) -> Any:
    cur: Any = d or {}
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def build_runtime_view(
    control_plane_report: Optional[dict],
    router_report: Optional[dict],
    repo_root: Path,
    packet_text: str = "",
    changed_files: Optional[list[str]] = None,
    evidence_text: Optional[str] = None,
) -> dict[str, object]:
    changed_files = changed_files or []

    cp_status = str(_g(control_plane_report, "status", default="UNKNOWN"))
    validator_status = str(_g(control_plane_report, "validator", "status", default="UNKNOWN"))
    runner_status = str(_g(control_plane_report, "packet_runner", "status", default="UNKNOWN"))

    next_action = str(_g(router_report, "next_action", default="UNKNOWN"))
    raw_command = str(_g(router_report, "safe_command", default=""))
    requires_human = bool(_g(router_report, "requires_anthony", default=False))
    protected = bool(_g(router_report, "protected_action", default=False))
    live_risk = bool(_g(router_report, "live_risk", default=False))

    # TRUST GATE: run the completion evidence validator (#512) on any claimed completion.
    completion = {"verdict": "NOT_EVALUATED", "reasons": []}
    if changed_files or evidence_text:
        cev = _load_completion_validator()
        if cev is not None:
            result = cev.evaluate_completion(packet_text, changed_files, repo_root, evidence_text)
            completion = {"verdict": result["verdict"], "reasons": result.get("reasons", [])}
        else:
            completion = {"verdict": "TRUST_GATE_UNAVAILABLE", "reasons": ["completion validator not found"]}

    # Refuse to surface any apply/merge/live/broker command from an observe-only seam.
    command_is_prohibited = bool(raw_command) and bool(PROHIBITED_COMMAND.search(raw_command))
    if command_is_prohibited:
        surfaced_command = "echo Held for Human Owner approval; observe-only connector takes no action."
        requires_human = True
    else:
        surfaced_command = raw_command or "echo No safe next command available."

    # Runtime gate classification (what the loop may do with this, observe-only).
    if cp_status.upper() in {"BLOCKED", "FAILED"} or next_action.upper() == "BLOCKED":
        runtime_gate = "BLOCKED"
    elif completion["verdict"] == "COMPLETION_CONTRADICTED":
        runtime_gate = "TRUST_FAILED"
    elif requires_human or protected or live_risk or command_is_prohibited:
        runtime_gate = "HUMAN_REQUIRED"
    else:
        runtime_gate = "READY_TO_REPORT"

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "DRY_RUN",
        "observe_only": True,
        "control_plane": {
            "status": cp_status,
            "validator_status": validator_status,
            "packet_runner_status": runner_status,
        },
        "next_action": {
            "action": next_action,
            "surfaced_command": surfaced_command,
            "requires_human": requires_human,
            "protected_action": protected,
            "live_risk": live_risk,
            "command_was_prohibited_and_held": command_is_prohibited,
        },
        "trust_gate_completion": completion,
        "runtime_gate": runtime_gate,
        "safety": {
            "apply": False,
            "merge": False,
            "live_trading": False,
            "broker": False,
            "secrets": False,
            "mutated_repo_state": False,
        },
        "safe_next_action": (
            "Surface to operator report. No action taken by the observe-only connector."
            if runtime_gate in {"READY_TO_REPORT"}
            else "Hold and surface to Human Owner. Observe-only connector takes no action."
        ),
    }


def _read_json(path: Optional[str]) -> Optional[dict]:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="AI_OS control-plane runtime connector (observe-only).")
    parser.add_argument("--control-plane-report")
    parser.add_argument("--router-report")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--packet")
    parser.add_argument("--changed", action="append", default=[])
    parser.add_argument("--evidence")
    parser.add_argument("--output", help="optional: write the runtime view atomically to this path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    packet_text = Path(args.packet).read_text(encoding="utf-8") if args.packet and Path(args.packet).exists() else ""
    evidence_text = Path(args.evidence).read_text(encoding="utf-8") if args.evidence and Path(args.evidence).exists() else None

    view = build_runtime_view(
        _read_json(args.control_plane_report),
        _read_json(args.router_report),
        repo_root,
        packet_text=packet_text,
        changed_files=args.changed,
        evidence_text=evidence_text,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=str(out.parent), delete=False, encoding="utf-8") as tmp:
            tmp.write(json.dumps(view, indent=2, sort_keys=True))
            tmp_path = Path(tmp.name)
        tmp_path.replace(out)

    print(json.dumps(view, indent=2, sort_keys=True))
    return 0 if view["runtime_gate"] != "BLOCKED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
