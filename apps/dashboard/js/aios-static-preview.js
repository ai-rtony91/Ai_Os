const tabButtons = document.querySelectorAll("[data-tab]");
const actionButtons = document.querySelectorAll("[data-action]");
const panels = document.querySelectorAll(".panel");
const assistantOutput = document.getElementById("assistantOutput");
const consoleOutput = document.getElementById("consoleOutput");
const mockMessage = document.getElementById("mockMessage");
const sidebarToggle = document.querySelector(".command-sidebar .sidebar-toggle");
const drawerReopen = document.querySelector(".drawer-reopen");
const drawerBackdrop = document.querySelector(".drawer-backdrop");
const mobileSidebarQuery = window.matchMedia("(max-width: 1120px)");
const tapTargets = document.querySelectorAll("button, .glass-card, .chart-card, .work-card, .status-card, .status-panel-button, .registry-chip, .app-card");
const statusCards = document.querySelectorAll("[data-status-card]");
const statusPanelButtons = document.querySelectorAll("[data-status-panel-button]");
const statusPanels = document.querySelectorAll("[data-status-panel]");
const toolRegistryMessage = document.querySelector("[data-tool-registry-message]");
const toolRegistryGrid = document.querySelector("[data-tool-registry-grid]");
const toolRegistrySummaryValues = document.querySelectorAll("[data-tool-summary]");
const workTableAiMessage = document.querySelector("[data-work-table-ai-message]");
const workTableAiMode = document.querySelector("[data-work-table-ai-mode]");
const workTableAiMeta = document.querySelector("[data-work-table-ai-meta]");
const workTableAiCards = document.querySelector("[data-work-table-ai-cards]");
const workTableAiSafeActions = document.querySelector("[data-work-table-ai-safe-actions]");
const workTableAiBlockedActions = document.querySelector("[data-work-table-ai-blocked-actions]");
const workTableAiSources = document.querySelector("[data-work-table-ai-sources]");
const dashboardThemeSelector = document.querySelector("[data-theme-selector]");
const youtubeRadioDock = document.querySelector("[data-youtube-radio-dock]");
const youtubeRadioState = document.querySelector("[data-youtube-radio-state]");
const youtubeRadioControls = document.querySelectorAll("[data-youtube-radio-control]");
const drawerStateKey = "aios.drawer.closed";
const dashboardThemeKey = "aios.dashboard.theme";
const dashboardThemeClasses = [
  "theme-terminal-green",
  "theme-cyan-command",
  "theme-amber-warning",
  "theme-high-contrast"
];
const dashboardThemeMap = {
  "terminal-green": "theme-terminal-green",
  "cyan-command": "theme-cyan-command",
  "amber-warning": "theme-amber-warning",
  "high-contrast": "theme-high-contrast"
};
const toolRegistryFixturePath = "mock-data/tool-registry-status-fixture.example.json";
const toolRegistrySummaryStatuses = ["READY", "INSTALLED", "MISSING", "NEEDS_LOGIN", "NEEDS_CONFIG", "BLOCKED", "UNKNOWN"];
const workTableAiFixturePath = "mock-data/work-table-ai-fixture.example.json";
const workTableAiActionsFixturePath = "mock-data/work-table-ai-actions.example.json";
const lifetimeTelemetryFixturePath = "mock-data/lifetime-telemetry-fixture.example.json";
const youtubeRadioVideoId = "VFzsSbdS7Sk";
const youtubeRadioPlaylistId = "RDVFzsSbdS7Sk";
const youtubeRadioPlaylistUrl = `https://www.youtube.com/watch?v=${youtubeRadioVideoId}&list=${youtubeRadioPlaylistId}`;
let youtubeRadioPlayer = null;
let youtubeRadioScriptLoading = false;
let youtubeRadioShouldPlay = false;

const statusFixtures = {
  overall: {
    path: "mock-data/aios-status-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Status unavailable - local fixture missing."
    }
  },
  progress: {
    path: "mock-data/progress-ledger-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Progress status unavailable."
    }
  },
  lifetimeTelemetry: {
    path: lifetimeTelemetryFixturePath,
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Lifetime telemetry fixture unavailable — mock data only."
    }
  },
  validator: {
    path: "mock-data/validator-health-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Validator health unknown."
    }
  },
  checkpoint: {
    path: "mock-data/checkpoint-status-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Checkpoint unknown."
    }
  },
  safety: {
    path: "mock-data/safety-status-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Safety status unknown."
    }
  },
  nextAction: {
    path: "mock-data/next-action-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Next action unavailable."
    }
  },
  aiAssistance: {
    path: "mock-data/ai-assistant-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "AI Assistance placeholder unavailable."
    }
  },
  workTableAi: {
    path: "mock-data/work-table-ai-fixture.example.json",
    fallback: {
      status: "UNKNOWN",
      value: "UNKNOWN",
      detail: "Work Table AI placeholder unavailable."
    }
  }
};

