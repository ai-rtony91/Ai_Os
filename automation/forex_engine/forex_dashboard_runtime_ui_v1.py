from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
BUCKET_ID = "BKT-FOREX-DASHBOARD-RUNTIME-UI-001"
PACKET_ID = "PKT-FOREX-DASHBOARD-RUNTIME-UI-V1"
CANONICAL_DASHBOARD_ID = "FOREX_DASHBOARD_RUNTIME_UI_V1"
DUPLICATE_DASHBOARD_POLICY = "SINGLE_CANONICAL_SURFACE_ONLY"
DASHBOARD_VISUAL_HANDOFF_STATUS = "HANDOFF_REQUIRED_BEFORE_FINAL_VISUAL_IMPLEMENTATION"
BITWARDEN_STATUS = "LOCKED_UNTIL_OWNER_CONFIRMS_AFTER_FOREX_110"
PROTECTED_BROKER_BOUNDARY_STATUS = "PROTECTED_AND_SEPARATE"

STATE_PATH = Path("Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json")
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_REPORT.md")
PREVIEW_PATH = Path("Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_PREVIEW.html")
DOCS_PATH = Path("docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.md")
DOCS_HTML_PATH = Path("docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.html")

DASHBOARD_PACKAGE_FILES = [
    PREVIEW_PATH.as_posix(),
    REPORT_PATH.as_posix(),
    STATE_PATH.as_posix(),
    "automation/forex_engine/forex_dashboard_runtime_ui_v1.py",
    DOCS_HTML_PATH.as_posix(),
    DOCS_PATH.as_posix(),
    "scripts/forex_delivery/run_forex_dashboard_runtime_ui_v1.py",
    "tests/forex_engine/test_forex_dashboard_runtime_ui_v1.py",
]

SOURCE_ARTIFACTS = [
    Path("Reports/forex_delivery/AIOS_FOREX_110_COMPLETION_AND_BITWARDEN_UNLOCK_GATE_V1_STATE.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_DASHBOARD_END_USER_FINAL_UX_V1.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_DASHBOARD_EMOJI_WINDOW_MAP_FINAL_V1.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_FINAL_PROTECTED_BROKER_BOUNDARY_HANDOFF_V1.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_CANDIDATE_SELECTOR_HARDENING_V1_STATE.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_DECISION_V1_STATE.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_EVIDENCE_DEPTH_WALKFORWARD_SUFFICIENCY_V1_STATE.json"),
]

PROTECTED_FLAGS = {
    "broker_api_used": False,
    "credentials_used": False,
    "env_read": False,
    "account_identifiers_used": False,
    "order_execution": False,
    "demo_authorized": False,
    "live_authorized": False,
    "scheduler_started": False,
    "daemon_started": False,
    "webhook_started": False,
    "background_loop_started": False,
    "bitwarden_started": False,
    "vaultwarden_started": False,
    "secrets_migration_started": False,
    "token_storage_started": False,
}

CRITICAL_DISPLAY_RULES = [
    "Show critical status by default.",
    "Show active blocker by default.",
    "Show next safe action by default.",
    "Show safety state by default.",
    "Do not show secret values.",
    "Do not show broker account identifiers.",
    "Do not show order execution data.",
    "Do not show demo or live authorization controls.",
]

HIDDEN_DETAIL_RULES = [
    "Hide raw broker data behind report/detail windows.",
    "Hide raw trade data behind report/detail windows.",
    "Hide raw metadata behind report/detail windows.",
    "Hide long validator logs behind report/detail windows.",
    "Hide internal state dumps behind report/detail windows.",
]

