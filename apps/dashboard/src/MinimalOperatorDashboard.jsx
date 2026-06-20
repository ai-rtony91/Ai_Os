import { useEffect, useMemo, useState } from "react";
import dashboardFixture from "../mock-data/aios-minimal-operator-dashboard-v1.example.json";
import aiosForexBotSymbolBanner from "./assets/aios-forex-bot-symbol-banner.png";
import "./MinimalOperatorDashboard.css";

const VIEWS = {
  HOME: "home",
  FOREX: "forex",
  WATCHLIST: "watchlist",
  DETAIL: "detail",
  SYSTEM: "system",
  SAFETY: "safety",
  SETTINGS: "settings",
  POSITION: "position",
  RISK: "risk",
  EXIT: "exit",
  HISTORY: "history",
  READINESS: "readiness"
};

const ICONS = {
  operator: "🎛️",
  forex: "🤖",
  system: "🖥️",
  safety: "🛡️",
  settings: "⚙️",
  watchlist: "🎯",
  position: "📍",
  risk: "📊",
  exit: "⏏️",
  history: "🧾",
  readiness: "🚦",
  detail: "🔎"
};

const SYSTEM_DETAIL_ITEMS = [
  {
    id: "dashboard",
    emoji: "📊",
    label: "DASHBOARD",
    value: "READY",
    tone: "good"
  },
  {
    id: "mode",
    emoji: "⚙️",
    label: "MODE",
    value: dashboardFixture.mode
  },
  {
    id: "data",
    emoji: "🧾",
    label: "DATA",
    value: dashboardFixture.source
  },
  {
    id: "broker",
    emoji: "🏦",
    label: "BROKER",
    value: dashboardFixture.bridges.brokerBridge
  },
  {
    id: "liveApis",
    emoji: "🔌",
    label: "LIVE APIS",
    value: "BLOCKED"
  }
];

const VIEW_LABELS = {
  [VIEWS.HOME]: "Operator",
  [VIEWS.FOREX]: "Forex Bot",
  [VIEWS.WATCHLIST]: "Watchlist",
  [VIEWS.DETAIL]: "Pair Detail",
  [VIEWS.SYSTEM]: "System",
  [VIEWS.SAFETY]: "Safety",
  [VIEWS.SETTINGS]: "Settings",
  [VIEWS.POSITION]: "Position",
  [VIEWS.RISK]: "Risk / P&L",
  [VIEWS.EXIT]: "Exit",
  [VIEWS.HISTORY]: "Trading History",
  [VIEWS.READINESS]: "Execution Readiness"
};

const VIEW_ICONS = {
  [VIEWS.HOME]: ICONS.operator,
  [VIEWS.FOREX]: ICONS.forex,
  [VIEWS.WATCHLIST]: ICONS.watchlist,
  [VIEWS.DETAIL]: ICONS.detail,
  [VIEWS.SYSTEM]: ICONS.system,
  [VIEWS.SAFETY]: ICONS.safety,
  [VIEWS.SETTINGS]: ICONS.settings,
  [VIEWS.POSITION]: ICONS.position,
  [VIEWS.RISK]: ICONS.risk,
  [VIEWS.EXIT]: ICONS.exit,
  [VIEWS.HISTORY]: ICONS.history,
  [VIEWS.READINESS]: ICONS.readiness
};

const FOREX_CHILD_VIEWS = new Set([
  VIEWS.WATCHLIST,
  VIEWS.DETAIL,
  VIEWS.POSITION,
  VIEWS.RISK,
  VIEWS.EXIT,
  VIEWS.HISTORY,
  VIEWS.READINESS
]);

const OPERATION_CONTRACTS = {
  watchlist: {
    cause: "Request latest available watchlist and opportunity snapshot from the AIOS read-model source.",
    effect: "Display ranked pairs, score, confidence, trend, source, freshness, and live-trading permission."
  },
  position: {
    cause: "Request broker/account position reconciliation read-model.",
    effect: "Display open position, units, entry price if available, realized P/L, unrealized P/L, freshness, and source."
  },
  risk: {
    cause: "Request risk governor and P/L truth read-model.",
    effect: "Display daily loss cap, max position size, realized P/L, unrealized P/L, risk status, and blocked/allowed state."
  },
  exit: {
    cause: "Request exit readiness and readiness-plan evaluation for any current open trade.",
    effect: "Display stop-loss, take-profit, trailing stop, max-time policy, auto-exit readiness, and block reason."
  },
  history: {
    cause: "Request sanitized closed-trade and execution-evidence read-model.",
    effect: "Display closed trades, realized P/L, exit reason, protection controls used, slippage, evidence status, source, and freshness."
  },
  readiness: {
    cause: "Request the live-capable execution readiness bridge projection.",
    effect: "Display live data, broker, signal, risk, exit, history-writeback, and arming-review gates with LIVE_READY, blockers, and next safe action."
  }
};

const FOREX_COMMAND_STATUSES = [
  { label: "LIVE", value: "BLOCKED", tone: "danger" },
  { label: "MODE", value: "DASHBOARD_ONLY", tone: "neutral" },
  { label: "BROKER", value: "NOT_CONNECTED", tone: "warn" },
  { label: "ORDER ROUTE", value: "DISABLED", tone: "danger" },
  { label: "CLOSE ROUTE", value: "DISABLED", tone: "danger" },
  { label: "AUTO TRADE", value: "OFF", tone: "warn" }
];

const FOREX_CRITICAL_INFO = [
  { label: "Selected pair", value: `${formatPair(dashboardFixture.selectedPair)} placeholder` },
  { label: "Setup quality", value: "PENDING SCAN" },
  { label: "Max loss", value: "APPROVAL REQUIRED" },
  { label: "Daily cap", value: "APPROVAL REQUIRED" },
  { label: "Stop-loss", value: "REQUIRED" },
  { label: "Final disarm", value: "REQUIRED" }
];

const FOREX_COMMAND_INTENTS = {
  GET_IN: "GET_IN",
  GET_OUT: "GET_OUT",
  ARM_DISARM: "ARM_DISARM",
  KILL_SWITCH: "KILL_SWITCH",
  PANIC_FLATTEN: "PANIC_FLATTEN",
  PAIR_SCANNER: "PAIR_SCANNER",
  CANDIDATE_FILTER: "CANDIDATE_FILTER",
  DEMO_CONNECTOR_PROOF: "DEMO_CONNECTOR_PROOF",
  RISK_GATE: "RISK_GATE",
  RECONCILIATION: "RECONCILIATION",
  AIOS_SIGNAL_STATUS: "AIOS_SIGNAL_STATUS"
};

const FOREX_COMMAND_CONTROLS = [
  {
    id: "get-in",
    intent: FOREX_COMMAND_INTENTS.GET_IN,
    icon: "🚀",
    label: "GET IN",
    state: "BLOCKED",
    mode: "TRADE_INTENT_BLOCKED",
    blockedReasons: [
      "live_execution_blocked",
      "broker_not_connected",
      "order_route_disabled",
      "risk_gate_not_approved",
      "human_approval_required"
    ],
    missingEvidence: [
      "protected live approval packet",
      "risk gate proof",
      "broker connection approval",
      "order route approval"
    ],
    nextSafeStep: "Next safe ladder step: PAPER ORDER PREVIEW.",
    message: "GET IN is blocked. Live order submission requires future protected Human Owner approval."
  },
  {
    id: "get-out",
    intent: FOREX_COMMAND_INTENTS.GET_OUT,
    icon: "🛑",
    label: "GET OUT",
    state: "BLOCKED",
    mode: "CLOSE_INTENT_BLOCKED",
    blockedReasons: [
      "close_route_disabled",
      "broker_not_connected",
      "final_disarm_required",
      "live_safe_close_packet_not_approved"
    ],
    missingEvidence: [
      "live-safe close packet approval",
      "final disarm proof",
      "broker connection approval",
      "close route approval"
    ],
    nextSafeStep: "Next safe ladder step: RECONCILIATION / FINAL DISARM. Close execution remains disabled.",
    message: "GET OUT is blocked. Close routes are disabled and no live position action exists here."
  },
  {
    id: "arm-disarm",
    intent: FOREX_COMMAND_INTENTS.ARM_DISARM,
    icon: "🟣",
    label: "ARM / DISARM",
    state: "LOCAL ONLY",
    mode: "ARMING_REVIEW",
    blockedReasons: ["future_protected_approval_required", "final_disarm_required"],
    missingEvidence: ["fresh Human Owner approval", "final disarm proof"],
    nextSafeStep: "Review arming status locally; do not arm live execution from the dashboard.",
    message: "Arm/disarm selection is dashboard-only. Final disarm remains required before any future review."
  },
  {
    id: "kill-switch",
    intent: FOREX_COMMAND_INTENTS.KILL_SWITCH,
    icon: "☠️",
    label: "KILL SWITCH",
    state: "VISIBLE",
    mode: "LOCAL_EMERGENCY",
    emergency: true,
    blockedReasons: ["no_broker_call_sent", "no_order_sent", "no_close_sent"],
    missingEvidence: ["approved kill-switch backend wiring", "broker/manual path confirmation"],
    nextSafeStep: "Use the approved broker/manual path until execution wiring exists.",
    message: "Kill switch is visible as an operator control surface marker. It does not call a broker."
  },
  {
    id: "panic-flatten",
    intent: FOREX_COMMAND_INTENTS.PANIC_FLATTEN,
    icon: "🚨",
    label: "PANIC FLATTEN / EMERGENCY EXIT",
    state: "PLACEHOLDER",
    mode: "LOCAL_EMERGENCY",
    emergency: true,
    blockedReasons: ["close_route_disabled", "no_broker_call_sent", "no_order_sent", "no_close_sent"],
    missingEvidence: ["approved emergency close route", "live-safe close packet approval"],
    nextSafeStep: "Use the approved broker/manual path until execution wiring exists.",
    message: "Emergency exit is a placeholder. No close-trade action, order route, or broker write path is wired."
  },
  {
    id: "pair-scanner",
    intent: FOREX_COMMAND_INTENTS.PAIR_SCANNER,
    icon: "🔎",
    label: "Pair Scanner",
    state: "VIEW",
    mode: "SCANNER",
    blockedReasons: ["scanner_is_dashboard_only", "live_execution_blocked"],
    missingEvidence: ["safe backend status/API feed"],
    nextSafeStep: "Use the local watchlist read-model and wire safe backend status/API next.",
    message: "Pair scanner points the operator toward the local watchlist read-model only."
  },
  {
    id: "demo-connector-proof",
    intent: FOREX_COMMAND_INTENTS.DEMO_CONNECTOR_PROOF,
    icon: "🧪",
    label: "DEMO CONNECTOR PROOF",
    state: "PARTIAL",
    mode: "STATUS_ONLY_NO_CONNECTOR_CALL",
    blockedReasons: [
      "value_free_callable_handle_missing",
      "sanitized_terminal_demo_result_missing",
      "broker_demo_connector_proof_not_complete"
    ],
    missingEvidence: [
      "value-free callable connector handle",
      "practice/demo-only proof",
      "sanitized terminal proof result"
    ],
    nextSafeStep: "Supply value-free callable handle; keep Codex and repo away from broker values.",
    message: "Demo connector proof is a local status intent. No connector call, broker call, or market data request is sent."
  },
  {
    id: "candidate-filter",
    intent: FOREX_COMMAND_INTENTS.CANDIDATE_FILTER,
    icon: "🧪",
    label: "Candidate Filter",
    state: "VIEW",
    mode: "FILTER",
    blockedReasons: ["candidate_filter_is_dashboard_only", "live_execution_blocked"],
    missingEvidence: ["safe candidate status feed", "approved risk-gate evidence"],
    nextSafeStep: "Filter candidates locally, then connect safe backend status/API in a later packet.",
    message: "Candidate filter is a local dashboard mode marker for reviewing candidates."
  },
  {
    id: "risk-gate",
    intent: FOREX_COMMAND_INTENTS.RISK_GATE,
    icon: "🛡️",
    label: "Risk Gate",
    state: "REQUIRED",
    mode: "RISK",
    blockedReasons: ["risk_gate_not_approved", "max_loss_not_final", "daily_cap_not_final"],
    missingEvidence: ["max loss proof", "daily cap proof", "stop-loss proof"],
    nextSafeStep: "Review local risk fields and keep live trade submission blocked.",
    message: "Risk gate remains required. Max loss, daily cap, and stop-loss proof are not execution wiring."
  },
  {
    id: "reconciliation",
    intent: FOREX_COMMAND_INTENTS.RECONCILIATION,
    icon: "🧾",
    label: "Reconciliation",
    state: "REQUIRED",
    mode: "RECONCILIATION",
    blockedReasons: ["broker_readonly_evidence_required", "account_values_not_loaded"],
    missingEvidence: ["sanitized read-only account evidence", "sanitized position/P&L/margin evidence"],
    nextSafeStep: "Collect sanitized read-only evidence and keep private broker data out of the dashboard.",
    message: "Reconciliation is a read-only evidence status marker. It does not access accounts or broker payloads."
  },
  {
    id: "signal-status",
    intent: FOREX_COMMAND_INTENTS.AIOS_SIGNAL_STATUS,
    icon: "🤖",
    label: "AIOS Signal Status",
    state: "WATCHING",
    mode: "SIGNAL_STATUS",
    blockedReasons: ["signal_is_dashboard_only", "live_execution_blocked"],
    missingEvidence: ["safe signal status feed", "paper/demo proof path"],
    nextSafeStep: "Watch AIOS signal status locally and wire safe backend status/API next.",
    message: "AIOS signal status is dashboard-only and cannot submit a live trade from this screen."
  }
];