const messages = {
  "work-table": {
    assistant: "Work Table: static center workspace for project briefs, prompt stacks, build instructions, tool output, approval gates, and validation queues.",
    console: "Ai_Os> Work Table selected\nMode: static preview\nAPPLY: requires human approval\nWriters/persistence/trading: BLOCKED"
  },
  "app-store": {
    assistant: "App Store: future catalog for approved generated apps such as Calendar, Notes, Reports, and Telemetry panels. No install or activation behavior exists.",
    console: "Ai_Os> App Store selected\nCatalog: static mock\nInstall actions: BLOCKED\nApproval gate: REQUIRED"
  },
  connectors: {
    assistant: "Connectors: future review lane for approved integrations. API keys, credentials, broker access, and service connections remain blocked.",
    console: "Ai_Os> Connectors selected\nAPI calls: BLOCKED\nCredentials: BLOCKED\nService connections: REVIEW ONLY"
  },
  calendar: {
    assistant: "Calendar: static app packet example for planning dates and checkpoint reminders. No Google, Microsoft, Outlook, or provider API is connected.",
    console: "Ai_Os> Calendar selected\nProvider API: NONE\nPersistence: BLOCKED\nFixture mode: REVIEW"
  },
  notes: {
    assistant: "Notes: future local note concept for project instructions and operator context. No note writer or persistence is active.",
    console: "Ai_Os> Notes selected\nWriter: INACTIVE\nPersistence: BLOCKED\nStatus: DRAFT"
  },
  "build-queue": {
    assistant: "Build Queue: future list of generated work packets waiting for DRY_RUN review, human approval, validation, and commit checkpoints.",
    console: "Ai_Os> Build Queue selected\nAPPLY packets: approval required\nCommit/push: approval required\nStatus: REVIEW"
  },
  reports: {
    assistant: "Reports: future health, checkpoint, and progress surface. Report writers remain inactive and protected root files remain blocked.",
    console: "Ai_Os> Reports selected\nReport writer: INACTIVE\nProtected root edits: BLOCKED\nStatus: REVIEW"
  },
  telemetry: {
    assistant: "Telemetry: future system health/event visibility using approved fixtures first. No telemetry writer and no persistence are enabled.",
    console: "Ai_Os> Telemetry selected\nTelemetry writer: INACTIVE\nPersistence: BLOCKED\nPrivate data: BLOCKED"
  },
  admin: {
    assistant: "Admin: safety locks, settings review, approval gates, and blocked-action visibility. This static preview cannot execute APPLY behavior.",
    console: "Ai_Os> Admin selected\nApproval gates: MANUAL\nStartup tasks: BLOCKED\nLive automation: BLOCKED"
  },
  "system-status": {
    assistant: "System Status: mock status shows static preview online, backend disabled, persistence disabled, service-worker registration disabled, and trading automation blocked.",
    console: "Ai_Os> System Status\nSTATIC PREVIEW: ONLINE\nBACKEND/API: DISABLED\nPERSISTENCE: DISABLED\nTRADING AUTOMATION: BLOCKED"
  },
  diagnostics: {
    assistant: "Run Diagnostics: mock plan checks static file presence, registry labels, JSON validity, unsafe keyword scans, and git status visibility.",
    console: "Ai_Os> Diagnostics plan\n1. Validate static files\n2. Parse registry JSON\n3. Scan unsafe calls\n4. Open preview\n5. Check git status"
  },
  "project-brief": {
    assistant: "Project Brief: shows objective, scope, allowed files, blocked actions, expected result, and next safe action before APPLY.",
    console: "Ai_Os> Project Brief\nObjective: selected packet summary\nAllowed files: explicit list required\nBlocked actions: visible"
  },
  "prompt-stack": {
    assistant: "Prompt Stack: stores approved operator instructions and generated work packet text as visible static context. No prompts are sent anywhere.",
    console: "Ai_Os> Prompt Stack\nMode: static display\nNetwork calls: BLOCKED\nPrivate data: BLOCKED"
  },
  "build-instructions": {
    assistant: "Build Instructions: exact APPLY scope, validators, preview command, rollback notes, and stop conditions for a future approved packet.",
    console: "Ai_Os> Build Instructions\nAPPLY scope: requires approval\nValidators: required\nStop condition: visible"
  },
  "tool-output": {
    assistant: "Tool Output: static area for terminal summaries, validation output, mismatch labels, and blocked-action notes.",
    console: "Ai_Os> Tool Output\nTerminal summary: placeholder\nMismatch reporting: required\nHidden errors: blocked"
  },
  "approval-gate": {
    assistant: "Approval Gate: displays whether APPLY, commit, publishing, persistence, or integration work is allowed. Default is blocked until approved.",
    console: "Ai_Os> Approval Gate\nAPPLY: BLOCKED BY DEFAULT\nCommit/push: APPROVAL REQUIRED\nProduction: NOT APPROVED"
  },
  "validation-queue": {
    assistant: "Validation Queue: path checks, JSON parsing, unsafe scans, visual preview, and final git status before commit.",
    console: "Ai_Os> Validation Queue\nPath checks: required\nJSON parse: required\nUnsafe scan: required\nGit status: required"
  },
  "tool-chatgpt": {
    assistant: "ChatGPT: planning, explanation, workflow design, and draft work packets only. No execution or live order path.",
    console: "Ai_Os> Tool Registry: ChatGPT\nAllowed: planning/review\nBlocked: execution, credentials, trading"
  },
  "tool-codex": {
    assistant: "Codex: approved code and file implementation in the active repo. APPLY, staging, commits, and pushes require explicit human approval.",
    console: "Ai_Os> Tool Registry: Codex\nAllowed: approved patches\nBlocked: unapproved edits and trading paths"
  },
  "tool-claude": {
    assistant: "Claude: optional future review and planning lane. No autonomous execution or credential access.",
    console: "Ai_Os> Tool Registry: Claude\nAllowed: review/planning\nBlocked: execution and credentials"
  },
  "tool-github": {
    assistant: "GitHub: source control and future publishing review. Commits, pushes, workflows, and deployments require approval.",
    console: "Ai_Os> Tool Registry: GitHub\nCommits/pushes: approval required\nDeployment secrets: blocked"
  },
  "tool-powershell": {
    assistant: "PowerShell: local validators and controlled operator commands. No startup tasks, destructive operations, credentials, or trading execution.",
    console: "Ai_Os> Tool Registry: PowerShell\nValidators: allowed\nStartup/system changes: BLOCKED"
  },
  "tool-web": {
    assistant: "Web/Research: public documentation and source research only. No private account scraping, broker access, or credential capture.",
    console: "Ai_Os> Tool Registry: Web/Research\nPublic docs: allowed\nPrivate/session data: BLOCKED"
  },
  "tool-files": {
    assistant: "Files/OneDrive: approved local file inspection in allowed project paths. Private data, browser profiles, deletes, moves, and renames are blocked.",
    console: "Ai_Os> Tool Registry: Files/OneDrive\nAllowed paths: approved only\nDeletes/moves/renames: BLOCKED"
  },
  "tool-reports": {
    assistant: "Reports: display and planning for checkpoint/report outputs. No active report writer or protected root mutation.",
    console: "Ai_Os> Tool Registry: Reports\nDisplay/planning: allowed\nReport writer: INACTIVE"
  },
  "tool-telemetry": {
    assistant: "Telemetry: future fixture-only health/event visibility. No telemetry writer, persistence, private data, broker data, or live market data.",
    console: "Ai_Os> Tool Registry: Telemetry\nFixtures: allowed\nPersistence/private data: BLOCKED"
  },
  "app-calendar": {
    assistant: "Calendar App: static planning example for review windows and checkpoint reminders. No provider API, OAuth, notifications, or persistence.",
    console: "Ai_Os> App Registry: Calendar\nProvider: none\nFixture only: true\nStatus: REVIEW"
  },
  "app-notes": {
    assistant: "Notes App: future instruction and context panel. No note persistence or file writer is active.",
    console: "Ai_Os> App Registry: Notes\nWriter: inactive\nPersistence: BLOCKED\nStatus: DRAFT"
  },
  "app-reports": {
    assistant: "Reports App: future health and checkpoint panel. Report writing remains gated by human approval and validators.",
    console: "Ai_Os> App Registry: Reports\nWriter: inactive\nApproval: required\nStatus: GATED"
  },
  "app-telemetry": {
    assistant: "Telemetry App: future event visibility panel. Active telemetry and persistence remain blocked.",
    console: "Ai_Os> App Registry: Telemetry\nTelemetry writer: inactive\nPersistence: BLOCKED\nStatus: BLOCKED"
  },
  "send-message": {
    assistant: "Preview only. No message sent.",
    console: "Ai_Os> assistant message blocked\nPreview only. No message sent.\nNo backend/API calls."
  }
};

