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
const drawerStateKey = "aios.drawer.closed";

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
}

async function loadStatusOverview() {
  if (!statusCards.length) return;
  await Promise.all(Object.entries(statusFixtures).map(async ([cardId, fixture]) => {
    const payload = await loadJsonFixture(fixture.path, fixture.fallback);
    setStatusCard(cardId, payload);
  }));
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

applySavedDrawerState();
syncSidebarState();
loadStatusOverview();

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