const FOREX_NEXT_SAFE_STEPS = [
  "Design landed",
  "Command surface visible",
  "Intent state local only",
  "Next: wire dashboard to safe backend status/API"
];

const AIOS_TRADING_LADDER = [
  { label: "UI", value: "ACTIVE", tone: "good" },
  { label: "Paper", value: "NEXT", tone: "neutral" },
  { label: "Demo Read-Only", value: "NEXT", tone: "neutral" },
  { label: "One-Shot Live", value: "PROTECTED", tone: "warn" },
  { label: "Auto Live", value: "FUTURE", tone: "danger" }
];

const PAPER_SANDBOX_PATHWAY_STEPS = [
  { label: "Paper Preview", value: "READY_NEXT", tone: "good" },
  { label: "Sandbox/Demo", value: "NOT_CONNECTED", tone: "warn" },
  { label: "Live One-Shot", value: "PROTECTED", tone: "warn" },
  { label: "Auto Live", value: "FUTURE_BLOCKED", tone: "danger" }
];

const PAPER_SANDBOX_CRITICAL_STRIP = [
  "LIVE BLOCKED",
  "PAPER NEXT",
  "SANDBOX NEXT",
  "BROKER NOT CONNECTED",
  "ORDER ROUTE DISABLED",
  "CLOSE ROUTE DISABLED"
];

const PAPER_ORDER_PREVIEW_ROWS = [
  { label: "Pair", value: `${formatPair(dashboardFixture.selectedPair)} placeholder` },
  { label: "Side", value: "BUY/SELL placeholder" },
  { label: "Units", value: "1 micro / placeholder" },
  { label: "Stop Loss", value: "REQUIRED" },
  { label: "Take Profit", value: "NOT SET / placeholder" },
  { label: "Max Loss", value: "REQUIRED" },
  { label: "Status", value: "PREVIEW_ONLY_NO_ORDER_SENT" }
];

const SANDBOX_DRY_RUN_ROWS = [
  { label: "Selection", value: "SANDBOX_DRY_RUN_SELECTED" },
  { label: "Broker", value: "broker_not_connected" },
  { label: "Order route", value: "no_order_route" },
  { label: "Close route", value: "no_close_route" },
  { label: "Live execution", value: "no_live_execution" }
];

const AIOS_FOREX_BRAND_PILLS = [
  "⚡ SIGNAL",
  "📡 TOWER",
  "🌐 GLOBAL",
  "💎 CAPITAL"
];

const SAFE_DASHBOARD_STATUS_ENDPOINTS = [
  { id: "api-health", label: "/api/health", path: "/api/health" },
  { id: "runtime-status", label: "/api/runtime/status", path: "/api/runtime/status" },
  { id: "runtime-health", label: "/api/runtime/health", path: "/api/runtime/health" },
  { id: "runtime-visibility", label: "/api/runtime/visibility", path: "/api/runtime/visibility" },
  { id: "runtime-control", label: "/api/runtime/control", path: "/api/runtime/control" },
  {
    id: "forex-paper-sandbox-status",
    label: "/api/forex/paper-sandbox/status",
    path: "/api/forex/paper-sandbox/status"
  },
  {
    id: "forex-paper-order-preview",
    label: "/api/forex/paper-sandbox/order-preview",
    path: "/api/forex/paper-sandbox/order-preview"
  },
  {
    id: "forex-six-bullet-status",
    label: "/api/forex/six-bullet/status",
    path: "/api/forex/six-bullet/status"
  },
  {
    id: "forex-risk-gate-status",
    label: "/api/forex/risk-gate/status",
    path: "/api/forex/risk-gate/status"
  },
  {
    id: "forex-approval-package-status",
    label: "/api/forex/approval-package/status",
    path: "/api/forex/approval-package/status"
  },
  {
    id: "forex-reconciliation-status",
    label: "/api/forex/reconciliation/status",
    path: "/api/forex/reconciliation/status"
  },
  {
    id: "forex-demo-connector-proof-status",
    label: "/api/forex/demo-connector/proof-status",
    path: "/api/forex/demo-connector/proof-status"
  },
  {
    id: "forex-demo-connector-proof-intake-sample",
    label: "/api/forex/demo-connector/proof-intake/sample",
    path: "/api/forex/demo-connector/proof-intake/sample"
  }
];

const SAFE_STATUS_SUMMARY_KEYS = [
  "status",
  "state",
  "mode",
  "preview_status",
  "selected_pair",
  "side",
  "units",
  "order_type",
  "paper_preview_ready",
  "sandbox_demo_connected",
  "live_execution_allowed",
  "broker_connected",
  "order_route_enabled",
  "close_route_enabled",
  "auto_trade_enabled",
  "stop_loss_required",
  "take_profit_required",
  "max_loss_required",
  "order_sent",
  "trade_placed",
  "bullet",
  "proof_mode",
  "intake_status",
  "can_close_bullet_b",
  "sample_only",
  "broker_call_sent",
  "connector_handle_present",
  "connector_handle_required",
  "practice_demo_only_required",
  "sanitized_terminal_result_required",
  "credentials_allowed",
  "account_ids_allowed",
  "endpoint_values_allowed",
  "raw_broker_payloads_allowed",
  "market_data_allowed",
  "retry_loop_enabled",
  "scheduler_enabled",
  "daemon_enabled",
  "done_count",
  "partial_count",
  "next_target",
  "no_live_authority",
  "risk_gate_status",
  "approval_package_status",
  "reconciliation_status",
  "A_EXTERNAL_CREDENTIAL_ACCOUNT_BOUNDARY",
  "B_PROTECTED_BROKER_DEMO_RUNTIME_CONNECTOR_PROOF",
  "C_LIVE_ENDPOINT_DENIAL_PRACTICE_DEMO_ALLOWLIST_PROOF",
  "D_RISK_CAP_KILL_SWITCH_FINAL_DISARM_PROOF",
  "E_HUMAN_OWNER_LIVE_MICRO_TRADE_APPROVAL_PACKAGE",
  "F_POST_TRADE_JOURNAL_RECONCILIATION_PROOF",
  "human_owner_required",
  "daily_loss_cap_required",
  "kill_switch_required",
  "final_disarm_required",
  "broker_read_only_evidence_required",
  "closed_history_writeback_required",
  "next_safe_step",
  "ok",
  "healthy",
  "running",
  "runtimeStatus",
  "runtime_status",
  "health",
  "visibility",
  "control",
  "sourcePath",
  "updatedAt",
  "updated_at",
  "generatedAt",
  "generated_at",
  "timestamp"
];

const FOREX_PAPER_SANDBOX_BACKEND_STATUS_ROWS = [
  { label: "📄 PAPER PREVIEW", value: "READY", tone: "good" },
  { label: "🧪 SANDBOX/DEMO", value: "NOT CONNECTED", tone: "warn" },
  { label: "🛑 LIVE", value: "BLOCKED", tone: "danger" },
  { label: "🏦 BROKER", value: "NOT CONNECTED", tone: "warn" },
  { label: "🚦 ORDER ROUTE", value: "DISABLED", tone: "danger" },
  { label: "⏏️ CLOSE ROUTE", value: "DISABLED", tone: "danger" },
  { label: "🤖 AUTO TRADE", value: "OFF", tone: "warn" }
];

const FOREX_SIX_BULLET_BOARD_ROWS = [
  {
    bullet: "A",
    label: "Credential Boundary",
    key: "A_EXTERNAL_CREDENTIAL_ACCOUNT_BOUNDARY",
    fallback: "DONE"
  },
  {
    bullet: "B",
    label: "Demo Connector Proof",
    key: "B_PROTECTED_BROKER_DEMO_RUNTIME_CONNECTOR_PROOF",
    fallback: "PARTIAL"
  },
  {
    bullet: "C",
    label: "Live Denial / Demo Allowlist",
    key: "C_LIVE_ENDPOINT_DENIAL_PRACTICE_DEMO_ALLOWLIST_PROOF",
    fallback: "DONE"
  },
  {
    bullet: "D",
    label: "Risk / Kill / Disarm",
    key: "D_RISK_CAP_KILL_SWITCH_FINAL_DISARM_PROOF",
    fallback: "PARTIAL"
  },
  {
    bullet: "E",
    label: "Owner Approval Package",
    key: "E_HUMAN_OWNER_LIVE_MICRO_TRADE_APPROVAL_PACKAGE",
    fallback: "PARTIAL"
  },
  {
    bullet: "F",
    label: "Journal / Reconciliation",
    key: "F_POST_TRADE_JOURNAL_RECONCILIATION_PROOF",
    fallback: "PARTIAL"
  }
];

function normalizeDataSourceType(value) {
  const text = String(value ?? "").toUpperCase();

  if (text.includes("FIXTURE") || text.includes("STALE") || text.includes("UNVERIFIED")) {
    return "fixture";
  }

  if (text.includes("PAPER") || text.includes("DEMO")) {
    return "paper";
  }

  if (text.includes("BROKER") && text.includes("EXECUTION")) {
    return "broker-live-execution";
  }

  if (text.includes("LIVE") || text.includes("BROKER")) {
    return "broker-live-read-only";
  }

  return "fixture";
}

function statusTone(value) {
  const text = String(value ?? "").toUpperCase();

  if (text.includes("BLOCKED") || text.includes("MISSING") || text.includes("FALSE")) {
    return "danger";
  }

  if (
    text.includes("FIXTURE") ||
    text.includes("LOCKED") ||
    text.includes("REVIEW") ||
    text.includes("NEUTRAL")
  ) {
    return "warn";
  }

  if (
    text.includes("PRESENT") ||
    text.includes("BULLISH") ||
    text.includes("READY") ||
    text.includes("READ_ONLY")
  ) {
    return "good";
  }

  return "neutral";
}

function isSafePlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function safePrimitiveText(value) {
  if (typeof value === "string") {
    return value.slice(0, 84);
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  return null;
}

function findSafeValue(payload, key) {
  if (!isSafePlainObject(payload)) {
    return undefined;
  }

  if (Object.prototype.hasOwnProperty.call(payload, key)) {
    return payload[key];
  }

  for (const containerKey of ["runtime", "health", "visibility", "control", "summary", "status", "bullets"]) {
    const nested = payload[containerKey];
    if (isSafePlainObject(nested) && Object.prototype.hasOwnProperty.call(nested, key)) {
      return nested[key];
    }
  }

  return undefined;
}

function summarizeSafeStatusPayload(payload) {
  const primitivePayload = safePrimitiveText(payload);
  if (primitivePayload) {
    return [{ label: "response", value: primitivePayload }];
  }

  if (!isSafePlainObject(payload)) {
    return [{ label: "response", value: "NO_SAFE_SUMMARY" }];
  }

  const rows = [];
  for (const key of SAFE_STATUS_SUMMARY_KEYS) {
    const safeText = safePrimitiveText(findSafeValue(payload, key));
    if (safeText) {
      rows.push({ label: key, value: safeText });
    }

    if (rows.length >= 4) {
      break;
    }
  }

  return rows.length > 0 ? rows : [{ label: "response", value: "JSON_RECEIVED" }];
}

function collectSafeStatusFields(payload) {
  if (!isSafePlainObject(payload)) {
    return {};
  }

  return SAFE_STATUS_SUMMARY_KEYS.reduce((fields, key) => {
    const safeText = safePrimitiveText(findSafeValue(payload, key));
    if (safeText) {
      fields[key] = safeText;
    }

    return fields;
  }, {});
}

async function readSafeStatusBody(response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (!contentType.toLowerCase().includes("application/json")) {
    return { status: response.statusText || "NON_JSON_RESPONSE" };
  }

  try {
    return await response.json();
  } catch {
    return { status: "JSON_PARSE_FAILED" };
  }
}

async function fetchSafeDashboardStatusEndpoint(endpoint, signal) {
  try {
    const response = await fetch(endpoint.path, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      method: "GET",
      signal
    });
    const payload = await readSafeStatusBody(response);

    return {
      ...endpoint,
      httpStatus: response.status,
      ok: response.ok,
      safeFields: collectSafeStatusFields(payload),
      summary: summarizeSafeStatusPayload(payload)
    };
  } catch (error) {
    return {
      ...endpoint,
      httpStatus: "UNAVAILABLE",
      ok: false,
      safeFields: {},
      summary: [
        {
          label: "status",
          value: error?.name === "AbortError" ? "TIMEOUT_OR_ABORTED" : "NO_CONNECTION"
        }
      ]
    };
  }
}