function setActiveTab(target) {
  tabButtons.forEach((button) => button.classList.toggle("active", button.dataset.tab === target));
  panels.forEach((panel) => panel.classList.toggle("active", panel.id === target));
}

function updateOutput(action) {
  const message = messages[action];
  if (!message) return;
  assistantOutput.textContent = message.assistant;
  consoleOutput.textContent = message.console;
}

async function loadJsonFixture(path, fallback) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      return { ...fallback, status: "UNKNOWN", source: path };
    }
    const data = await response.json();
    return { data, source: path };
  } catch (error) {
    return { ...fallback, status: "UNKNOWN", source: path };
  }
}

function normalizeStatusState(value) {
  const raw = String(value || "UNKNOWN").toUpperCase();
  if (raw.includes("FAIL") || raw.includes("INVALID")) return "fail";
  if (raw.includes("BLOCK")) return "blocked";
  if (raw.includes("WARN") || raw.includes("REVIEW")) return "warn";
  if (raw.includes("STALE")) return "stale";
  if (raw.includes("PENDING") || raw.includes("APPLY")) return "pending";
  if (raw.includes("PASS") || raw.includes("COMPLETE") || raw.includes("AVAILABLE")) return "pass";
  return "unknown";
}

function formatMetricValue(value, fallbackText = "UNKNOWN") {
  if (value === undefined || value === null || value === "") return fallbackText;
  return String(value);
}

