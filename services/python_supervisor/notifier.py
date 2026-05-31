"""AI_OS local SOS notifier.

Default channel is file only. Email and push channels are intentionally disabled
until Anthony supplies local environment variables and approves that gate.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCKING_STATUSES = {"BLOCKED", "NEEDS_APPROVAL"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def status_from_state(state: dict[str, Any]) -> str:
    raw = (
        state.get("night_supervisor_status")
        or state.get("supervisor_status")
        or state.get("status")
        or "UNKNOWN"
    )
    return str(raw).upper()


def notification_key(state: dict[str, Any]) -> str:
    status = status_from_state(state)
    generated = str(state.get("generated_at") or "")
    summary = str(state.get("plain_summary") or "")
    return f"{status}|{generated}|{summary}"


def render_sos(state: dict[str, Any]) -> str:
    status = status_from_state(state)
    summary = str(state.get("plain_summary") or "No summary available.")
    approval_count = state.get("approval_needed_count", "UNKNOWN")
    next_action = str(state.get("next_safe_action") or "Review bridge state before taking action.")
    must_see = state.get("must_see") or []
    if not isinstance(must_see, list):
        must_see = [must_see]

    lines = [
        f"# AI_OS SOS - {status}",
        "",
        f"- Generated: {utc_now()}",
        f"- Bridge generated_at: {state.get('generated_at', 'UNKNOWN')}",
        f"- Plain summary: {summary}",
        f"- Waiting approvals: {approval_count}",
        "- Must see:",
    ]
    if must_see:
        lines.extend(f"  - {item}" for item in must_see)
    else:
        lines.append("  - No must-see items reported.")
    lines.append(f"- Next safe action: {next_action}")
    lines.append("")
    lines.append("Channel: file")
    lines.append("Secrets used: none")
    return "\n".join(lines) + "\n"


def write_file_channel(root: Path, state: dict[str, Any]) -> Path:
    outbox = root / "relay" / "reports" / "SOS_OUTBOX"
    outbox.mkdir(parents=True, exist_ok=True)
    filename = f"SOS_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    target = outbox / filename
    target.write_text(render_sos(state), encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="AI_OS file-channel SOS notifier")
    parser.add_argument("--channel", default="file", choices=["file", "email", "push"])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--state", default="telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json")
    args = parser.parse_args()

    root = repo_root()
    state_path = root / args.state
    last_path = root / "telemetry" / "night_supervisor" / "last_notified.json"

    if args.channel != "file":
        print("STATUS=BLOCKED")
        print("REASON=non-file channels require Anthony-managed environment secrets and are disabled")
        return 2

    if not state_path.exists():
        print("STATUS=NO_STATE")
        print(f"STATE_PATH={state_path}")
        return 0

    state = read_json(state_path)
    status = status_from_state(state)
    key = notification_key(state)
    previous = read_json(last_path) if last_path.exists() else {}

    if status not in BLOCKING_STATUSES:
        if args.apply:
            write_json(last_path, {"last_status": status, "last_key": key, "updated_at": utc_now()})
        print("STATUS=NO_BLOCKER")
        print(f"BRIDGE_STATUS={status}")
        return 0

    if previous.get("last_key") == key:
        print("STATUS=SUPPRESSED")
        print(f"BRIDGE_STATUS={status}")
        print("REASON=already notified for this state")
        return 0

    if not args.apply:
        print("STATUS=DRY_RUN_WOULD_NOTIFY")
        print(f"BRIDGE_STATUS={status}")
        print("CHANNEL=file")
        return 0

    target = write_file_channel(root, state)
    write_json(last_path, {"last_status": status, "last_key": key, "updated_at": utc_now(), "channel": "file"})
    print("STATUS=NOTIFIED")
    print(f"BRIDGE_STATUS={status}")
    print(f"OUTBOX_FILE={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