function safeEndpointField(endpointResult, key, fallback) {
  if (!endpointResult?.ok) {
    return fallback;
  }

  return endpointResult.safeFields?.[key] ?? fallback;
}

function statusText(value) {
  return String(value ?? "")
    .replaceAll("_", " ")
    .toUpperCase();
}

function requiredText(value) {
  return String(value).toLowerCase() === "true" ? "REQUIRED" : "NOT REQUIRED";
}

function yesNoText(value) {
  return String(value).toLowerCase() === "true" ? "YES" : "NO";
}

function liveExecutionText(value) {
  return String(value).toLowerCase() === "true" ? "ALLOWED" : "BLOCKED";
}

function enabledDisabledText(value) {
  return String(value).toLowerCase() === "true" ? "ENABLED" : "DISABLED";
}

function buildPaperOrderPreviewEngineRows(endpointResult) {
  const pair = safeEndpointField(endpointResult, "selected_pair", "EUR_USD");
  const side = safeEndpointField(endpointResult, "side", "BUY");
  const units = safeEndpointField(endpointResult, "units", "1");
  const orderType = statusText(safeEndpointField(endpointResult, "order_type", "MARKET_PREVIEW_ONLY"));
  const stopLoss = requiredText(safeEndpointField(endpointResult, "stop_loss_required", "true"));
  const maxLoss = requiredText(safeEndpointField(endpointResult, "max_loss_required", "true"));
  const orderSent = yesNoText(safeEndpointField(endpointResult, "order_sent", "false"));
  const live = liveExecutionText(safeEndpointField(endpointResult, "live_execution_allowed", "false"));

  return [
    { label: "PAIR", value: pair, tone: "good" },
    { label: "SIDE", value: side, tone: "good" },
    { label: "UNITS", value: units, tone: "good" },
    { label: "TYPE", value: orderType, tone: "warn" },
    { label: "STOP LOSS", value: stopLoss, tone: "warn" },
    { label: "MAX LOSS", value: maxLoss, tone: "warn" },
    { label: "ORDER SENT", value: orderSent, tone: "danger" },
    { label: "LIVE", value: live, tone: "danger" }
  ];
}

function buildPaperOrderPreviewRows(endpointResult) {
  if (!endpointResult?.ok) {
    return PAPER_ORDER_PREVIEW_ROWS;
  }

  const orderSent = yesNoText(safeEndpointField(endpointResult, "order_sent", "false"));
  const status = orderSent === "YES" ? "BLOCKED_UNEXPECTED_ORDER_STATE" : "PREVIEW_ONLY_NO_ORDER_SENT";

  return [
    { label: "Pair", value: safeEndpointField(endpointResult, "selected_pair", "EUR_USD") },
    { label: "Side", value: safeEndpointField(endpointResult, "side", "BUY") },
    { label: "Units", value: safeEndpointField(endpointResult, "units", "1") },
    { label: "Stop Loss", value: requiredText(safeEndpointField(endpointResult, "stop_loss_required", "true")) },
    {
      label: "Take Profit",
      value:
        String(safeEndpointField(endpointResult, "take_profit_required", "false")).toLowerCase() === "true"
          ? "REQUIRED"
          : "NOT SET / placeholder"
    },
    { label: "Max Loss", value: requiredText(safeEndpointField(endpointResult, "max_loss_required", "true")) },
    { label: "Status", value: status }
  ];
}

function completionStatusTone(value) {
  const text = String(value ?? "").toUpperCase();
  if (text === "DONE" || text === "SAFE" || text === "YES") {
    return "good";
  }

  if (text.includes("PARTIAL") || text.includes("REQUIRED") || text.includes("NOT CURRENT")) {
    return "warn";
  }

  if (text.includes("BLOCKED") || text.includes("FALSE") || text.includes("NO")) {
    return "danger";
  }

  return "neutral";
}

function buildForexCompletionStatusCards({
  sixBulletResult,
  riskGateResult,
  approvalPackageResult,
  reconciliationResult
}) {
  return [
    {
      title: "Six Bullet Status",
      endpointResult: sixBulletResult,
      rows: [
        { label: "DONE", value: safeEndpointField(sixBulletResult, "done_count", "2"), tone: "good" },
        { label: "PARTIAL", value: safeEndpointField(sixBulletResult, "partial_count", "4"), tone: "warn" },
        { label: "LIVE", value: liveExecutionText(safeEndpointField(sixBulletResult, "live_execution_allowed", "false")), tone: "danger" },
        { label: "SAFE", value: yesNoText(safeEndpointField(sixBulletResult, "no_live_authority", "true")), tone: "good" }
      ]
    },
    {
      title: "Risk Gate",
      endpointResult: riskGateResult,
      rows: [
        { label: "STATUS", value: statusText(safeEndpointField(riskGateResult, "risk_gate_status", "BLOCKED_PENDING_APPROVAL")), tone: "danger" },
        { label: "STOP LOSS", value: requiredText(safeEndpointField(riskGateResult, "stop_loss_required", "true")), tone: "warn" },
        { label: "FINAL DISARM", value: requiredText(safeEndpointField(riskGateResult, "final_disarm_required", "true")), tone: "warn" },
        { label: "LIVE", value: liveExecutionText(safeEndpointField(riskGateResult, "live_execution_allowed", "false")), tone: "danger" }
      ]
    },
    {
      title: "Approval Package",
      endpointResult: approvalPackageResult,
      rows: [
        { label: "STATUS", value: statusText(safeEndpointField(approvalPackageResult, "approval_package_status", "NOT_CURRENT")), tone: "warn" },
        { label: "OWNER", value: requiredText(safeEndpointField(approvalPackageResult, "human_owner_required", "true")), tone: "warn" },
        { label: "TIMESTAMP", value: requiredText(safeEndpointField(approvalPackageResult, "absolute_timestamp_required", "true")), tone: "warn" },
        { label: "LIVE", value: liveExecutionText(safeEndpointField(approvalPackageResult, "live_execution_allowed", "false")), tone: "danger" }
      ]
    },
    {
      title: "Reconciliation",
      endpointResult: reconciliationResult,
      rows: [
        { label: "STATUS", value: statusText(safeEndpointField(reconciliationResult, "reconciliation_status", "PARTIAL")), tone: "warn" },
        { label: "READ-ONLY", value: requiredText(safeEndpointField(reconciliationResult, "broker_read_only_evidence_required", "true")), tone: "warn" },
        { label: "FINAL DISARM", value: requiredText(safeEndpointField(reconciliationResult, "final_disarm_required", "true")), tone: "warn" },
        { label: "LIVE", value: liveExecutionText(safeEndpointField(reconciliationResult, "live_execution_allowed", "false")), tone: "danger" }
      ]
    }
  ];
}

function viewLabel(view) {
  return VIEW_LABELS[view] ?? "Dashboard";
}

function viewIcon(view) {
  return VIEW_ICONS[view] ?? ICONS.operator;
}

function BackButton({ onClick }) {
  return (
    <button aria-label="Back" className="backButton iconOnlyButton" title="Back" type="button" onClick={onClick}>
      <span aria-hidden="true">←</span>
    </button>
  );
}

function formatPair(pair) {
  return String(pair ?? "UNKNOWN").replace("_", "/");
}