function summarizeStatus(cardId, payload) {
  const data = payload.data || payload;
  switch (cardId) {
    case "overall":
      return {
        status: data.overall_status || data.status || payload.status,
        value: data.overall_status || data.status || payload.value,
        detail: `${data.phase || "AI_OS"} ${data.stage || "status"}`,
        source: payload.source
      };
    case "progress":
      return {
        status: data.status || payload.status,
        value: `${formatMetricValue(data.percent_complete)}%`,
        detail: `${data.task_name || data.stage || "Progress"} - ${data.completed_steps || 0}/${data.planned_steps || 0} steps. Next: ${data.next_action || "UNKNOWN"}.`,
        source: payload.source
      };
    case "lifetimeTelemetry":
      return {
        status: data.safety?.fixture_only ? "PASS" : payload.status,
        value: `${formatMetricValue(data.git_totals?.commit_count)} commits`,
        detail: `${data.evidence_scope || "UNKNOWN"} - complete lifetime time and bytes remain ${data.time_spent?.complete_lifetime_minutes || "UNKNOWN"}.`,
        source: payload.source
      };
    case "validator":
      return {
        status: data.status,
        value: data.status || "UNKNOWN",
        detail: `${data.validators_run || 0} run, ${data.pass || 0} pass, ${data.warn || 0} warn, ${data.fail || 0} fail.`,
        source: payload.source
      };
    case "checkpoint":
      return {
        status: data.status,
        value: data.mode || data.status || "UNKNOWN",
        detail: data.next_safe_action || data.source || "Checkpoint unknown.",
        source: payload.source
      };
    case "safety":
      return {
        status: data.status,
        value: data.status || "UNKNOWN",
        detail: data.notes || (data.blocked_actions_confirmed || []).join(", ") || "Safety status unknown.",
        source: payload.source
      };
    case "nextAction":
      return {
        status: data.status,
        value: data.status || "UNKNOWN",
        detail: data.next_action || "Next action unavailable.",
        source: payload.source
      };
    case "aiAssistance":
      return {
        status: data.assistant_response?.approval_required ? "PENDING" : data.mode,
        value: data.mode || "LOCAL MOCK",
        detail: data.assistant_response?.message || "AI Assistance placeholder unavailable.",
        source: payload.source
      };
    case "workTableAi":
      return {
        status: data.mode || "LOCAL MOCK",
        value: `${(data.cards || []).length} cards`,
        detail: data.cards?.[0]?.recommendation || "Work Table AI placeholder unavailable.",
        source: payload.source
      };
    default:
      return {
        status: payload.status || "UNKNOWN",
        value: payload.value || "UNKNOWN",
        detail: payload.detail || "Status unavailable - local fixture missing.",
        source: payload.source
      };
  }
}

function setStatusCard(cardId, payload) {
  const card = document.querySelector(`[data-status-card="${cardId}"]`);
  if (!card) return;

  const summary = summarizeStatus(cardId, payload);
  const state = normalizeStatusState(summary.status);
  const value = card.querySelector("[data-status-value]");
  const detail = card.querySelector("[data-status-detail]");
  const source = card.querySelector("[data-status-source]");

  card.classList.remove(
    "status-state-pass",
    "status-state-warn",
    "status-state-fail",
    "status-state-unknown",
    "status-state-stale",
    "status-state-blocked",
    "status-state-pending"
  );
  card.classList.add(`status-state-${state}`);

  if (value) value.textContent = formatMetricValue(summary.value);
  if (detail) detail.textContent = summary.detail || "Status unavailable - local fixture missing.";
  if (source) source.textContent = summary.source || "local fixture";
  if (cardId === "lifetimeTelemetry") {
    renderLifetimeTelemetryPanel(card, payload);
  }
}

function createLifetimeTelemetryMetric(label, value, detail = "") {
  const item = document.createElement("div");
  item.className = "lifetime-telemetry-metric";

  const labelElement = document.createElement("span");
  labelElement.textContent = label;

  const valueElement = document.createElement("strong");
  valueElement.textContent = formatMetricValue(value);

  item.append(labelElement, valueElement);

  if (detail) {
    const detailElement = document.createElement("small");
    detailElement.textContent = detail;
    item.append(detailElement);
  }

  return item;
}

function createLifetimeTelemetryChip(label, value, className = "") {
  const chip = document.createElement("span");
  chip.className = `lifetime-telemetry-chip${className ? ` ${className}` : ""}`;
  chip.textContent = `${label}: ${formatMetricValue(value)}`;
  return chip;
}