WINDOWS = [
    {
        "emoji": "🏛️",
        "title": "Command Center",
        "short_label": "Command Center",
        "default_summary": "Forex 110 completion, blocker state, and next safe action.",
        "detail_summary": "The repo-safe Forex 110 gate is complete. Broker/live work remains protected and separate.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[0]), str(SOURCE_ARTIFACTS[1])],
        "criticality": "critical",
        "hidden_by_default_fields": ["raw completion state", "full report text"],
    },
    {
        "emoji": "🛡️",
        "title": "Safety Gate",
        "short_label": "Safety Gate",
        "default_summary": "Protected actions are blocked in this local dashboard preview.",
        "detail_summary": "Broker contact, credentials, account identifiers, order paths, demo/live authorization, and automation starts remain blocked.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[1]), str(SOURCE_ARTIFACTS[3])],
        "criticality": "critical",
        "hidden_by_default_fields": ["full blocked-action list", "raw safety notes"],
    },
    {
        "emoji": "🎯",
        "title": "Candidate",
        "short_label": "Candidate",
        "default_summary": "Selected candidate is review-ready, not execution-authorized.",
        "detail_summary": "Candidate evidence is summarized for owner review without authorizing demo or live trading.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[5]), str(SOURCE_ARTIFACTS[6])],
        "criticality": "normal",
        "hidden_by_default_fields": ["candidate metrics", "rejected candidates", "selection reasons"],
    },
    {
        "emoji": "📊",
        "title": "Evidence",
        "short_label": "Evidence",
        "default_summary": "Evidence status is visible without raw-data overload.",
        "detail_summary": "Evidence depth, walk-forward sufficiency, and blockers stay inside detail panels.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[7]), str(SOURCE_ARTIFACTS[1])],
        "criticality": "normal",
        "hidden_by_default_fields": ["walk-forward counts", "evidence quality flags", "raw scoring"],
    },
    {
        "emoji": "🚧",
        "title": "Broker Boundary",
        "short_label": "Broker Boundary",
        "default_summary": "Broker connection proof is owner-gated and separate.",
        "detail_summary": "This dashboard reads local reports only and does not contact broker systems or inspect account state.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[3]), str(SOURCE_ARTIFACTS[4])],
        "criticality": "critical",
        "hidden_by_default_fields": ["owner input checklist", "protected boundary detail"],
    },
    {
        "emoji": "💰",
        "title": "Profit Readiness",
        "short_label": "Profit Readiness",
        "default_summary": "Profit readiness is display-only.",
        "detail_summary": "Profit readiness depends on governed evidence and owner review; it does not authorize demo/live action.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[5]), str(SOURCE_ARTIFACTS[6]), str(SOURCE_ARTIFACTS[7])],
        "criticality": "normal",
        "hidden_by_default_fields": ["profit factors", "drawdown metrics", "promotion blockers"],
    },
    {
        "emoji": "📁",
        "title": "Reports",
        "short_label": "Reports",
        "default_summary": "Report index for the local evidence used by this UI.",
        "detail_summary": "All source artifacts are local repo files. Heavy reports stay behind this detail window.",
        "source_artifacts": [str(path) for path in SOURCE_ARTIFACTS],
        "criticality": "normal",
        "hidden_by_default_fields": ["full artifact contents", "raw report dumps"],
    },
    {
        "emoji": "🆘",
        "title": "SOS",
        "short_label": "SOS",
        "default_summary": "Escalate only if protected boundaries are violated or source artifacts go missing.",
        "detail_summary": "This is a stop signal surface, not an alert sender or runtime notification system.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[1]), str(SOURCE_ARTIFACTS[3])],
        "criticality": "critical",
        "hidden_by_default_fields": ["full stop rules", "operator escalation detail"],
    },
    {
        "emoji": "⚙️",
        "title": "Settings",
        "short_label": "Settings",
        "default_summary": "Display preferences only; no execution controls.",
        "detail_summary": "Settings are visual/local only in this static HTML and do not persist or trigger actions.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[1]), str(SOURCE_ARTIFACTS[2])],
        "criticality": "low",
        "hidden_by_default_fields": ["visual preferences", "panel behavior notes"],
    },
    {
        "emoji": "🔒",
        "title": "Secrets Later",
        "short_label": "Secrets Later",
        "default_summary": "Bitwarden remains locked until owner confirmation after Forex 110.",
        "detail_summary": "Bitwarden, Vaultwarden, secrets migration, and token storage are not started by this packet.",
        "source_artifacts": [str(SOURCE_ARTIFACTS[0]), str(SOURCE_ARTIFACTS[1])],
        "criticality": "critical",
        "hidden_by_default_fields": ["future secret-manager planning", "owner confirmation requirements"],
    },
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _artifact_presence() -> tuple[dict[str, bool], list[str]]:
    present = {str(path): (REPO_ROOT / path).is_file() for path in SOURCE_ARTIFACTS}
    missing = [path for path, exists in present.items() if not exists]
    return present, missing


def run_forex_dashboard_runtime_ui_v1() -> dict[str, Any]:
    source_artifacts_present, missing_source_artifacts = _artifact_presence()
    forex_110_state = _read_json(SOURCE_ARTIFACTS[0]) if not missing_source_artifacts else {}
    forex_110_complete = bool(forex_110_state.get("forex_110_complete", False))
    dashboard_ready = forex_110_complete and not missing_source_artifacts

    result: dict[str, Any] = {
        "canonical_dashboard_id": CANONICAL_DASHBOARD_ID,
        "canonical_dashboard_surfaces": [CANONICAL_DASHBOARD_ID],
        "duplicate_dashboard_policy": DUPLICATE_DASHBOARD_POLICY,
        "owner_visual_design_required": True,
        "dashboard_visual_handoff_status": DASHBOARD_VISUAL_HANDOFF_STATUS,
        "no_alternate_dashboard_variants": True,
        "no_extra_dashboard_examples": True,
        "dashboard_package_files": DASHBOARD_PACKAGE_FILES,
        "dashboard_status": "FOREX_DASHBOARD_RUNTIME_UI_READY" if dashboard_ready else "FOREX_DASHBOARD_RUNTIME_UI_BLOCKED",
        "forex_110_complete": forex_110_complete,
        "source_artifacts_present": source_artifacts_present,
        "missing_source_artifacts": missing_source_artifacts,
        "runtime_ui_type": "STATIC_LOCAL_CLICKABLE_EMOJI_HTML",
        "html_preview_path": str(PREVIEW_PATH),
        "dashboard_windows": WINDOWS,
        "default_visible_summary": {
            "critical_status": "Forex 110% complete - broker/live work remains protected.",
            "active_blocker": "Broker, live, demo, secrets, Bitwarden, Vaultwarden, and background automation actions are blocked.",
            "next_safe_action": "Open the static local HTML preview and review display-only Forex state.",
            "safety_state": "Repo-safe local dashboard preview only.",
        },
        "hidden_detail_rules": HIDDEN_DETAIL_RULES,
        "critical_display_rules": CRITICAL_DISPLAY_RULES,
        "protected_boundary_summary": {
            "status": PROTECTED_BROKER_BOUNDARY_STATUS,
            "broker_contact": "blocked",
            "account_inspection": "blocked",
            "orders": "blocked",
            "demo_live_authorization": "blocked",
        },
        "protected_broker_boundary_status": PROTECTED_BROKER_BOUNDARY_STATUS,
        "bitwarden_lock_summary": {
            "bitwarden_unlocked": False,
            "status": BITWARDEN_STATUS,
            "vaultwarden_unlocked": False,
            "secrets_migration_allowed": False,
            "token_storage_allowed": False,
        },
        "bitwarden_status": BITWARDEN_STATUS,
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
        "packet_id": PACKET_ID,
    }
    result.update(PROTECTED_FLAGS)
    return result


def _list_items(items: list[str]) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in items)