function formatTime(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function formatFreshness(source) {
  const timestamp = source?.timestamp ? formatTime(source.timestamp) : "UNKNOWN";
  const staleness = Number.isFinite(source?.stalenessSeconds)
    ? `${source.stalenessSeconds}s`
    : "UNKNOWN";

  return `${timestamp} / ${staleness}`;
}

function chartPolyline(points) {
  if (!Array.isArray(points) || points.length === 0) {
    return "";
  }

  const width = 340;
  const height = 132;
  const pad = 14;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const spread = max - min || 1;

  return points
    .map((point, index) => {
      const x = pad + (index * (width - pad * 2)) / Math.max(points.length - 1, 1);
      const y = height - pad - ((point - min) / spread) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function StatusBadge({ value }) {
  return <span className={`statusBadge status-${statusTone(value)}`}>{value}</span>;
}

function ReadinessRow({ label, value, tone }) {
  const displayValue = typeof value === "boolean" ? String(value) : value;

  return (
    <div className="field readinessField">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(displayValue)}`}>{displayValue}</strong>
    </div>
  );
}

function dataSourceForPair(pair) {
  const dataSource = dashboardFixture.dataSource ?? {};

  return {
    label:
      pair?.explanation?.dataSourceLabel ??
      dataSource.DISPLAY_LABEL ??
      dashboardFixture.source ??
      "UNVERIFIED",
    liveTradingAllowed:
      pair?.explanation?.liveTradingAllowedFromThisData ??
      dataSource.LIVE_TRADING_ALLOWED_FROM_THIS_DATA ??
      false,
    blockReason:
      pair?.explanation?.blockReason ??
      dataSource.BLOCK_REASON ??
      "Source permission is not approved for live trade decisions.",
    timestamp: pair?.lastUpdated ?? dataSource.DATA_TIMESTAMP_UTC ?? dashboardFixture.generatedAt,
    stalenessSeconds: dataSource.DATA_STALENESS_SECONDS
  };
}

function DataLabel({ source, compact = false }) {
  const liveAllowed = Boolean(source?.liveTradingAllowed);

  return (
    <div className={`dataLabel ${compact ? "compactLabel" : ""}`}>
      <StatusBadge value={source?.label ?? "UNVERIFIED"} />
      <span>{`Freshness: ${formatFreshness(source)}`}</span>
      <span>{`LIVE_TRADING_ALLOWED_FROM_THIS_DATA: ${String(liveAllowed)}`}</span>
      {!compact && !liveAllowed ? (
        <small>{source?.blockReason ?? "Data is blocked for live decisions."}</small>
      ) : null}
    </div>
  );
}

function buildReadOnlyBridgeStatus() {
  const bridge = dashboardFixture.readOnlyLiveDataBridge ?? {};
  const dataSource = dashboardFixture.dataSource ?? {};
  const brokerState = bridge.broker_state ?? {};
  const positions = bridge.positions ?? {};
  const riskPl = bridge.risk_pl ?? {};
  const tradingHistory = bridge.trading_history ?? {};
  const executionReadiness = bridge.execution_readiness ?? {};
  const sourceType =
    bridge.source_type ??
    normalizeDataSourceType(dataSource.DATA_SOURCE_TYPE ?? dashboardFixture.source);
  const sourceLabel =
    bridge.source_label ??
    dataSource.DISPLAY_LABEL ??
    dashboardFixture.source ??
    "NO_READ_MODEL_AVAILABLE";
  const blockReason =
    bridge.block_reason ??
    dataSource.BLOCK_REASON ??
    "No sanitized read-only live data bridge model is loaded.";

  return {
    sourceType,
    sourceLabel,
    freshnessUtc: bridge.freshness_utc ?? dataSource.DATA_TIMESTAMP_UTC ?? dashboardFixture.generatedAt,
    staleStatus: bridge.stale_status ?? dataSource.MARKET_DATA_STATUS ?? "BLOCKED",
    brokerReachable: brokerState.account_reachable ?? false,
    positionsReconciled: positions.positions_reconciled ?? false,
    plAvailable: riskPl.daily_pl_available ?? false,
    tradingHistoryAvailable: tradingHistory.trading_history_available ?? false,
    liveExecutionAllowed: false,
    nextSafeAction:
      executionReadiness.next_safe_action ??
      "run read-only live data bridge.",
    blockReason
  };
}

function bridgeDataLabelSource() {
  const bridge = buildReadOnlyBridgeStatus();

  return {
    label: bridge.sourceLabel,
    liveTradingAllowed: false,
    blockReason: bridge.blockReason,
    timestamp: bridge.freshnessUtc,
    stalenessSeconds: undefined
  };
}

function buildPaperLoopStatus() {
  const loop = dashboardFixture.paperSignalExecutionLoop ?? {};
  const dashboardStatus = loop.dashboard_status ?? {};
  const history = loop.trading_history ?? {};
  const reconciliation = loop.reconciliation ?? {};
  const historyRows = Array.isArray(history.history_rows) ? history.history_rows : [];
  const latestRow = historyRows[0] ?? {};
  const paperLoopAvailable =
    dashboardStatus.PAPER_LOOP_AVAILABLE ??
    loop.PAPER_LOOP_AVAILABLE ??
    history.trading_history_row_written ??
    false;

  return {
    paperLoopAvailable,
    lastPaperSignal:
      dashboardStatus.last_paper_signal ??
      loop.signal_side ??
      "UNAVAILABLE",
    lastPaperTradeStatus:
      dashboardStatus.last_paper_trade_status ??
      reconciliation.paper_trade_status ??
      "NO_PAPER_LOOP_READ_MODEL",
    lastPaperRealizedPl:
      dashboardStatus.last_paper_realized_pl ??
      reconciliation.realized_paper_pl ??
      loop.realized_paper_pl ??
      "UNAVAILABLE",
    historyWritebackStatus:
      dashboardStatus.history_writeback_status ??
      (paperLoopAvailable ? "PAPER_HISTORY_WRITTEN" : "PAPER_HISTORY_UNAVAILABLE"),
    liveExecutionAllowed: false,
    evidencePath:
      loop.evidence_path ??
      history.evidence_path ??
      "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md",
    sourceLabel:
      loop.source_label ??
      latestRow.source_label ??
      "PAPER_SIMULATION_STATUS",
    freshnessUtc:
      loop.freshness_utc ??
      latestRow.freshness_utc ??
      dashboardFixture.generatedAt,
    nextSafeAction:
      dashboardStatus.next_safe_action ??
      loop.next_safe_action ??
      "run paper signal execution loop.",
    blockReason: paperLoopAvailable
      ? "Paper loop evidence is available for review only; live execution remains blocked."
      : "No sanitized paper loop read-model is loaded."
  };
}

function paperLoopDataLabelSource() {
  const paperLoop = buildPaperLoopStatus();

  return {
    label: paperLoop.sourceLabel,
    liveTradingAllowed: false,
    blockReason: paperLoop.blockReason,
    timestamp: paperLoop.freshnessUtc,
    stalenessSeconds: undefined
  };
}

function buildArmingGateStatus() {
  const gate = dashboardFixture.liveMicroTradeArmingGate ?? {};
  const blockedReasons = Array.isArray(gate.blocked_reasons)
    ? gate.blocked_reasons
    : [
        "read_only_source_not_live_tradable_or_not_valid",
        "broker_account_not_reachable",
        "positions_not_reconciled",
        "daily_pl_not_available",
        "real_trading_history_unavailable_or_blocked",
        "required_human_phrase_not_provided"
      ];

  return {
    liveArmable: gate.LIVE_ARMABLE ?? false,
    liveExecutionAllowed: false,
    requiredHumanPhrase:
      gate.required_human_phrase ??
      "I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW",
    blockedReasons,
    nextSafeAction:
      gate.next_safe_action ??
      "Resolve arming blockers, review evidence, and keep live execution blocked until a separate approved one-shot execution packet exists.",
    nextPacketCandidate:
      gate.next_packet_candidate ??
      "AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1",
    sourceLabel: gate.source_label ?? "LIVE_ARMING_GATE_REVIEW_ONLY",
    freshnessUtc: gate.generated_at_utc ?? dashboardFixture.generatedAt,
    blockReason:
      blockedReasons.length > 0
        ? blockedReasons.join("; ")
        : "Arming review has no blockers, but execution still requires a separate packet."
  };
}

function armingGateDataLabelSource() {
  const armingGate = buildArmingGateStatus();

  return {
    label: armingGate.sourceLabel,
    liveTradingAllowed: false,
    blockReason: armingGate.blockReason,
    timestamp: armingGate.freshnessUtc,
    stalenessSeconds: undefined
  };
}

function buildExecutionReviewStatus() {
  return {
    dataLabel: "EXECUTION_REVIEW_DRY_RUN",
    executionReviewReady: false,
    liveExecutionAllowed: false,
    liveTradePlaced: false,
    requiredHumanPhrase:
      "I AUTHORIZE ONE LIVE MICRO TRADE EXECUTION WITH MAXIMUM MICRO RISK",
    evidencePresent: [
      "read-only bridge evidence evaluated when report is available",
      "paper loop evidence evaluated when report is available",
      "arming gate evidence evaluated when report is available",
    ],
    evidenceMissing: [
      "future execution phrase is not provided in this review packet",
      "separate one-shot execution packet is not approved here",
      "live broker write path remains unavailable by design",
    ],
    blockedReasons: [
      "execution review packet is not an execution packet",
      "live execution remains blocked",
      "broker write calls are not allowed",
    ],
    nextSafeAction:
      "Review sanitized evidence, resolve blockers, and require a separate Human Owner-approved execution packet before any live micro-trade can be considered.",
    nextPacketCandidate:
      "AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1",
  };
}

function executionReviewDataLabelSource() {
  const executionReview = buildExecutionReviewStatus();
  return executionReview.dataLabel;
}

function buildLiveReadinessModel(pair) {
  const dataSource = dashboardFixture.dataSource ?? {};
  const bridges = dashboardFixture.bridges ?? {};
  const riskPl = dashboardFixture.riskPl ?? {};
  const exitReadiness = dashboardFixture.exitReadiness ?? {};
  const explanation = pair?.explanation ?? {};
  const bridgeStatus = buildReadOnlyBridgeStatus();
  const paperLoopStatus = buildPaperLoopStatus();
  const armingGateStatus = buildArmingGateStatus();
  const executionReviewStatus = buildExecutionReviewStatus();
  void executionReviewStatus;
  const sourceType = normalizeDataSourceType(
    bridgeStatus.sourceType ?? explanation.dataSourceType ?? dataSource.DATA_SOURCE_TYPE ?? dashboardFixture.source
  );
  const liveSourceAllowed = Boolean(dataSource.LIVE_TRADING_ALLOWED_FROM_THIS_DATA);
  const selectedPair = formatPair(pair?.pair ?? dashboardFixture.selectedPair);
  const blockReasons = [
    "Real market data source is not approved for live trade decisions.",
    "Broker/account state has not been reconciled.",
    "Signal logic and expected edge evidence are not connected.",
    "Risk governor has not approved a live trade boundary.",
    "Pre-entry exit plan and auto-exit readiness are blocked.",
    "Trading history writeback is not available for real closed-trade evidence.",
    "Human Owner has not explicitly armed live execution."
  ];
  if (!paperLoopStatus.paperLoopAvailable) {
    blockReasons.splice(
      blockReasons.length - 1,
      0,
      "Paper signal execution loop evidence is not loaded."
    );
  }
  if (!armingGateStatus.liveArmable) {
    blockReasons.splice(
      blockReasons.length - 1,
      0,
      "Live micro-trade arming gate is not armable."
    );
  }

  return {
    liveReady: false,
    actionMode: "READ_ONLY",
    liveButton: "NOT_PRESENT",
    nextSafeAction:
      "Connect permitted read-only data and broker reconciliation in a later packet, then run paper signal execution before any live arming gate.",
    blockReasons,
    sections: [
      {
        title: "Live data readiness",
        status: bridgeStatus.sourceLabel === "OANDA_READ_ONLY_SANITIZED" ? "READ_ONLY_VALID" : "BLOCKED",
        rows: [
          { label: "Data source name", value: bridgeStatus.sourceLabel },
          { label: "Source type", value: sourceType },
          {
            label: "Freshness timestamp",
            value: bridgeStatus.freshnessUtc ?? "UNKNOWN"
          },
          { label: "Stale/valid status", value: bridgeStatus.staleStatus },
          { label: "Live trading allowed from this source", value: liveSourceAllowed },
          {
            label: "Block reason",
            value: bridgeStatus.blockReason
          },
          { label: "No secrets printed", value: true, tone: "good" },
          { label: "No account IDs printed", value: true, tone: "good" }
        ]
      },
      {
        title: "Broker state readiness",
        status: bridgeStatus.brokerReachable ? "READ_ONLY_AVAILABLE" : "BLOCKED",
        rows: [
          { label: "Account reachable", value: bridgeStatus.brokerReachable },
          { label: "Broker mode", value: "UNKNOWN" },
          { label: "Open positions reconciled", value: bridgeStatus.positionsReconciled },
          { label: "Pending orders reconciled", value: false },
          { label: "Daily P/L available", value: bridgeStatus.plAvailable },
          { label: "Margin/risk availability", value: false },
          {
            label: "Block reason",
            value: bridgeStatus.brokerReachable
              ? "Read-only broker state is available; execution remains blocked."
              : "Broker bridge is blocked and no sanitized account reconciliation is available."
          }
        ]
      },
      {
        title: "Signal readiness",
        status: "BLOCKED",
        rows: [
          { label: "Selected pair", value: selectedPair, tone: "neutral" },
          { label: "Strategy name", value: "UNCONNECTED" },
          { label: "Signal side", value: "NONE" },
          {
            label: "Confidence",
            value: pair?.confidence ? `${pair.confidence}% fixture confidence` : "UNVERIFIED"
          },
          { label: "Expected edge evidence path", value: "UNAVAILABLE" },
          { label: "Backtest/paper evidence required", value: true, tone: "warn" },
          {
            label: "Spread/slippage status",
            value: explanation.spreadSlippageStatus ?? "UNVERIFIED"
          },
          {
            label: "Block reason",
            value: "No approved live signal logic or expected-edge evidence is connected."
          }
        ]
      },
      {
        title: "Paper signal loop readiness",
        status: paperLoopStatus.paperLoopAvailable ? "PAPER_AVAILABLE" : "BLOCKED",
        rows: [
          { label: "PAPER_LOOP_AVAILABLE", value: paperLoopStatus.paperLoopAvailable },
          { label: "Last paper signal", value: paperLoopStatus.lastPaperSignal },
          { label: "Last paper trade status", value: paperLoopStatus.lastPaperTradeStatus },
          { label: "Last paper realized P/L", value: paperLoopStatus.lastPaperRealizedPl },
          { label: "History writeback status", value: paperLoopStatus.historyWritebackStatus },
          { label: "Live execution allowed", value: false },
          { label: "Next safe action", value: paperLoopStatus.nextSafeAction, tone: "warn" }
        ]
      },
      {
        title: "Live micro-trade arming gate",
        status: armingGateStatus.liveArmable ? "ARMING_REVIEW_READY" : "BLOCKED",
        rows: [
          { label: "LIVE_ARMABLE", value: armingGateStatus.liveArmable },
          { label: "LIVE_EXECUTION_ALLOWED", value: armingGateStatus.liveExecutionAllowed },
          { label: "Required Human phrase", value: armingGateStatus.requiredHumanPhrase },
          { label: "Next safe action", value: armingGateStatus.nextSafeAction, tone: "warn" },
          { label: "Next packet candidate", value: armingGateStatus.nextPacketCandidate, tone: "neutral" }
        ]
      },
      {
        title: "Risk readiness",
        status: "BLOCKED",
        rows: [
          { label: "Max units", value: riskPl.positionSize ?? "NOT_APPROVED" },
          { label: "Max trade risk", value: riskPl.riskCap ?? "NOT_APPROVED" },
          { label: "Daily loss cap", value: riskPl.riskCap ?? "NOT_APPROVED" },
          { label: "One-position rule", value: "REQUIRED_NOT_ARMED" },
          { label: "No revenge-loop rule", value: "REQUIRED_NOT_ARMED" },
          { label: "No duplicate-entry rule", value: "REQUIRED_NOT_ARMED" },
          { label: "Kill switch required", value: bridges.killSwitch ?? "REQUIRED" },
          { label: "Risk governor approval", value: false },
          {
            label: "Block reason",
            value: "Risk governor has not approved a live trade boundary."
          }
        ]
      },
      {
        title: "Exit readiness",
        status: exitReadiness.autoExitStatus ?? "BLOCKED",
        rows: [
          { label: "Stop-loss before or with entry", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Take-profit policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Trailing-stop policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Max-time policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Auto-exit readiness", value: exitReadiness.autoExitStatus ?? "BLOCKED" },
          { label: "Manual close fallback", value: "REQUIRED" },
          {
            label: "Block reason",
            value:
              exitReadiness.blockReason ??
              "Exit readiness is not approved for live execution."
          }
        ]
      },
      {
        title: "Trading history writeback readiness",
        status: bridgeStatus.tradingHistoryAvailable ? "READ_ONLY_AVAILABLE" : "BLOCKED",
        rows: [
          { label: "Opened trade evidence row", value: "REQUIRED" },
          { label: "Close realized P/L record", value: "REQUIRED" },
          {
            label: "Required row fields",
            value:
              "pair, side, units, entry time, exit time, duration, realized P/L, exit reason, slippage, source, freshness"
          },
          { label: "History writeback available", value: bridgeStatus.tradingHistoryAvailable },
          {
            label: "Block reason",
            value: bridgeStatus.tradingHistoryAvailable
              ? "Sanitized read-only history is available; live execution remains blocked."
              : "Live execution is blocked until sanitized trade-history writeback is available."
          }
        ]
      }
    ]
  };
}

function Field({ label, value, tone, source = dataSourceForPair(), compact = false }) {
  return (
    <div className="field">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
      <DataLabel compact={compact} source={source} />
    </div>
  );
}

function SystemDetailField({ label, value, tone }) {
  return (
    <div className="field systemDetailField">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
    </div>
  );
}

function SystemDetailPanel({ item, source }) {
  const liveAllowed = Boolean(source?.liveTradingAllowed);
  const rows = [
    {
      label: item.label,
      value: item.value,
      tone: item.tone
    },
    {
      label: "SOURCE",
      value: source?.label ?? "UNVERIFIED"
    },
    {
      label: "FRESHNESS",
      value: formatFreshness(source),
      tone: "neutral"
    },
    {
      label: "LIVE_TRADING_ALLOWED_FROM_THIS_DATA",
      value: String(liveAllowed)
    }
  ];

  return (
    <section className="systemDetailPanel" aria-label={`${item.label} detail`}>
      <div className="fieldGrid systemDetailGrid">
        {rows.map((row) => (
          <SystemDetailField
            key={row.label}
            label={row.label}
            tone={row.tone}
            value={row.value}
          />
        ))}
      </div>
    </section>
  );
}

function CauseEffectPanel({ contract, source = dataSourceForPair() }) {
  return (
    <section className="panel causeEffectPanel" aria-label="Button cause and effect contract">
      <div className="causeEffectGrid">
        <div>
          <span>Cause</span>
          <p>{contract.cause}</p>
        </div>
        <div>
          <span>Effect</span>
          <p>{contract.effect}</p>
        </div>
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function BridgeStatusPanel() {
  const bridge = buildReadOnlyBridgeStatus();
  const source = bridgeDataLabelSource();

  return (
    <section className="panel bridgeStatusPanel" aria-label="Read-only live data bridge status">
      <div className="panelHeading">
        <p>Read-only bridge</p>
        <h3>{bridge.sourceLabel}</h3>
      </div>
      <div className="fieldGrid bridgeStatusGrid">
        <ReadinessRow label="Source type" value={bridge.sourceType} tone="neutral" />
        <ReadinessRow label="Freshness" value={bridge.freshnessUtc ?? "UNKNOWN"} tone="neutral" />
        <ReadinessRow label="Broker reachable" value={bridge.brokerReachable} />
        <ReadinessRow label="Positions reconciled" value={bridge.positionsReconciled} />
        <ReadinessRow label="P/L available" value={bridge.plAvailable} />
        <ReadinessRow label="Trading history available" value={bridge.tradingHistoryAvailable} />
        <ReadinessRow label="Live execution allowed" value={bridge.liveExecutionAllowed} />
        <ReadinessRow label="Next safe action" value={bridge.nextSafeAction} tone="warn" />
        <ReadinessRow label="Block reason" value={bridge.blockReason} />
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function PaperLoopStatusPanel() {
  const paperLoop = buildPaperLoopStatus();
  const source = paperLoopDataLabelSource();

  return (
    <section className="panel paperLoopStatusPanel" aria-label="Paper signal execution loop status">
      <div className="panelHeading">
        <p>Paper loop</p>
        <h3>{`PAPER_LOOP_AVAILABLE: ${String(paperLoop.paperLoopAvailable)}`}</h3>
      </div>
      <div className="fieldGrid paperLoopGrid">
        <ReadinessRow label="PAPER_LOOP_AVAILABLE" value={paperLoop.paperLoopAvailable} />
        <ReadinessRow label="Last paper signal" value={paperLoop.lastPaperSignal} />
        <ReadinessRow label="Last paper trade status" value={paperLoop.lastPaperTradeStatus} />
        <ReadinessRow label="Last paper realized P/L" value={paperLoop.lastPaperRealizedPl} />
        <ReadinessRow label="History writeback status" value={paperLoop.historyWritebackStatus} />
        <ReadinessRow label="Live execution allowed" value={paperLoop.liveExecutionAllowed} />
        <ReadinessRow label="Evidence path" value={paperLoop.evidencePath} tone="neutral" />
        <ReadinessRow label="Next safe action" value={paperLoop.nextSafeAction} tone="warn" />
        <ReadinessRow label="Block reason" value={paperLoop.blockReason} />
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function ArmingGateStatusPanel() {
  const armingGate = buildArmingGateStatus();
  const source = armingGateDataLabelSource();

  return (
    <section className="panel armingGateStatusPanel" aria-label="Live micro-trade arming gate status">
      <div className="panelHeading">
        <p>Arming gate</p>
        <h3>{`LIVE_ARMABLE: ${String(armingGate.liveArmable)}`}</h3>
      </div>
      <div className="fieldGrid armingGateGrid">
        <ReadinessRow label="LIVE_ARMABLE" value={armingGate.liveArmable} />
        <ReadinessRow label="LIVE_EXECUTION_ALLOWED" value={armingGate.liveExecutionAllowed} />
        <ReadinessRow label="Required Human phrase" value={armingGate.requiredHumanPhrase} tone="warn" />
        <ReadinessRow label="Next safe action" value={armingGate.nextSafeAction} tone="warn" />
        <ReadinessRow label="Next packet candidate" value={armingGate.nextPacketCandidate} tone="neutral" />
      </div>
      <div className="blockedReasonList" aria-label="Arming gate blocked reasons">
        {armingGate.blockedReasons.map((reason) => (
          <div className="blockedReason" key={`arming-${reason}`}>
            <span>Blocked</span>
            <p>{reason}</p>
          </div>
        ))}
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function ShellHeader({ view }) {
  const label = viewLabel(view);

  return (
    <header className="dashboardHeader">
      <div>
        <h1 aria-label={label} className="pageIdentityGlyph" title={label}>
          <span aria-hidden="true">{viewIcon(view)}</span>
        </h1>
      </div>
      <div className="headerBadges" aria-label="Dashboard safety labels">
        <StatusBadge value={dashboardFixture.mode} />
        <StatusBadge value={dashboardFixture.source} />
        <StatusBadge value={dashboardFixture.bridges.safeStatus} />
      </div>
    </header>
  );
}

function Breadcrumb({ view, selected, onNavigate }) {
  const crumbs = [{ label: "Home", icon: ICONS.operator }];

  if (view === VIEWS.FOREX || FOREX_CHILD_VIEWS.has(view)) {
    crumbs.push({ label: "Forex Bot", icon: ICONS.forex });
  }

  if (view === VIEWS.WATCHLIST || view === VIEWS.DETAIL) {
    crumbs.push({ label: "Watchlist", icon: ICONS.watchlist });
  }

  if (view === VIEWS.DETAIL) {
    crumbs.push({ label: formatPair(selected.pair), showLabel: true });
  } else if (view !== VIEWS.HOME && view !== VIEWS.FOREX && view !== VIEWS.WATCHLIST) {
    crumbs.push({ label: viewLabel(view), icon: viewIcon(view) });
  }

  const visibleCrumbs = view === VIEWS.DETAIL ? crumbs : crumbs.slice(0, -1);

  if (visibleCrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="breadcrumb" aria-label="Dashboard breadcrumb">
      {visibleCrumbs.map((crumb, index) => {
        const isLast = index === visibleCrumbs.length - 1 && crumb.showLabel;
        const target =
          crumb.label === "Home"
            ? VIEWS.HOME
            : crumb.label === "Forex Bot"
              ? VIEWS.FOREX
              : crumb.label === "Watchlist"
                ? VIEWS.WATCHLIST
                : view;

        return (
          <button
            aria-current={isLast ? "page" : undefined}
            aria-label={crumb.label}
            className={isLast ? "activeCrumb" : ""}
            disabled={isLast}
            key={`${crumb.label}-${index}`}
            title={crumb.label}
            type="button"
            onClick={() => onNavigate(target)}
          >
            {crumb.icon ? <span aria-hidden="true">{crumb.icon}</span> : null}
            {crumb.showLabel ? <span>{crumb.label}</span> : null}
          </button>
        );
      })}
    </nav>
  );
}

function DoorCard({ title, icon, onClick, disabled = false }) {
  const content = (
    <span aria-hidden="true" className="doorCardIconOnly">
      {icon}
    </span>
  );

  if (onClick && !disabled) {
    return (
      <button
        aria-label={title}
        className="doorCard interactiveDoorCard"
        title={title}
        type="button"
        onClick={onClick}
      >
        {content}
      </button>
    );
  }

  return (
    <div
      aria-label={title}
      className={`doorCard ${disabled ? "disabledDoorCard" : ""}`}
      title={title}
    >
      {content}
    </div>
  );
}

function PairViewButton({ pair, onViewPair }) {
  const label = `View ${formatPair(pair)} details`;

  return (
    <button
      aria-label={label}
      className="viewButton iconOnlyButton"
      title={label}
      type="button"
      onClick={() => onViewPair(pair)}
    >
      <span aria-hidden="true">{ICONS.detail}</span>
    </button>
  );
}

function HomeScreen({ onNavigate }) {
  return (
    <section className="screen homeScreen" aria-label="Home">
      <div className="doorGrid">
        <DoorCard icon={ICONS.forex} title="Forex Bot" onClick={() => onNavigate(VIEWS.FOREX)} />
        <DoorCard icon={ICONS.system} title="System" onClick={() => onNavigate(VIEWS.SYSTEM)} />
        <DoorCard
          icon={ICONS.safety}
          title="Safety"
          onClick={() => onNavigate(VIEWS.SAFETY)}
        />
        <DoorCard
          icon={ICONS.settings}
          title="Settings"
          onClick={() => onNavigate(VIEWS.SETTINGS)}
        />
      </div>
    </section>
  );
}

function ForexPaperSandboxBackendStatusCard({ endpointResult }) {
  const sourceStatus = endpointResult?.ok ? "BACKEND STATUS READABLE" : "BACKEND OFFLINE / NOT CONNECTED";
  const httpStatus = endpointResult?.httpStatus ?? "NOT_CHECKED";

  return (
    <div className="forexPaperSandboxBackendCard" aria-label="Paper/Sandbox Backend Status">
      <div className="forexPaperSandboxBackendHeader">
        <div className="panelHeading">
          <p>Paper/Sandbox Backend Status</p>
          <h3>{sourceStatus}</h3>
        </div>
        <strong>{`HTTP: ${httpStatus}`}</strong>
      </div>

      <div className="forexPaperSandboxBackendGrid" aria-label="Paper sandbox backend safe status">
        {FOREX_PAPER_SANDBOX_BACKEND_STATUS_ROWS.map((row) => (
          <div className={`forexPaperSandboxBackendItem tone-${row.tone}`} key={`${row.label}-${row.value}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>

      <p className="forexPaperSandboxBackendRoute">
        READ-ONLY LOCAL STATUS: /api/forex/paper-sandbox/status / NO ORDER OR CLOSE ROUTE
      </p>
    </div>
  );
}

function PaperOrderPreviewEngineCard({ endpointResult }) {
  const sourceStatus = endpointResult?.ok ? "PREVIEW ENGINE READABLE" : "PREVIEW ENGINE LOCAL FALLBACK";
  const httpStatus = endpointResult?.httpStatus ?? "NOT_CHECKED";
  const rows = buildPaperOrderPreviewEngineRows(endpointResult);

  return (
    <div className="forexPaperOrderPreviewEngineCard" aria-label="Paper Order Preview Engine">
      <div className="forexPaperOrderPreviewEngineHeader">
        <div className="panelHeading">
          <p>Paper Order Preview Engine</p>
          <h3>{sourceStatus}</h3>
        </div>
        <strong>{`HTTP: ${httpStatus}`}</strong>
      </div>

      <div className="forexPaperOrderPreviewEngineGrid" aria-label="Paper order preview engine fields">
        {rows.map((row) => (
          <div className={`forexPaperOrderPreviewEngineItem tone-${row.tone}`} key={`${row.label}-${row.value}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>

      <p className="forexPaperOrderPreviewEngineRoute">
        READ-ONLY LOCAL PREVIEW: /api/forex/paper-sandbox/order-preview / NO ORDER SENT
      </p>
    </div>
  );
}

function DemoConnectorProofCard({ endpointResult }) {
  const httpStatus = endpointResult?.httpStatus ?? "NOT_CHECKED";
  const handlePresent = yesNoText(safeEndpointField(endpointResult, "connector_handle_present", "false"));
  const handleStatus = handlePresent === "YES" ? "PRESENT" : "REQUIRED";
  const rows = [
    { label: "BULLET B", value: safeEndpointField(endpointResult, "status", "PARTIAL"), tone: "warn" },
    { label: "HANDLE", value: handleStatus, tone: "warn" },
    {
      label: "DEMO ONLY",
      value: requiredText(safeEndpointField(endpointResult, "practice_demo_only_required", "true")),
      tone: "warn"
    },
    {
      label: "SANITIZED RESULT",
      value: requiredText(safeEndpointField(endpointResult, "sanitized_terminal_result_required", "true")),
      tone: "warn"
    },
    {
      label: "ORDER ROUTE",
      value: enabledDisabledText(safeEndpointField(endpointResult, "order_route_enabled", "false")),
      tone: "danger"
    },
    {
      label: "LIVE",
      value: liveExecutionText(safeEndpointField(endpointResult, "live_execution_allowed", "false")),
      tone: "danger"
    },
    { label: "NEXT", value: "SUPPLY VALUE-FREE CALLABLE HANDLE", tone: "good" }
  ];

  return (
    <section className="forexDemoConnectorProofCard" aria-label="Demo Connector Proof">
      <div className="forexDemoConnectorProofHeader">
        <div className="panelHeading">
          <p>Demo Connector Proof</p>
          <h3>Bullet B: Protected Broker-Demo Runtime Connector Proof</h3>
        </div>
        <strong>{`HTTP: ${httpStatus}`}</strong>
      </div>

      <div className="forexDemoConnectorProofNotice">
        <span>STATUS ONLY — NO CONNECTOR CALL SENT</span>
        <span>{statusText(safeEndpointField(endpointResult, "proof_mode", "STATUS_ONLY_NO_CONNECTOR_CALL"))}</span>
      </div>

      <div className="forexDemoConnectorProofGrid" aria-label="Demo connector proof status fields">
        {rows.map((row) => (
          <div className={`forexDemoConnectorProofItem tone-${row.tone}`} key={`${row.label}-${row.value}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function DemoConnectorEvidenceIntakeCard({ endpointResult }) {
  const sourceStatus = endpointResult?.ok ? "INTAKE SAMPLE READABLE" : "INTAKE SAMPLE LOCAL FALLBACK";
  const httpStatus = endpointResult?.httpStatus ?? "NOT_CHECKED";
  const rows = [
    { label: "INTAKE", value: safeEndpointField(endpointResult, "intake_status", "BLOCKED"), tone: "danger" },
    { label: "CAN CLOSE B", value: yesNoText(safeEndpointField(endpointResult, "can_close_bullet_b", "false")), tone: "danger" },
    { label: "SAMPLE ONLY", value: yesNoText(safeEndpointField(endpointResult, "sample_only", "true")), tone: "warn" },
    { label: "BROKER CALL", value: yesNoText(safeEndpointField(endpointResult, "broker_call_sent", "false")), tone: "danger" },
    { label: "ORDER SENT", value: yesNoText(safeEndpointField(endpointResult, "order_sent", "false")), tone: "danger" },
    { label: "LIVE", value: liveExecutionText(safeEndpointField(endpointResult, "live_execution_allowed", "false")), tone: "danger" },
    { label: "NEXT", value: "PROVIDE SANITIZED TERMINAL DEMO PROOF", tone: "good" }
  ];

  return (
    <section className="forexDemoConnectorIntakeCard" aria-label="Demo Connector Evidence Intake">
      <div className="forexDemoConnectorIntakeHeader">
        <div className="panelHeading">
          <p>Demo Connector Evidence Intake</p>
          <h3>{sourceStatus}</h3>
        </div>
        <strong>{`HTTP: ${httpStatus}`}</strong>
      </div>

      <div className="forexDemoConnectorIntakeNotice">
        <span>EVIDENCE EVALUATOR ONLY</span>
        <span>NO BROKER / CONNECTOR CALL</span>
      </div>

      <div className="forexDemoConnectorIntakeGrid" aria-label="Demo connector evidence intake sample fields">
        {rows.map((row) => (
          <div className={`forexDemoConnectorIntakeItem tone-${row.tone}`} key={`${row.label}-${row.value}`}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function ForexSixBulletCompletionBoard({
  sixBulletResult,
  riskGateResult,
  approvalPackageResult,
  reconciliationResult
}) {
  const boardRows = FOREX_SIX_BULLET_BOARD_ROWS.map((row) => {
    const value = safeEndpointField(sixBulletResult, row.key, row.fallback);
    return {
      ...row,
      value,
      tone: completionStatusTone(value)
    };
  });
  const statusCards = buildForexCompletionStatusCards({
    sixBulletResult,
    riskGateResult,
    approvalPackageResult,
    reconciliationResult
  });
  const sixBulletHttp = sixBulletResult?.httpStatus ?? "NOT_CHECKED";

  return (
    <section className="forexSixBulletBoard" aria-label="Six Bullet Completion Board">
      <div className="forexSixBulletHeader">
        <div className="panelHeading">
          <p>Six Bullet Completion Board</p>
          <h3>NEXT TARGET: B - DEMO CONNECTOR PROOF</h3>
        </div>
        <strong>{`SIX BULLET HTTP: ${sixBulletHttp}`}</strong>
      </div>

      <div className="forexSixBulletSummary" aria-label="Six bullet completion summary">
        <span>DONE: {safeEndpointField(sixBulletResult, "done_count", "2")}</span>
        <span>PARTIAL: {safeEndpointField(sixBulletResult, "partial_count", "4")}</span>
        <span>SAFE: NO LIVE AUTHORITY</span>
        <span>NEXT: B - DEMO CONNECTOR PROOF</span>
      </div>

      <div className="forexSixBulletGrid" aria-label="A-F six bullet statuses">
        {boardRows.map((row) => (
          <div className={`forexSixBulletItem tone-${row.tone}`} key={row.key}>
            <span>{row.bullet}</span>
            <strong>{row.value}</strong>
            <small>{row.label}</small>
          </div>
        ))}
      </div>

      <div className="forexCompletionCardGrid" aria-label="Forex completion status cards">
        {statusCards.map((card) => (
          <div className="forexCompletionStatusCard" key={card.title}>
            <div className="forexCompletionStatusCardHeader">
              <strong>{card.title}</strong>
              <span>{card.endpointResult?.ok ? "ONLINE" : "LOCAL FALLBACK"}</span>
            </div>
            <div className="forexCompletionStatusRows">
              {card.rows.map((row) => (
                <div className={`forexCompletionStatusRow tone-${row.tone}`} key={`${card.title}-${row.label}`}>
                  <span>{row.label}</span>
                  <strong>{row.value}</strong>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function SafeDashboardStatusPanel({ onSafeStatusUpdate }) {
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [status, setStatus] = useState({
    checkedAt: null,
    endpoints: [],
    phase: "idle"
  });
  const online = status.endpoints.some((endpoint) => endpoint.ok);
  const forexPaperSandboxResult = status.endpoints.find((item) => item.id === "forex-paper-sandbox-status");
  const nextSafeStep = online
    ? "Wire paper/sandbox trading status, still no live orders."
    : "Start local orchestrator/runtime status service.";

  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 3500);
    let active = true;

    async function loadSafeDashboardStatus() {
      setStatus((current) => ({
        ...current,
        phase: "loading"
      }));

      const endpointResults = await Promise.all(
        SAFE_DASHBOARD_STATUS_ENDPOINTS.map((endpoint) =>
          fetchSafeDashboardStatusEndpoint(endpoint, controller.signal)
        )
      );

      if (active) {
        setStatus({
          checkedAt: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
          }),
          endpoints: endpointResults,
          phase: "complete"
        });
        onSafeStatusUpdate?.(endpointResults);
      }
    }

    loadSafeDashboardStatus().finally(() => window.clearTimeout(timeout));

    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeout);
    };
  }, [onSafeStatusUpdate, refreshNonce]);

  return (
    <section className="forexSafeStatusPanel" aria-label="Safe dashboard runtime status">
      <div className="forexSafeStatusHeader">
        <div className="panelHeading">
          <p>Safe Status Wiring</p>
          <h3>{online ? "ORCHESTRATOR: ONLINE" : "ORCHESTRATOR: OFFLINE / NOT CONNECTED"}</h3>
        </div>
        <button
          className="forexRefreshStatusButton"
          type="button"
          onClick={() => setRefreshNonce((value) => value + 1)}
        >
          🔄 REFRESH STATUS
        </button>
      </div>

      <div className="forexSafeStatusFlags" aria-label="Safe status guardrails">
        <span>{status.phase === "loading" ? "STATUS: CHECKING" : "DASHBOARD STILL SAFE"}</span>
        <span>NO BROKER ROUTE ENABLED</span>
        <span>GET IN / GET OUT STILL BLOCKED</span>
        <span>{`NEXT: ${nextSafeStep}`}</span>
      </div>

      <ForexPaperSandboxBackendStatusCard endpointResult={forexPaperSandboxResult} />

      <div className="forexSafeEndpointGrid" aria-label="Safe dashboard status endpoints">
        {SAFE_DASHBOARD_STATUS_ENDPOINTS.map((endpoint) => {
          const result = status.endpoints.find((item) => item.id === endpoint.id);
          const rows = result?.summary ?? [{ label: "status", value: "NOT_CHECKED" }];

          return (
            <div className="forexSafeEndpointCard" key={endpoint.id}>
              <div>
                <span>{endpoint.label}</span>
                <strong>{result?.ok ? "ONLINE" : "OFFLINE"}</strong>
              </div>
              <small>{`HTTP: ${result?.httpStatus ?? "NOT_CHECKED"}`}</small>
              {rows.map((row) => (
                <p key={`${endpoint.id}-${row.label}`}>
                  <span>{row.label}</span>
                  <strong>{row.value}</strong>
                </p>
              ))}
            </div>
          );
        })}
      </div>

      <p className="forexSafeStatusTimestamp">
        {status.checkedAt ? `Last safe status check: ${status.checkedAt}` : "Safe status has not been checked yet."}
      </p>
    </section>
  );
}

function PaperSandboxTradePathwayPanel({ paperOrderPreviewResult }) {
  const [previewMode, setPreviewMode] = useState("paper-preview");
  const isPaperPreview = previewMode === "paper-preview";
  const previewRows = isPaperPreview ? buildPaperOrderPreviewRows(paperOrderPreviewResult) : SANDBOX_DRY_RUN_ROWS;
  const previewTitle = isPaperPreview ? "PAPER ORDER PREVIEW" : "SANDBOX DRY RUN";

  return (
    <section className="forexPaperSandboxPanel" aria-label="Paper/Sandbox Trade Pathway">
      <div className="forexPaperSandboxHeader">
        <div className="panelHeading">
          <p>Paper/Sandbox Trade Pathway</p>
          <h3>UI intent → paper preview → sandbox/demo → protected one-shot live → future auto-live</h3>
        </div>
        <strong>PREVIEW ONLY / NO ORDER SENT</strong>
      </div>

      <div className="forexPaperSandboxSteps" aria-label="Paper and sandbox ladder status">
        {PAPER_SANDBOX_PATHWAY_STEPS.map((step) => (
          <div className={`forexPaperSandboxStep tone-${step.tone}`} key={`${step.label}-${step.value}`}>
            <span>{step.label}</span>
            <strong>{step.value}</strong>
          </div>
        ))}
      </div>

      <div className="forexPaperSandboxActions" aria-label="Paper sandbox preview controls">
        <button
          aria-pressed={isPaperPreview}
          className={`forexPaperSandboxButton ${isPaperPreview ? "activePaperSandboxButton" : ""}`}
          type="button"
          onClick={() => setPreviewMode("paper-preview")}
        >
          <span aria-hidden="true" className="forexPaperSandboxButtonIcon">
            📄
          </span>
          <span className="forexPaperSandboxButtonText">PAPER ORDER PREVIEW</span>
        </button>
        <button
          aria-pressed={!isPaperPreview}
          className={`forexPaperSandboxButton ${!isPaperPreview ? "activePaperSandboxButton" : ""}`}
          type="button"
          onClick={() => setPreviewMode("sandbox-dry-run")}
        >
          <span aria-hidden="true" className="forexPaperSandboxButtonIcon">
            🧪
          </span>
          <span className="forexPaperSandboxButtonText">SANDBOX DRY RUN</span>
        </button>
      </div>

      <div className="forexPaperSandboxCriticalStrip" aria-label="Critical paper sandbox operator strip">
        {PAPER_SANDBOX_CRITICAL_STRIP.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>

      <div className="forexPaperSandboxPreview" aria-live="polite">
        <div className="panelHeading">
          <p>Selected local preview</p>
          <h3>{previewTitle}</h3>
        </div>
        <div className="forexPaperSandboxPreviewGrid">
          {previewRows.map((row) => (
            <div key={`${previewMode}-${row.label}`}>
              <span>{row.label}</span>
              <strong>{row.value}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function AiosForexBrandBanner() {
  return (
    <section className="aiosForexBrandBanner" aria-label="AIOS Forex Bot preview brand layer">
      <img
        alt="AIOS.FOREX.BOT preview symbol banner"
        className="aiosForexBrandImage"
        src={aiosForexBotSymbolBanner}
      />
      <div className="aiosForexBrandText">
        <span className="aiosForexBrandPreview">PREVIEW BRAND LAYER</span>
        <h3>AIOS.FOREX.BOT</h3>
        <div className="aiosForexBrandPills" aria-label="AIOS Forex Bot concept labels">
          {AIOS_FOREX_BRAND_PILLS.map((pill) => (
            <span key={pill}>{pill}</span>
          ))}
        </div>
        <p>Customizable cockpit identity. Replaceable before final brand lock.</p>
      </div>
    </section>
  );
}

function ForexCommandSurface() {
  const [selectedCommandIntent, setSelectedCommandIntent] = useState(
    FOREX_COMMAND_INTENTS.AIOS_SIGNAL_STATUS
  );
  const [localEmergencyMode, setLocalEmergencyMode] = useState(false);
  const [safeStatusEndpoints, setSafeStatusEndpoints] = useState([]);
  const selectedCommand =
    FOREX_COMMAND_CONTROLS.find((control) => control.intent === selectedCommandIntent) ??
    FOREX_COMMAND_CONTROLS[FOREX_COMMAND_CONTROLS.length - 1];
  const paperOrderPreviewResult = safeStatusEndpoints.find((item) => item.id === "forex-paper-order-preview");
  const sixBulletResult = safeStatusEndpoints.find((item) => item.id === "forex-six-bullet-status");
  const riskGateResult = safeStatusEndpoints.find((item) => item.id === "forex-risk-gate-status");
  const approvalPackageResult = safeStatusEndpoints.find((item) => item.id === "forex-approval-package-status");
  const reconciliationResult = safeStatusEndpoints.find((item) => item.id === "forex-reconciliation-status");
  const demoConnectorProofResult = safeStatusEndpoints.find(
    (item) => item.id === "forex-demo-connector-proof-status"
  );
  const demoConnectorIntakeResult = safeStatusEndpoints.find(
    (item) => item.id === "forex-demo-connector-proof-intake-sample"
  );

  function selectCommandIntent(control) {
    setSelectedCommandIntent(control.intent);
    setLocalEmergencyMode(Boolean(control.emergency));
  }

  return (
    <section className="panel forexCommandSurface" aria-label="Forex Command Surface">
      <div className="forexCommandHeader">
        <div className="panelHeading">
          <p>Forex Command Surface</p>
          <h3>Trade Command Dock</h3>
        </div>
        <strong>LIVE EXECUTION BLOCKED UNTIL FUTURE PROTECTED APPROVAL</strong>
      </div>

      <AiosForexBrandBanner />

      <div className="forexStatusStrip" aria-label="Forex command safety status">
        {FOREX_COMMAND_STATUSES.map((status) => (
          <div className={`forexStatusPill tone-${status.tone}`} key={`${status.label}-${status.value}`}>
            <span>{status.label}</span>
            <strong>{status.value}</strong>
          </div>
        ))}
      </div>

      <SafeDashboardStatusPanel onSafeStatusUpdate={setSafeStatusEndpoints} />

      <PaperOrderPreviewEngineCard endpointResult={paperOrderPreviewResult} />

      <DemoConnectorProofCard endpointResult={demoConnectorProofResult} />

      <DemoConnectorEvidenceIntakeCard endpointResult={demoConnectorIntakeResult} />

      <ForexSixBulletCompletionBoard
        approvalPackageResult={approvalPackageResult}
        reconciliationResult={reconciliationResult}
        riskGateResult={riskGateResult}
        sixBulletResult={sixBulletResult}
      />

      <PaperSandboxTradePathwayPanel paperOrderPreviewResult={paperOrderPreviewResult} />

      <div className="forexCriticalStrip" aria-label="Critical forex command information">
        {FOREX_CRITICAL_INFO.map((item) => (
          <div className="forexCriticalItem" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>

      <div className="forexCommandGrid" aria-label="Urgent trade controls">
        {FOREX_COMMAND_CONTROLS.map((control) => {
          const isActive = control.intent === selectedCommandIntent;

          return (
            <button
              aria-pressed={isActive}
              aria-disabled={control.state === "BLOCKED" ? "true" : undefined}
              className={[
                "forexCommandButton",
                isActive ? "activeForexCommandButton" : "",
                control.state === "BLOCKED" ? "blockedForexCommandButton" : "",
                control.emergency ? "emergencyForexCommandButton" : ""
              ]
                .filter(Boolean)
                .join(" ")}
              key={control.id}
              title={control.message}
              type="button"
              onClick={() => selectCommandIntent(control)}
            >
              <span aria-hidden="true" className="forexCommandIcon">
                {control.icon}
              </span>
              <span className="forexCommandText">{control.label}</span>
              <strong>{control.state}</strong>
            </button>
          );
        })}
      </div>

      <section className="forexCommandIntentPanel" aria-label="Command Intent" aria-live="polite">
        <div className="panelHeading">
          <p>Command Intent</p>
          <h3>{selectedCommand.intent}</h3>
        </div>
        <div className="forexIntentGrid">
          <div>
            <span>Selected button</span>
            <strong>{selectedCommand.label}</strong>
          </div>
          <div>
            <span>AIOS mode</span>
            <strong>{selectedCommand.mode}</strong>
          </div>
          <div>
            <span>Blocked because</span>
            <strong>{selectedCommand.blockedReasons.join(", ")}</strong>
          </div>
          <div>
            <span>Missing evidence</span>
            <strong>{selectedCommand.missingEvidence.join(", ")}</strong>
          </div>
          <div className="forexIntentWide">
            <span>Next safe step</span>
            <strong>{selectedCommand.nextSafeStep}</strong>
          </div>
        </div>
      </section>

      {localEmergencyMode ? (
        <div className="forexEmergencyState" aria-label="Local dashboard emergency mode">
          <span>LOCAL DASHBOARD EMERGENCY MODE</span>
          <strong>No broker call sent. No order sent. No close sent.</strong>
          <p>Operator must use approved broker/manual path until execution wiring exists.</p>
        </div>
      ) : null}

      <div className="forexNextSafeStepStrip" aria-label="Next safe step">
        {FOREX_NEXT_SAFE_STEPS.map((step) => (
          <span key={step}>{step}</span>
        ))}
      </div>

      <div className="forexTradingLadder" aria-label="AIOS Trading Ladder">
        {AIOS_TRADING_LADDER.map((item) => (
          <div className={`forexLadderItem tone-${item.tone}`} key={`${item.label}-${item.value}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function ForexHub({ onBack, onNavigate }) {
  return (
    <section className="screen" aria-label="Forex Bot">
      <div className="screenTop">
        <BackButton onClick={onBack} />
      </div>

      <ForexCommandSurface />

      <div className="hubGrid">
        <DoorCard icon={ICONS.watchlist} title="Watchlist" onClick={() => onNavigate(VIEWS.WATCHLIST)} />
        <DoorCard icon={ICONS.position} title="Position" onClick={() => onNavigate(VIEWS.POSITION)} />
        <DoorCard icon={ICONS.risk} title="Risk / P&L" onClick={() => onNavigate(VIEWS.RISK)} />
        <DoorCard
          icon={ICONS.exit}
          title="Exit"
          onClick={() => onNavigate(VIEWS.EXIT)}
        />
        <DoorCard
          icon={ICONS.history}
          title="Trading History"
          onClick={() => onNavigate(VIEWS.HISTORY)}
        />
        <DoorCard
          icon={ICONS.readiness}
          title="Execution Readiness"
          onClick={() => onNavigate(VIEWS.READINESS)}
        />
      </div>
    </section>
  );
}

function WatchlistScreen({ pairs, selectedPair, onBack, onViewPair }) {
  return (
    <section className="screen" aria-label="Watchlist">
      <div className="screenTop">
        <BackButton onClick={onBack} />
      </div>

      <CauseEffectPanel contract={OPERATION_CONTRACTS.watchlist} source={dataSourceForPair()} />
      <BridgeStatusPanel />

      <div className="watchlistList" role="list" aria-label="Ranked fixture pair watchlist">
        {pairs.map((pair) => {
          const selected = pair.pair === selectedPair;
          const source = dataSourceForPair(pair);

          return (
            <div className={`watchlistItem ${selected ? "selectedWatchlistItem" : ""}`} key={pair.pair}>
              <strong className="pairName">{formatPair(pair.pair)}</strong>
              <span className="scorePair">
                <span>Score</span>
                <strong>{pair.opportunityScore}</strong>
              </span>
              <span className="scorePair">
                <span>Confidence</span>
                <strong>{pair.confidence}</strong>
              </span>
              <StatusBadge value={pair.trend} />
              <DataLabel compact source={source} />
              <PairViewButton pair={pair.pair} onViewPair={onViewPair} />
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ChartPanel({ pair, source }) {
  const points = chartPolyline(pair.chart);

  return (
    <section className="panel chartPanel" aria-label={`${formatPair(pair.pair)} fixture chart`}>
      <div className="panelHeading">
        <p>Chart</p>
        <h3>{pair.fixturePrice}</h3>
      </div>
      <div className="chartShell">
        <svg viewBox="0 0 340 132" role="img" aria-label="Fixture price line">
          <polyline className="chartGridLine" points="14,104 326,104" />
          <polyline className="chartGridLine" points="14,66 326,66" />
          <polyline className="chartGridLine" points="14,28 326,28" />
          <polyline className="chartLine" points={points} />
          {pair.chart.map((point, index) => (
            <circle
              className="chartPoint"
              cx={14 + (index * 312) / Math.max(pair.chart.length - 1, 1)}
              cy={
                118 -
                ((point - Math.min(...pair.chart)) /
                  (Math.max(...pair.chart) - Math.min(...pair.chart) || 1)) *
                  104
              }
              key={`${pair.pair}-${point}-${index}`}
              r="3"
            />
          ))}
        </svg>
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function AnalyticsPanel({ pair }) {
  const explanation = pair.explanation ?? {};

  return (
    <section className="panel" aria-label="Analytics">
      <div className="panelHeading">
        <p>Analytics</p>
        <h3>Opportunity</h3>
      </div>
      <p className="shortText">{explanation.rankingReason ?? pair.reason}</p>
      <div className="miniGrid">
        <StatusBadge value={pair.supertrend} />
        <StatusBadge value={explanation.spreadSlippageStatus ?? "UNVERIFIED_FIXTURE"} />
      </div>
    </section>
  );
}

function RiskPanel({ riskPl }) {
  const source = dataSourceForPair();

  return (
    <section className="panel" aria-label="Risk and P/L">
      <div className="panelHeading">
        <p>Risk</p>
        <h3>P/L</h3>
      </div>
      <div className="fieldGrid">
        <Field compact label="Realized" source={source} value={riskPl.realizedPl} tone="neutral" />
        <Field compact label="Unrealized" source={source} value={riskPl.unrealizedPl} tone="neutral" />
        <Field compact label="Cap" source={source} value={riskPl.riskCap} tone="warn" />
        <Field compact label="Position" source={source} value={riskPl.currentPosition} tone="neutral" />
      </div>
    </section>
  );
}

function ExitPanel({ exitReadiness }) {
  const source = dataSourceForPair();

  return (
    <section className="panel" aria-label="Exit readiness">
      <div className="panelHeading">
        <p>Exit</p>
        <h3>{exitReadiness.autoExitStatus}</h3>
      </div>
      <div className="controlList">
        {exitReadiness.controls.map((control) => (
          <div className="controlRow" key={control.label}>
            <span>{control.label}</span>
            <StatusBadge value={control.status} />
          </div>
        ))}
      </div>
      <DataLabel compact source={source} />
    </section>
  );
}

function DecisionPanel({ pair, bridges, exitReadiness }) {
  const source = dataSourceForPair(pair);
  const explanation = pair.explanation ?? {};

  return (
    <section className="panel decisionPanel" aria-label="Decision">
      <div className="panelHeading">
        <p>Decision</p>
        <h3>{explanation.safeDecision ?? bridges.safeStatus}</h3>
      </div>
      <p className="shortText">{explanation.nextSafeAction ?? bridges.nextAction}</p>
      <p className="shortText">{explanation.blockReason ?? exitReadiness.blockReason}</p>
      <DataLabel source={source} />
    </section>
  );
}

function PairDetail({ pair, riskPl, exitReadiness, bridges, onBack }) {
  const source = dataSourceForPair(pair);

  return (
    <section className="screen detailScreen" aria-label="Pair Detail">
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>{formatPair(pair.pair)}</h2>
        <StatusBadge value={bridges.safeStatus} />
      </div>

      <div className="detailGrid">
        <section className="panel pricePanel" aria-label="Price">
          <div className="panelHeading">
            <p>Price</p>
            <h3>{pair.fixturePrice}</h3>
          </div>
          <div className="miniGrid">
            <StatusBadge value={pair.trend} />
            <StatusBadge value={pair.session} />
          </div>
          <DataLabel source={source} />
        </section>
        <ChartPanel pair={pair} source={source} />
        <AnalyticsPanel pair={pair} />
        <RiskPanel riskPl={riskPl} />
        <ExitPanel exitReadiness={exitReadiness} />
        <DecisionPanel bridges={bridges} exitReadiness={exitReadiness} pair={pair} />
      </div>
    </section>
  );
}

function SimpleStatusPage({ title, backLabel, onBack, children }) {
  return (
    <section className="screen" aria-label={title}>
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <StatusBadge value={backLabel} />
      </div>
      <div className="simpleGrid">{children}</div>
    </section>
  );
}

function SystemPage({ onBack }) {
  const source = dataSourceForPair();
  const [selectedDetailId, setSelectedDetailId] = useState(SYSTEM_DETAIL_ITEMS[0].id);
  const selectedDetail =
    SYSTEM_DETAIL_ITEMS.find((item) => item.id === selectedDetailId) ?? SYSTEM_DETAIL_ITEMS[0];

  return (
    <section className="screen" aria-label="System">
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>System</h2>
        <StatusBadge value="READ_ONLY" />
      </div>

      <div className="systemEmojiGrid" aria-label="System status controls">
        {SYSTEM_DETAIL_ITEMS.map((item) => {
          const isActive = item.id === selectedDetail.id;

          return (
            <button
              aria-label={item.label}
              aria-pressed={isActive}
              className={`systemEmojiButton ${isActive ? "activeSystemEmojiButton" : ""}`}
              key={item.id}
              title={item.label}
              type="button"
              onClick={() => setSelectedDetailId(item.id)}
            >
              <span aria-hidden="true">{item.emoji}</span>
            </button>
          );
        })}
      </div>

      <SystemDetailPanel item={selectedDetail} source={source} />
      <BridgeStatusPanel />
    </section>
  );
}

function SafetyPage({ onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="BLOCKED" title="Safety" onBack={onBack}>
      <Field compact label="Live trading" source={source} value="BLOCKED" />
      <Field compact label="Source labels" source={source} value="REQUIRED" tone="warn" />
      <Field compact label="Secrets" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Kill switch" source={source} value="REQUIRED" tone="warn" />
      <Field compact label="Broker/API action" source={source} value="BLOCKED" />
    </SimpleStatusPage>
  );
}

function SettingsPage({ bridges, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="NO_SECRETS" title="Settings" onBack={onBack}>
      <Field compact label="Secret bridge" source={source} value={bridges.secretBridge} />
      <Field compact label="Broker bridge" source={source} value={bridges.brokerBridge} />
      <Field compact label="API keys" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Tokens" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Account IDs" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Secret values" source={source} value="NOT_DISPLAYED" tone="good" />
    </SimpleStatusPage>
  );
}

function PositionPage({ riskPl, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="READ_ONLY" title="Position" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.position} source={source} />
      <BridgeStatusPanel />
      <Field compact label="Position" source={source} value={riskPl.currentPosition} tone="neutral" />
      <Field compact label="Units" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Entry price" source={source} value="UNAVAILABLE" tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
    </SimpleStatusPage>
  );
}

function RiskPage({ riskPl, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="FIXTURE_NOT_LIVE" title="Risk / P&L" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.risk} source={source} />
      <BridgeStatusPanel />
      <Field compact label="Daily loss cap" source={source} value={riskPl.riskCap} tone="warn" />
      <Field compact label="Max position size" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
      <Field compact label="Risk status" source={source} value="BLOCKED" tone="danger" />
      <Field compact label="Live trading allowed" source={source} value="false" />
    </SimpleStatusPage>
  );
}

function ExitPage({ exitReadiness, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel={exitReadiness.autoExitStatus} title="Exit" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.exit} source={source} />
      <BridgeStatusPanel />
      <section className="panel notePanel" aria-label="Exit page meaning">
        <div className="panelHeading">
          <p>Meaning</p>
          <h3>Readiness only</h3>
        </div>
        <p className="shortText">
          Exit evaluates whether a trade is protected and exit-ready. This page does not close trades.
        </p>
      </section>
      {exitReadiness.controls.map((control) => (
        <Field compact key={control.label} label={control.label} source={source} value={control.status} />
      ))}
      <Field compact label="Auto-exit" source={source} value={exitReadiness.autoExitStatus} />
      <section className="panel notePanel" aria-label="Exit block reason">
        <div className="panelHeading">
          <p>Block reason</p>
          <h3>{exitReadiness.autoExitStatus}</h3>
        </div>
        <p className="shortText">{exitReadiness.blockReason}</p>
        <DataLabel compact source={source} />
      </section>
    </SimpleStatusPage>
  );
}

function tradeValue(trade, keys, fallback = "UNAVAILABLE") {
  for (const key of keys) {
    if (trade?.[key] !== undefined && trade?.[key] !== null && trade?.[key] !== "") {
      return trade[key];
    }
  }

  return fallback;
}

function TradingHistoryPage({ onBack }) {
  const source = dataSourceForPair();
  const history = Array.isArray(dashboardFixture.tradingHistory)
    ? dashboardFixture.tradingHistory
    : [];
  const rows =
    history.length > 0
      ? history
      : [
          {
            pair: "UNAVAILABLE",
            evidenceStatus: "NO_REAL_HISTORY_AVAILABLE",
            sourceLabel: "FIXTURE_NOT_LIVE"
          }
        ];

  return (
    <SimpleStatusPage
      backLabel={history.length > 0 ? "READ_ONLY" : "NO_REAL_HISTORY_AVAILABLE"}
      title="Trading History"
      onBack={onBack}
    >
      <CauseEffectPanel contract={OPERATION_CONTRACTS.history} source={source} />
      <BridgeStatusPanel />
      <PaperLoopStatusPanel />
      {history.length === 0 ? (
        <section className="panel notePanel" aria-label="Trading history unavailable">
          <div className="panelHeading">
            <p>Trading History</p>
            <h3>NO_REAL_HISTORY_AVAILABLE</h3>
          </div>
          <p className="shortText">
            No sanitized real closed-trade history is available to this dashboard. Fixture/demo state is
            read-only and cannot prove live execution.
          </p>
          <DataLabel source={source} />
        </section>
      ) : null}
      <div className="historyList" role="list" aria-label="Closed trade history">
        {rows.map((trade, index) => (
          <section className="panel historyCard" key={`${trade.pair ?? "trade"}-${index}`} role="listitem">
            <div className="panelHeading">
              <p>Closed trade</p>
              <h3>{formatPair(tradeValue(trade, ["pair"], "UNKNOWN"))}</h3>
            </div>
            <div className="fieldGrid">
              <Field compact label="Pair" source={source} value={formatPair(tradeValue(trade, ["pair"]))} />
              <Field compact label="Side" source={source} value={tradeValue(trade, ["side"])} />
              <Field compact label="Units" source={source} value={tradeValue(trade, ["units"])} />
              <Field compact label="Entry time" source={source} value={tradeValue(trade, ["entryTime"])} />
              <Field compact label="Exit time" source={source} value={tradeValue(trade, ["exitTime"])} />
              <Field compact label="Duration" source={source} value={tradeValue(trade, ["duration"])} />
              <Field compact label="Realized P/L" source={source} value={tradeValue(trade, ["realizedPl", "realizedPL"])} />
              <Field compact label="Exit reason" source={source} value={tradeValue(trade, ["exitReason"])} />
              <Field compact label="Stop-loss used" source={source} value={tradeValue(trade, ["stopLossUsed"])} />
              <Field compact label="Take-profit used" source={source} value={tradeValue(trade, ["takeProfitUsed"])} />
              <Field compact label="Trailing used" source={source} value={tradeValue(trade, ["trailingStopUsed"])} />
              <Field compact label="Max-time used" source={source} value={tradeValue(trade, ["maxTimeUsed"])} />
              <Field compact label="Slippage" source={source} value={tradeValue(trade, ["slippage"])} />
              <Field compact label="Evidence status" source={source} value={tradeValue(trade, ["evidenceStatus"])} />
            </div>
          </section>
        ))}
      </div>
    </SimpleStatusPage>
  );
}

function ReadinessSection({ section, source }) {
  return (
    <section className="panel readinessPanel" aria-label={section.title}>
      <div className="panelHeading">
        <p>{section.title}</p>
        <h3>{section.status}</h3>
      </div>
      <div className="fieldGrid readinessGrid">
        {section.rows.map((row) => (
          <ReadinessRow
            key={`${section.title}-${row.label}`}
            label={row.label}
            tone={row.tone}
            value={row.value}
          />
        ))}
      </div>
      <DataLabel compact source={source} />
    </section>
  );
}

function ExecutionReviewStatusPanel() {
  const executionReview = buildExecutionReviewStatus();
  const summaryRows = [
    {
      label: "EXECUTION_REVIEW_READY",
      value: String(executionReview.executionReviewReady).toUpperCase(),
    },
    {
      label: "LIVE_EXECUTION_ALLOWED",
      value: String(executionReview.liveExecutionAllowed).toUpperCase(),
    },
    {
      label: "LIVE_TRADE_PLACED",
      value: String(executionReview.liveTradePlaced).toUpperCase(),
    },
    {
      label: "NEXT PACKET CANDIDATE",
      value: executionReview.nextPacketCandidate,
    },
  ];

  return (
    <section className="executionReviewStatusPanel" aria-labelledby="execution-review-status-title">
      <div className="readinessSectionHeader">
        <h3 id="execution-review-status-title">One-shot execution review</h3>
        <span>{executionReview.executionReviewReady ? "READY" : "BLOCKED"}</span>
      </div>
      <div className="executionReviewGrid">
        {summaryRows.map((row) => (
          <div className="readinessField" key={row.label}>
            <span>{row.label}</span>
            <strong>{row.value}</strong>
          </div>
        ))}
      </div>
      <div className="readinessField">
        <span>REQUIRED HUMAN PHRASE</span>
        <strong>{executionReview.requiredHumanPhrase}</strong>
      </div>
      <div className="readinessField">
        <span>EVIDENCE PRESENT</span>
        <strong>{executionReview.evidencePresent.join("; ")}</strong>
      </div>
      <div className="readinessField">
        <span>EVIDENCE MISSING</span>
        <strong>{executionReview.evidenceMissing.join("; ")}</strong>
      </div>
      <div className="readinessField">
        <span>BLOCKED REASONS</span>
        <strong>{executionReview.blockedReasons.join("; ")}</strong>
      </div>
      <div className="readinessField">
        <span>NEXT SAFE ACTION</span>
        <strong>{executionReview.nextSafeAction}</strong>
      </div>
    </section>
  );
}

function ExecutionReadinessPage({ pair, onBack }) {
  const source = dataSourceForPair(pair);
  const readiness = buildLiveReadinessModel(pair);

  return (
    <SimpleStatusPage backLabel="LIVE_READY: false" title="Execution Readiness" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.readiness} source={source} />
      <BridgeStatusPanel />
      <PaperLoopStatusPanel />
      <ArmingGateStatusPanel />
      <ExecutionReviewStatusPanel />
      <section className="panel readinessSummaryPanel" aria-label="Overall execution readiness">
        <div className="panelHeading">
          <p>Overall status</p>
          <h3>{`LIVE_READY: ${String(readiness.liveReady)}`}</h3>
        </div>
        <div className="fieldGrid readinessGrid">
          <ReadinessRow label="Action mode" value={readiness.actionMode} tone="good" />
          <ReadinessRow label="Live BUY/SELL button" value={readiness.liveButton} tone="good" />
          <ReadinessRow label="Next safe action" value={readiness.nextSafeAction} tone="warn" />
        </div>
        <div className="blockedReasonList" aria-label="Blocked reasons">
          {readiness.blockReasons.map((reason) => (
            <div className="blockedReason" key={reason}>
              <span>Blocked</span>
              <p>{reason}</p>
            </div>
          ))}
        </div>
        <DataLabel source={source} />
      </section>
      <div className="readinessSectionList">
        {readiness.sections.map((section) => (
          <ReadinessSection key={section.title} section={section} source={source} />
        ))}
      </div>
    </SimpleStatusPage>
  );
}

export default function MinimalOperatorDashboard() {
  const pairs = useMemo(
    () =>
      [...dashboardFixture.watchlist].sort(
        (a, b) => b.opportunityScore - a.opportunityScore || b.confidence - a.confidence
      ),
    []
  );
  const [view, setView] = useState(VIEWS.HOME);
  const [selectedPair, setSelectedPair] = useState(dashboardFixture.selectedPair);
  const selected = pairs.find((pair) => pair.pair === selectedPair) ?? pairs[0];

  function openPair(pair) {
    setSelectedPair(pair);
    setView(VIEWS.DETAIL);
  }

  return (
    <main className="minimalOperatorDashboard">
      <ShellHeader view={view} />
      <Breadcrumb selected={selected} view={view} onNavigate={setView} />

      {view === VIEWS.HOME ? <HomeScreen onNavigate={setView} /> : null}

      {view === VIEWS.FOREX ? (
        <ForexHub
          onBack={() => setView(VIEWS.HOME)}
          onNavigate={setView}
        />
      ) : null}

      {view === VIEWS.WATCHLIST ? (
        <WatchlistScreen
          pairs={pairs}
          selectedPair={selected.pair}
          onBack={() => setView(VIEWS.FOREX)}
          onViewPair={openPair}
        />
      ) : null}

      {view === VIEWS.DETAIL ? (
        <PairDetail
          bridges={dashboardFixture.bridges}
          exitReadiness={dashboardFixture.exitReadiness}
          pair={selected}
          riskPl={dashboardFixture.riskPl}
          onBack={() => setView(VIEWS.WATCHLIST)}
        />
      ) : null}

      {view === VIEWS.SYSTEM ? <SystemPage onBack={() => setView(VIEWS.HOME)} /> : null}

      {view === VIEWS.SAFETY ? <SafetyPage onBack={() => setView(VIEWS.HOME)} /> : null}

      {view === VIEWS.SETTINGS ? (
        <SettingsPage bridges={dashboardFixture.bridges} onBack={() => setView(VIEWS.HOME)} />
      ) : null}

      {view === VIEWS.POSITION ? (
        <PositionPage riskPl={dashboardFixture.riskPl} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.RISK ? (
        <RiskPage riskPl={dashboardFixture.riskPl} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.EXIT ? (
        <ExitPage exitReadiness={dashboardFixture.exitReadiness} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.HISTORY ? (
        <TradingHistoryPage onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.READINESS ? (
        <ExecutionReadinessPage pair={selected} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}
    </main>
  );
}