function renderLifetimeTelemetryPanel(card, payload) {
  const data = payload.data || payload;
  const grid = card.querySelector("[data-lifetime-telemetry-grid]");
  const unknowns = card.querySelector("[data-lifetime-telemetry-unknowns]");
  const safety = card.querySelector("[data-lifetime-telemetry-safety]");

  if (!grid || !unknowns || !safety) return;

  if (!data || !data.git_totals) {
    grid.textContent = "";
    unknowns.textContent = "Lifetime telemetry fixture unavailable — mock data only.";
    safety.textContent = "";
    return;
  }

  const gitTotals = data.git_totals || {};
  const reportTotals = data.report_totals || {};
  const timeSpent = data.time_spent || {};
  const sizeTotals = data.size_totals || {};
  const qualitySignals = data.quality_signals || {};

  grid.replaceChildren(
    createLifetimeTelemetryMetric("Commits", gitTotals.commit_count, "Evidence-backed git total"),
    createLifetimeTelemetryMetric("Tracked Files", gitTotals.tracked_file_count, "Evidence-backed git file count"),
    createLifetimeTelemetryMetric("Numstat Rows", gitTotals.numstat_file_change_rows, "Not a byte total"),
    createLifetimeTelemetryMetric("Insertions", gitTotals.insertions, "Git line evidence"),
    createLifetimeTelemetryMetric("Deletions", gitTotals.deletions, "Git line evidence"),
    createLifetimeTelemetryMetric("Checkpoints", reportTotals.checkpoint_files, "Reports/checkpoints"),
    createLifetimeTelemetryMetric("Daily Reports", reportTotals.daily_report_files, "Reports/daily"),
    createLifetimeTelemetryMetric("Progress Reports", reportTotals.progress_files, "Reports/progress"),
    createLifetimeTelemetryMetric("Mock Fixtures", reportTotals.dashboard_mock_data_files, "apps/dashboard/mock-data"),
    createLifetimeTelemetryMetric("Partial Minutes", timeSpent.partial_duration_minutes, `${timeSpent.partial_duration_row_count || 0} evidence rows`),
    createLifetimeTelemetryMetric("Validators", qualitySignals.validators, "Partial evidence signal"),
    createLifetimeTelemetryMetric("Pushes", qualitySignals.pushes, "Partial git/checkpoint signal")
  );

  unknowns.replaceChildren(
    createLifetimeTelemetryChip("Complete minutes", timeSpent.complete_lifetime_minutes, "unknown"),
    createLifetimeTelemetryChip("Complete hours", timeSpent.complete_lifetime_hours, "unknown"),
    createLifetimeTelemetryChip("Bytes changed", sizeTotals.complete_lifetime_bytes_changed, "unknown"),
    createLifetimeTelemetryChip("KB changed", sizeTotals.complete_lifetime_kb_changed, "unknown"),
    createLifetimeTelemetryChip("MB changed", sizeTotals.complete_lifetime_mb_changed, "unknown"),
    createLifetimeTelemetryChip("Blockers", qualitySignals.blockers, "unknown"),
    createLifetimeTelemetryChip("Recovery notes", qualitySignals.recovery_notes, "unknown"),
    createLifetimeTelemetryChip("Latest checkpoint", "CHECKPOINT_STAGE44_LIFETIME_TELEMETRY_PUSH_READINESS.md")
  );

  const safetyData = data.safety || {};
  safety.replaceChildren(
    createLifetimeTelemetryChip("Fixture only", safetyData.fixture_only === true ? "YES" : "UNKNOWN", "safe"),
    createLifetimeTelemetryChip("Real collector", safetyData.real_telemetry_collector === false ? "BLOCKED" : "UNKNOWN", "blocked"),
    createLifetimeTelemetryChip("APIs", safetyData.apis, "blocked"),
    createLifetimeTelemetryChip("Secrets", safetyData.secrets, "blocked"),
    createLifetimeTelemetryChip("Deployment", safetyData.deployment, "blocked"),
    createLifetimeTelemetryChip("Broker/trading", safetyData.broker_trading_execution, "blocked"),
    createLifetimeTelemetryChip("Live AI execution", safetyData.live_ai_execution, "blocked")
  );
}

async function loadStatusOverview() {
  if (!statusCards.length) return;
  await Promise.all(Object.entries(statusFixtures).map(async ([cardId, fixture]) => {
    const payload = await loadJsonFixture(fixture.path, fixture.fallback);
    setStatusCard(cardId, payload);
  }));
}

function toolStatusState(value) {
  const status = String(value || "UNKNOWN").toUpperCase();
  if (status === "READY" || status === "INSTALLED" || status === "INTERNAL_MODULE") return "pass";
  if (status === "NEEDS_LOGIN" || status === "NEEDS_CONFIG" || status === "NOT_APPLICABLE") return "warn";
  if (status === "MISSING" || status === "BLOCKED") return "blocked";
  return "unknown";
}

function setToolRegistryMessage(message) {
  if (toolRegistryMessage) {
    toolRegistryMessage.textContent = message;
  }
}

function renderToolRegistry(tools, generatedAt) {
  if (!toolRegistryGrid) return;

  toolRegistryGrid.textContent = "";
  tools.forEach((tool) => {
    const status = tool.detected_status || "UNKNOWN";
    const reason = tool.blocked_reason || tool.notes || "No notes supplied.";
    const checked = tool.last_checked || generatedAt || "DRY_RUN";
    const card = document.createElement("article");
    card.className = `tool-status-card tool-status-${toolStatusState(status)}`;
    card.tabIndex = 0;

    card.innerHTML = `
      <div class="tool-status-head">
        <span class="tool-name"></span>
        <span class="tool-status-pill"></span>
      </div>
      <div class="tool-meta"></div>
      <p class="tool-reason"></p>
      <small class="tool-checked"></small>
    `;

    card.querySelector(".tool-name").textContent = tool.label || tool.tool_id || "UNKNOWN";
    card.querySelector(".tool-status-pill").textContent = status;
    card.querySelector(".tool-meta").textContent = `Type: ${tool.category || "UNKNOWN"}`;
    card.querySelector(".tool-reason").textContent = reason;
    card.querySelector(".tool-checked").textContent = `Last checked: ${checked}`;
    toolRegistryGrid.appendChild(card);
  });
}

