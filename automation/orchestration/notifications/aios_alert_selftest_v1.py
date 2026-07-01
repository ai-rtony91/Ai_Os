#!/usr/bin/env python3
"""AI_OS ntfy alert tone self-test dry-run harness.

The checked-in self-test is DRY_RUN only. It plans alert-channel receipts from
an explicit example config and never sends notifications.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_ID = "AIOS-P29"
SCHEMA = "AIOS_ALERT_SELFTEST_RECEIPT.v1"
DEFAULT_BASE_URL = "https://ntfy.sh"
CHANNEL_ORDER = ("tip", "jackpot", "reply")
EXAMPLE_TOPIC_PREFIX = "PUT_"


@dataclass(frozen=True)
class ChannelSpec:
    title: str
    priority: int
    body: str
    tags: str
    hear_note: str


CHANNEL_SPECS: dict[str, ChannelSpec] = {
    "tip": ChannelSpec(
        title="AIOS TEST - TIP",
        priority=4,
        body="Tip tone test - bucket filling.",
        tags="bell",
        hear_note="Dry-run verifies the TIP alert receipt that would map to the tip topic.",
    ),
    "jackpot": ChannelSpec(
        title="AIOS TEST - JACKPOT",
        priority=5,
        body="Jackpot tone test - milestone hit.",
        tags="slot_machine",
        hear_note="Dry-run verifies the JACKPOT alert receipt that would map to the jackpot topic.",
    ),
    "reply": ChannelSpec(
        title="AIOS TEST - REPLY",
        priority=3,
        body="Reply channel test (reply APPROVE to check the poll leg).",
        tags="speech_balloon",
        hear_note="Dry-run verifies the REPLY alert receipt that would map to the reply topic.",
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def mask_secret(value: str | None) -> str:
    if not value:
        return "not_configured"
    text = str(value)
    return f"{text[:5]}***"


def is_placeholder_topic(value: str | None) -> bool:
    if not value:
        return True
    text = value.strip()
    upper = text.upper()
    return (
        not text
        or upper.startswith(EXAMPLE_TOPIC_PREFIX)
        or "PLACEHOLDER" in upper
        or upper in {"CHANGEME", "CHANGE_ME", "EXAMPLE", "REPLACE_ME"}
    )


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return None, None
    except json.JSONDecodeError:
        return None, "config_json_invalid"
    except OSError:
        return None, "config_read_failed"
    if not isinstance(data, dict):
        return None, "config_root_not_object"
    return data, None


def load_config(repo_root: Path, explicit_config: Path | None) -> tuple[dict[str, Any], str, str | None]:
    config_path = explicit_config or repo_root / "control" / "secrets" / "alert_channels.example.json"
    config_label = display_path(repo_root, config_path)
    if is_real_alert_config(repo_root, config_path):
        return {}, config_label, "real_config_blocked"
    data, error_name = read_json(config_path)
    if error_name is not None:
        return {}, config_label, error_name
    if data is None:
        return {}, "none", None
    return data, config_label, None


def display_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def is_real_alert_config(repo_root: Path, path: Path) -> bool:
    real_config_path = repo_root / "control" / "secrets" / "alert_channels.json"
    return path.resolve() == real_config_path.resolve()


def normalize_topics(config: dict[str, Any]) -> dict[str, str]:
    raw_topics = config.get("topics", {})
    if not isinstance(raw_topics, dict):
        return {}
    topics: dict[str, str] = {}
    for name in CHANNEL_ORDER:
        value = raw_topics.get(name, "")
        if isinstance(value, str):
            topics[name] = value.strip()
    return topics


def normalize_base_url(config: dict[str, Any]) -> str:
    value = config.get("ntfy_base_url", DEFAULT_BASE_URL)
    if not isinstance(value, str) or not value.strip():
        return DEFAULT_BASE_URL
    return value.strip().rstrip("/")


def normalize_token(config: dict[str, Any]) -> str:
    value = config.get("ntfy_auth_token", "")
    if not isinstance(value, str):
        return ""
    return value.strip()


def build_channel_receipt(
    *,
    name: str,
    topic: str | None,
    spec: ChannelSpec,
    config_error: str | None,
) -> dict[str, Any]:
    placeholder_or_missing = is_placeholder_topic(topic)
    configured = not placeholder_or_missing and config_error is None
    receipt: dict[str, Any] = {
        "channel": name,
        "topic_masked": mask_secret(topic),
        "title": spec.title,
        "priority": spec.priority,
        "planned": configured,
        "sent": False,
        "http_status": None,
        "failed_closed": not configured,
        "status": "planned" if configured else "channel_not_configured",
        "what_you_should_hear": spec.hear_note,
    }
    if config_error:
        receipt["status"] = config_error
        return receipt
    return receipt


def build_receipt(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    explicit_config = None
    if args.config:
        raw_config_path = Path(args.config)
        explicit_config = raw_config_path if raw_config_path.is_absolute() else repo_root / raw_config_path
        explicit_config = explicit_config.resolve()
    config, config_source, config_error = load_config(repo_root, explicit_config)
    topics = normalize_topics(config)
    base_url = normalize_base_url(config)
    token = normalize_token(config)
    selected = [args.only] if args.only else list(CHANNEL_ORDER)
    channel_receipts = [
        build_channel_receipt(
            name=name,
            topic=topics.get(name, ""),
            spec=CHANNEL_SPECS[name],
            config_error=config_error,
        )
        for name in selected
    ]
    all_unconfigured = all(item["status"] == "channel_not_configured" for item in channel_receipts)
    status = "dry_run_planned"
    if config_error:
        status = config_error
    elif all_unconfigured:
        status = "channel_not_configured"

    return {
        "schema": SCHEMA,
        "packet_id": PACKET_ID,
        "generated_at_utc": utc_now(),
        "mode": "DRY_RUN",
        "status": status,
        "config_source": config_source,
        "ntfy_base_url": base_url,
        "ntfy_auth_token_configured": bool(token),
        "outbound_only": True,
        "money_movement_allowed": False,
        "broker_or_oanda_allowed": False,
        "send_requested": False,
        "dry_run_only": True,
        "network_call_allowed": False,
        "channels": channel_receipts,
    }


def report_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# AIOS Alert Self-Test v1 Report",
        "",
        f"- Packet: {receipt['packet_id']}",
        f"- Generated UTC: {receipt['generated_at_utc']}",
        f"- Mode: {receipt['mode']}",
        f"- Status: {receipt['status']}",
        f"- Config source: {receipt['config_source']}",
        f"- Outbound only: {receipt['outbound_only']}",
        f"- Money movement allowed: {receipt['money_movement_allowed']}",
        f"- Broker/OANDA allowed: {receipt['broker_or_oanda_allowed']}",
        f"- Send requested: {receipt['send_requested']}",
        f"- Dry-run only: {receipt['dry_run_only']}",
        f"- Network call allowed: {receipt['network_call_allowed']}",
        f"- Auth token configured: {receipt['ntfy_auth_token_configured']}",
        "",
        "## Safety Boundary",
        "",
        "- This source stack is validation-only and does not send notifications.",
        "- The default config path is the checked-in example config.",
        "- The real alert_channels.json path is blocked by this harness.",
        "- Real alert channel config remains gitignored and is not required for validation.",
        "",
        "## Planned Alert Receipts",
        "",
    ]
    for item in receipt["channels"]:
        lines.append(
            f"- {item['channel']}: {item['what_you_should_hear']} "
            f"Title={item['title']}; Priority={item['priority']}; Topic={item['topic_masked']}; "
            f"Status={item['status']}."
        )
    lines.extend(
        [
            "",
            "## Receipt",
            "",
            "```json",
            json.dumps(receipt, indent=2),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(repo_root: Path, receipt: dict[str, Any]) -> Path:
    report_path = repo_root / "Reports" / "notifications" / "AIOS_ALERT_SELFTEST_V1_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_markdown(receipt), encoding="utf-8")
    return report_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI_OS ntfy alert tone self-test harness.")
    parser.add_argument("--repo-root", default=str(default_repo_root()), help="AI_OS repository root.")
    parser.add_argument("--config", default="", help="Optional config path for validation-only dry runs.")
    parser.add_argument("--only", choices=CHANNEL_ORDER, help="Test only one channel.")
    parser.add_argument("--pretty", action="store_true", help="Print indented JSON receipt.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    receipt = build_receipt(args)
    report_path = write_report(repo_root, receipt)
    receipt["report_path"] = str(report_path)
    text = json.dumps(receipt, indent=2 if args.pretty else None, sort_keys=False)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