def build_dashboard_html(result: dict[str, Any]) -> str:
    cards = []
    panels = []
    for index, window in enumerate(result["dashboard_windows"]):
        panel_id = f"panel-{index}"
        cards.append(
            f'<button class="window-card" type="button" data-panel="{panel_id}" aria-controls="{panel_id}">'
            f'<span class="emoji" aria-hidden="true">{window["emoji"]}</span>'
            f'<span class="card-title">{escape(window["title"])}</span>'
            f'<span class="card-summary">{escape(window["default_summary"])}</span>'
            "</button>"
        )
        panels.append(
            f'<section class="detail-panel" id="{panel_id}" tabindex="-1" hidden>'
            f'<h2>{window["emoji"]} {escape(window["title"])}</h2>'
            f'<p>{escape(window["detail_summary"])}</p>'
            f'<h3>Source Artifacts</h3><ul>{_list_items(window["source_artifacts"])}</ul>'
            f'<h3>Hidden By Default</h3><ul>{_list_items(window["hidden_by_default_fields"])}</ul>'
            f'<p class="criticality">Criticality: {escape(window["criticality"])}</p>'
            "</section>"
        )

    visible = result["default_visible_summary"]
    blocked_flags = [name for name, value in PROTECTED_FLAGS.items() if value is False]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Forex Dashboard Runtime UI V1</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #1f2933;
      --muted: #52616f;
      --line: #c8d2dc;
      --accent: #0f766e;
      --warn: #9a3412;
      --danger: #991b1b;
      --focus: #1d4ed8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    .shell {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}
    .banner {{
      padding: 14px 18px;
      border: 1px solid var(--line);
      background: var(--panel);
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .banner.primary {{ border-left: 8px solid var(--accent); }}
    .banner.locked {{ border-left: 8px solid var(--warn); }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .summary-box {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 14px;
      min-height: 120px;
    }}
    .summary-box strong {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 0.88rem;
      text-transform: uppercase;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(150px, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .window-card {{
      min-height: 176px;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      padding: 16px;
      text-align: left;
      cursor: pointer;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .window-card:hover,
    .window-card.active {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.16);
    }}
    .window-card:focus-visible {{
      outline: 3px solid var(--focus);
      outline-offset: 3px;
    }}
    .emoji {{ font-size: 2.4rem; line-height: 1; }}
    .card-title {{ font-weight: 700; font-size: 1.05rem; }}
    .card-summary {{ color: var(--muted); font-size: 0.94rem; }}
    .detail-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 8px solid var(--accent);
      padding: 18px;
      margin-top: 12px;
      border-radius: 8px;
    }}
    .detail-panel:focus {{ outline: 3px solid var(--focus); outline-offset: 3px; }}
    .criticality {{ color: var(--danger); font-weight: 700; }}
    .blocked {{
      background: #fff7ed;
      border: 1px solid #fed7aa;
      padding: 14px 18px;
      margin-top: 18px;
    }}
    code {{ overflow-wrap: anywhere; }}
    @media (max-width: 900px) {{
      .summary {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
      .shell {{ width: min(100% - 20px, 1180px); padding-top: 14px; }}
      .summary, .grid {{ grid-template-columns: 1fr; }}
      .window-card {{ min-height: 150px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <div class="banner primary">Forex 110% complete — broker/live work remains protected.</div>
    <div class="banner locked">Bitwarden locked until owner confirmation after Forex 110.</div>
    <section class="summary" aria-label="Default visible summary">
      <div class="summary-box"><strong>Critical Status</strong>{escape(visible["critical_status"])}</div>
      <div class="summary-box"><strong>Blockers</strong>{escape(visible["active_blocker"])}</div>
      <div class="summary-box"><strong>Next Safe Action</strong>{escape(visible["next_safe_action"])}</div>
      <div class="summary-box"><strong>Safety State</strong>{escape(visible["safety_state"])}</div>
    </section>
    <section class="grid" aria-label="Clickable dashboard windows">
      {"".join(cards)}
    </section>
    <section aria-live="polite">
      {"".join(panels)}
    </section>
    <section class="blocked">
      <h2>Protected Boundary</h2>
      <p>Broker contact, credentials, .env reads, account identifiers, account inspection, orders, demo/live authorization, scheduler, daemon, webhook, background loop, Bitwarden, Vaultwarden, secrets migration, and token storage are blocked.</p>
      <p>Protected false flags: {escape(", ".join(blocked_flags))}</p>
    </section>
  </main>
  <script>
    const cards = Array.from(document.querySelectorAll('.window-card'));
    const panels = Array.from(document.querySelectorAll('.detail-panel'));
    function showPanel(id) {{
      panels.forEach((panel) => {{ panel.hidden = panel.id !== id; }});
      cards.forEach((card) => {{ card.classList.toggle('active', card.dataset.panel === id); }});
      const active = document.getElementById(id);
      if (active) {{ active.focus(); }}
    }}
    cards.forEach((card) => {{
      card.addEventListener('click', () => showPanel(card.dataset.panel));
    }});
    if (cards[0]) {{ showPanel(cards[0].dataset.panel); }}
  </script>
</body>
</html>
"""


def build_report_markdown(result: dict[str, Any]) -> str:
    windows = "\n".join(
        f"- {window['emoji']} {window['title']}: {window['default_summary']}"
        for window in result["dashboard_windows"]
    )
    return f"""# AIOS Forex Dashboard Runtime UI V1 Report

Dashboard status: `{result["dashboard_status"]}`

Canonical dashboard ID: `{result["canonical_dashboard_id"]}`

Duplicate dashboard policy: `{result["duplicate_dashboard_policy"]}`

Dashboard visual handoff: `{result["dashboard_visual_handoff_status"]}`

Forex 110 complete: `{result["forex_110_complete"]}`

Runtime UI type: `{result["runtime_ui_type"]}`

HTML preview path: `{result["html_preview_path"]}`

## Windows

{windows}

## Default Visible Summary

- Critical status: {result["default_visible_summary"]["critical_status"]}
- Blockers: {result["default_visible_summary"]["active_blocker"]}
- Next safe action: {result["default_visible_summary"]["next_safe_action"]}
- Safety state: {result["default_visible_summary"]["safety_state"]}

## Protected Boundary

Broker/API, credentials, env reads, account identifiers, order execution, demo authorization, live authorization, scheduler, daemon, webhook, background loop, Bitwarden, Vaultwarden, secrets migration, and token storage all remain false.

Protected broker boundary status: `{result["protected_broker_boundary_status"]}`

Bitwarden status: `{result["bitwarden_status"]}`

## Missing Source Artifacts

{result["missing_source_artifacts"]}
"""


def build_docs_markdown(result: dict[str, Any]) -> str:
    windows = "\n".join(
        f"- {window['emoji']} **{window['title']}** - {window['default_summary']}"
        for window in result["dashboard_windows"]
    )
    return f"""# Forex Dashboard Runtime UI V1

This is a static, local, repo-safe dashboard preview for Forex 110 completion state.

Open `docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.html` or `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_PREVIEW.html` directly in a browser.

Canonical dashboard ID: `FOREX_DASHBOARD_RUNTIME_UI_V1`

Duplicate dashboard policy: `SINGLE_CANONICAL_SURFACE_ONLY`

Dashboard visual handoff: `HANDOFF_REQUIRED_BEFORE_FINAL_VISUAL_IMPLEMENTATION`

## Emoji Windows

{windows}

## Default View

The first view shows only critical status, blockers, next safe action, and safety state.

## Hidden Detail Windows

Raw report detail, validator-heavy data, metadata, broker-boundary detail, candidate metrics, and evidence detail stay behind clickable emoji windows.

## Protected Behavior

This UI reads local Forex report artifacts only. It has no broker contact, no credential handling, no env reads, no account identifiers, no account inspection, no order execution, no demo authorization, no live authorization, no scheduler, no daemon, no webhook, and no background loop.

## Bitwarden Boundary

Bitwarden and Vaultwarden remain locked. Secrets migration and token storage are not started by this dashboard.

## Forex 110 Relationship

This complements Forex 110 by turning the completed repo-safe evidence gate into a readable dashboard preview while preserving the protected broker/live/secrets boundary.

Status: `{result["dashboard_status"]}`
"""


def write_outputs(result: dict[str, Any]) -> None:
    outputs = {
        STATE_PATH: json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        REPORT_PATH: build_report_markdown(result),
        PREVIEW_PATH: build_dashboard_html(result),
        DOCS_PATH: build_docs_markdown(result),
        DOCS_HTML_PATH: build_dashboard_html(result),
    }
    for relative_path, content in outputs.items():
        path = REPO_ROOT / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