function renderToolRegistrySummary(tools) {
  const counts = toolRegistrySummaryStatuses.reduce((result, status) => {
    result[status] = 0;
    return result;
  }, {});

  tools.forEach((tool) => {
    const status = String(tool.detected_status || "UNKNOWN").toUpperCase();
    if (Object.prototype.hasOwnProperty.call(counts, status)) {
      counts[status] += 1;
    } else {
      counts.UNKNOWN += 1;
    }
  });

  toolRegistrySummaryValues.forEach((node) => {
    const key = node.dataset.toolSummary;
    node.textContent = key === "total" ? String(tools.length) : String(counts[key] || 0);
  });
}

async function loadToolRegistryStatus() {
  if (!toolRegistryGrid) return;
  try {
    const response = await fetch(toolRegistryFixturePath, { cache: "no-store" });
    if (!response.ok) throw new Error("Fixture unavailable");
    const data = await response.json();
    const tools = Array.isArray(data.tools) ? data.tools : [];
    setToolRegistryMessage(`Fixture source: ${toolRegistryFixturePath}`);
    renderToolRegistrySummary(tools);
    renderToolRegistry(tools, data.generated_at);
  } catch (error) {
    setToolRegistryMessage("Tool registry fixture unavailable — mock data only.");
    renderToolRegistrySummary([]);
    toolRegistryGrid.textContent = "";
  }
}

function clearNode(node) {
  if (node) {
    node.textContent = "";
  }
}

function setWorkTableAiMessage(message) {
  if (workTableAiMessage) {
    workTableAiMessage.textContent = message;
  }
}

function appendTextChip(parent, label, className = "") {
  if (!parent) return;
  const chip = document.createElement("span");
  chip.className = `work-table-ai-chip${className ? ` ${className}` : ""}`;
  chip.textContent = label || "UNKNOWN";
  parent.appendChild(chip);
}

function renderWorkTableAiMeta(data) {
  clearNode(workTableAiMeta);
  if (!workTableAiMeta) return;

  const fields = [
    ["Mode", data.mode],
    ["Classification", data.classification],
    ["Stage", data.stage],
    ["Task", data.task_name],
    ["Scope", data.scope]
  ];

  fields.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "work-table-ai-meta-item";
    const itemLabel = document.createElement("span");
    const itemValue = document.createElement("strong");
    itemLabel.textContent = label;
    itemValue.textContent = formatMetricValue(value);
    item.append(itemLabel, itemValue);
    workTableAiMeta.appendChild(item);
  });

  if (workTableAiMode) {
    workTableAiMode.textContent = data.mode || "LOCAL MOCK ONLY";
  }
}

function renderWorkTableAiCards(cards) {
  clearNode(workTableAiCards);
  if (!workTableAiCards) return;

  cards.forEach((item) => {
    const card = document.createElement("article");
    card.className = "work-table-ai-card";
    card.tabIndex = 0;

    const head = document.createElement("div");
    head.className = "work-table-ai-card-head";

    const titleWrap = document.createElement("div");
    const label = document.createElement("span");
    const title = document.createElement("h4");
    label.className = "card-label";
    label.textContent = item.label || "WORK CARD";
    title.textContent = item.title || item.id || "UNKNOWN";
    titleWrap.append(label, title);

    const score = document.createElement("strong");
    score.className = "work-table-ai-score";
    score.textContent = formatMetricValue(item.score, "0");
    head.append(titleWrap, score);

    const status = document.createElement("div");
    status.className = "work-table-ai-status";
    status.textContent = `${item.interpreted_status || "UNKNOWN"} / ${item.priority_tier || "UNKNOWN"}`;

    const confidence = document.createElement("div");
    confidence.className = "work-table-ai-confidence";
    confidence.textContent = `Confidence: ${formatMetricValue(item.confidence)}`;

    const recommendation = document.createElement("p");
    recommendation.textContent = item.recommendation || "No recommendation supplied.";

    const reason = document.createElement("small");
    reason.textContent = item.reason || "No reason supplied.";

    const approval = document.createElement("span");
    approval.className = `work-table-ai-approval${item.approval_required ? " required" : ""}`;
    approval.textContent = item.approval_required ? "Approval required" : "No approval required";

    card.append(head, status, confidence, recommendation, reason, approval);
    workTableAiCards.appendChild(card);
  });
}

function renderWorkTableAiActions(actionsData, fixtureData) {
  clearNode(workTableAiSafeActions);
  clearNode(workTableAiBlockedActions);
  clearNode(workTableAiSources);

  const safeActions = Array.isArray(actionsData.safe_mock_actions) ? actionsData.safe_mock_actions : [];
  safeActions.forEach((action) => {
    const label = `${action.label || action.id || "UNKNOWN"} | executes_code: ${Boolean(action.executes_code)} | approval: ${Boolean(action.requires_approval)}`;
    appendTextChip(workTableAiSafeActions, label, action.requires_approval ? "approval" : "");
  });

  const blocked = [
    ...(Array.isArray(fixtureData.blocked_actions) ? fixtureData.blocked_actions : []),
    ...(Array.isArray(actionsData.blocked_actions) ? actionsData.blocked_actions : [])
  ];
  Array.from(new Set(blocked)).forEach((action) => appendTextChip(workTableAiBlockedActions, action, "blocked"));

  const sources = Array.isArray(fixtureData.source_references) ? fixtureData.source_references : [];
  sources.forEach((source) => {
    if (!workTableAiSources) return;
    const item = document.createElement("small");
    item.textContent = source;
    workTableAiSources.appendChild(item);
  });
}

async function loadWorkTableAiInsights() {
  if (!workTableAiCards) return;
  try {
    const [fixtureResponse, actionsResponse] = await Promise.all([
      fetch(workTableAiFixturePath, { cache: "no-store" }),
      fetch(workTableAiActionsFixturePath, { cache: "no-store" })
    ]);

    if (!fixtureResponse.ok || !actionsResponse.ok) throw new Error("Fixture unavailable");

    const fixtureData = await fixtureResponse.json();
    const actionsData = await actionsResponse.json();
    const cards = Array.isArray(fixtureData.cards) ? fixtureData.cards : [];

    setWorkTableAiMessage(`Fixture sources: ${workTableAiFixturePath}; ${workTableAiActionsFixturePath}`);
    renderWorkTableAiMeta(fixtureData);
    renderWorkTableAiCards(cards);
    renderWorkTableAiActions(actionsData, fixtureData);
  } catch (error) {
    setWorkTableAiMessage("Work Table AI fixture unavailable — mock data only.");
    clearNode(workTableAiMeta);
    clearNode(workTableAiCards);
    clearNode(workTableAiSafeActions);
    clearNode(workTableAiBlockedActions);
    clearNode(workTableAiSources);
  }
}

function showStatusPanel(panelId) {
  statusPanelButtons.forEach((button) => {
    const isActive = button.dataset.statusPanelButton === panelId;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });

  statusPanels.forEach((panel) => {
    const isActive = panel.dataset.statusPanel === panelId;
    panel.classList.toggle("active", isActive);
    panel.hidden = !isActive;
  });
}

function pulseTap(target) {
  target.classList.add("tap-pop");
  window.setTimeout(() => target.classList.remove("tap-pop"), 520);
}

function setYouTubeRadioState(message) {
  if (youtubeRadioState) youtubeRadioState.textContent = message;
}

function setYouTubePlayButton(isPlaying) {
  const button = document.querySelector('[data-youtube-radio-control="play"]');
  if (button) button.textContent = isPlaying ? "Pause" : "Play";
}

function loadYouTubeRadioApi() {
  if (window.YT?.Player || youtubeRadioScriptLoading) return;
  youtubeRadioScriptLoading = true;
  const script = document.createElement("script");
  script.src = "https://www.youtube.com/iframe_api";
  script.async = true;
  document.head.appendChild(script);
}

window.onYouTubeIframeAPIReady = function onYouTubeIframeAPIReady() {
  if (!youtubeRadioDock || youtubeRadioPlayer) return;
  youtubeRadioPlayer = new window.YT.Player("youtubeRadioPlayer", {
    height: "120",
    width: "214",
    videoId: youtubeRadioVideoId,
    playerVars: {
      list: youtubeRadioPlaylistId,
      listType: "playlist",
      playsinline: 1,
      rel: 0
    },
    events: {
      onReady: () => {
        setYouTubeRadioState("Ready - click Play");
        if (youtubeRadioShouldPlay) {
          youtubeRadioPlayer.playVideo();
        }
      },
      onStateChange: (event) => {
        if (event.data === window.YT.PlayerState.PLAYING) {
          setYouTubeRadioState("Playing");
          setYouTubePlayButton(true);
        }
        if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
          setYouTubeRadioState("Paused");
          setYouTubePlayButton(false);
        }
      }
    }
  });
};

function ensureYouTubeRadioPlayer() {
  if (youtubeRadioPlayer) return true;
  youtubeRadioShouldPlay = true;
  setYouTubeRadioState("Loading YouTube player");
  if (window.YT?.Player) {
    window.onYouTubeIframeAPIReady();
  } else {
    loadYouTubeRadioApi();
  }
  return false;
}

function handleYouTubeRadioControl(action) {
  if (!youtubeRadioDock) return;

  if (action === "collapse") {
    youtubeRadioDock.classList.toggle("is-collapsed");
    const isCollapsed = youtubeRadioDock.classList.contains("is-collapsed");
    const collapseButton = youtubeRadioDock.querySelector('[data-youtube-radio-control="collapse"]');
    if (collapseButton) {
      collapseButton.textContent = isCollapsed ? "+" : "−";
      collapseButton.setAttribute("aria-label", isCollapsed ? "Expand YouTube Radio" : "Collapse YouTube Radio");
    }
    return;
  }

  if (action === "open") {
    window.open(youtubeRadioPlaylistUrl, "_blank", "noopener,noreferrer");
    return;
  }

  const hasPlayer = ensureYouTubeRadioPlayer();
  if (!hasPlayer) return;

  if (action === "play") {
    const state = youtubeRadioPlayer.getPlayerState();
    if (state === window.YT.PlayerState.PLAYING) {
      youtubeRadioPlayer.pauseVideo();
    } else {
      youtubeRadioPlayer.playVideo();
    }
  }

  if (action === "next") {
    youtubeRadioPlayer.nextVideo();
  }

  if (action === "back") {
    youtubeRadioPlayer.previousVideo();
  }
}

function readSavedDrawerClosed() {
  try {
    const value = window.sessionStorage.getItem(drawerStateKey);
    if (value === "true") return true;
    if (value === "false") return false;
    return null;
  } catch (error) {
    return null;
  }
}

function saveDrawerClosed(isClosed) {
  try {
    window.sessionStorage.setItem(drawerStateKey, String(isClosed));
  } catch (error) {
    // The drawer still works without persisted UI state.
  }
}

function readSavedDashboardTheme() {
  try {
    return window.localStorage.getItem(dashboardThemeKey) || "default";
  } catch (error) {
    return "default";
  }
}

function saveDashboardTheme(themeName) {
  try {
    window.localStorage.setItem(dashboardThemeKey, themeName);
  } catch (error) {
    // The selector still works without persisted visual preference.
  }
}

function applyDashboardTheme(themeName) {
  const nextTheme = dashboardThemeMap[themeName] ? themeName : "default";
  document.body.classList.remove(...dashboardThemeClasses);
  if (dashboardThemeMap[nextTheme]) {
    document.body.classList.add(dashboardThemeMap[nextTheme]);
  }
  if (dashboardThemeSelector) {
    dashboardThemeSelector.value = nextTheme;
  }
  saveDashboardTheme(nextTheme);
}

function applySavedDrawerState() {
  const savedClosed = readSavedDrawerClosed();
  document.body.classList.remove("sidebar-open");
  document.body.classList.toggle("sidebar-collapsed", savedClosed === true && !mobileSidebarQuery.matches);
  if (savedClosed === false && mobileSidebarQuery.matches) {
    document.body.classList.add("sidebar-open");
  }
}

function syncSidebarState() {
  const isMobile = mobileSidebarQuery.matches;
  const isOpen = document.body.classList.contains("sidebar-open");
  const isCollapsed = document.body.classList.contains("sidebar-collapsed");
  const expanded = isMobile ? isOpen : !isCollapsed;
  sidebarToggle.setAttribute("aria-expanded", String(expanded));
  drawerReopen.setAttribute("aria-expanded", String(expanded));
}

function closeSidebar() {
  document.body.classList.remove("sidebar-open");
  if (!mobileSidebarQuery.matches) {
    document.body.classList.add("sidebar-collapsed");
  }
  saveDrawerClosed(true);
  syncSidebarState();
}

function openSidebar() {
  if (mobileSidebarQuery.matches) {
    document.body.classList.add("sidebar-open");
  } else {
    document.body.classList.remove("sidebar-collapsed");
  }
  saveDrawerClosed(false);
  syncSidebarState();
}

function closeMobileSidebar() {
  closeSidebar();
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;
    setActiveTab(target);
    updateOutput(button.dataset.action || target);
  });
});

statusPanelButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showStatusPanel(button.dataset.statusPanelButton);
  });
});

actionButtons.forEach((item) => {
  item.addEventListener("click", () => {
    const action = item.dataset.action;
    actionButtons.forEach((target) => target.classList.toggle("active", target === item));
    if (item.dataset.tab) {
      setActiveTab(item.dataset.tab);
    }
    if (action === "send-message") {
      mockMessage.value = "Preview only. No message sent.";
    }
    updateOutput(action);
  });

  item.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      item.click();
    }
  });
});

tapTargets.forEach((target) => {
  target.addEventListener("pointerup", () => pulseTap(target));
});

if (dashboardThemeSelector) {
  dashboardThemeSelector.addEventListener("change", () => {
    applyDashboardTheme(dashboardThemeSelector.value);
  });
}

youtubeRadioControls.forEach((control) => {
  control.addEventListener("click", () => {
    handleYouTubeRadioControl(control.dataset.youtubeRadioControl);
  });
});

sidebarToggle.addEventListener("click", closeSidebar);
drawerReopen.addEventListener("click", openSidebar);
drawerBackdrop.addEventListener("click", closeMobileSidebar);
mobileSidebarQuery.addEventListener("change", () => {
  applySavedDrawerState();
  syncSidebarState();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && mobileSidebarQuery.matches) {
    closeMobileSidebar();
  }
});

applyDashboardTheme(readSavedDashboardTheme());
applySavedDrawerState();
syncSidebarState();
loadStatusOverview();
loadToolRegistryStatus();
loadWorkTableAiInsights();

window.addEventListener("mousemove", (event) => {
  const x = (event.clientX / window.innerWidth - 0.5).toFixed(3);
  const y = (event.clientY / window.innerHeight - 0.5).toFixed(3);
  document.documentElement.style.setProperty("--mx", x);
  document.documentElement.style.setProperty("--my", y);
});

window.addEventListener("scroll", () => {
  const ratio = Math.min(window.scrollY / 700, 1).toFixed(3);
  document.documentElement.style.setProperty("--scroll", ratio);
}, { passive: true });
