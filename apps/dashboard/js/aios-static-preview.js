const tabButtons = document.querySelectorAll("[data-tab]");
const actionButtons = document.querySelectorAll("[data-action]");
const panels = document.querySelectorAll(".panel");
const assistantOutput = document.getElementById("assistantOutput");
const consoleOutput = document.getElementById("consoleOutput");
const mockMessage = document.getElementById("mockMessage");

const messages = {
  node: {
    title: "AI_OS Node",
    assistant: "AI_OS Node: core system overview and command center. This mock lane explains local status, safety locks, and operator checkpoints.",
    console: "AI_OS> AI_OS Node selected\nAI_OS> core overview: REVIEW\nAI_OS> command center: static/local only"
  },
  engine: {
    title: "Trading Engine",
    assistant: "Trading Engine: future signal validation and paper execution review. No live execution, no broker routing, and no order placement.",
    console: "AI_OS> Trading Engine selected\nAI_OS> future signal validation: placeholder\nAI_OS> paper execution review: mock only"
  },
  bot: {
    title: "Trading Bot",
    assistant: "Trading Bot: future strategy/regime validation. No live trading, no real buy/sell execution, and no live order path.",
    console: "AI_OS> Trading Bot selected\nAI_OS> strategy/regime validation: future review\nAI_OS> live trading: BLOCKED"
  },
  reports: {
    title: "Reports",
    assistant: "Reports: future health, checkpoint, and progress reporting. No report writer is active in this static preview.",
    console: "AI_OS> Reports selected\nAI_OS> health queue: placeholder\nAI_OS> checkpoint reporting: mock only"
  },
  telemetry: {
    title: "Telemetry",
    assistant: "Telemetry: future system health/event visibility. No persistence yet, no telemetry writer, and no private data collection.",
    console: "AI_OS> Telemetry selected\nAI_OS> event visibility: placeholder\nAI_OS> persistence: BLOCKED"
  },
  admin: {
    title: "Admin",
    assistant: "Admin: approval gates, safety locks, and settings review. All APPLY and integration work requires human approval.",
    console: "AI_OS> Admin selected\nAI_OS> approval gates: manual\nAI_OS> safety locks: enabled"
  },
  "system-status": {
    assistant: "System Status: mock system status shows static preview online, backend disabled, persistence disabled, and safety locks active.",
    console: "AI_OS> System Status\nSTATIC PREVIEW: ONLINE\nBACKEND: DISABLED\nPERSISTENCE: DISABLED\nSAFETY LOCKS: ACTIVE"
  },
  diagnostics: {
    assistant: "Run Diagnostics: mock diagnostics plan would check file presence, UI labels, blocked-action text, and unsafe keyword scans.",
    console: "AI_OS> Diagnostics plan\n1. Validate static files\n2. Scan for unsafe calls\n3. Confirm safety labels\n4. Request human review"
  },
  "view-reports": {
    assistant: "View Reports: mock report queue includes health checkpoints, daily progress drafts, and future audit evidence maps.",
    console: "AI_OS> Report queue\nReports/health: REVIEW\nReports/daily: REVIEW\nAudit evidence: PLACEHOLDER"
  },
  "explain-telemetry": {
    assistant: "Explain Telemetry: mock telemetry is for future system health/event visibility only. No persistence is enabled yet.",
    console: "AI_OS> Telemetry purpose\nSystem health: future placeholder\nEvent visibility: future placeholder\nPersistence: BLOCKED"
  },
  "strategy-insights": {
    assistant: "Strategy Insights: future strategy assistant use case can explain offline ideas and regime notes. It cannot trade or approve orders.",
    console: "AI_OS> Strategy Insights\nOffline analysis: allowed in future review\nOrder approval: BLOCKED\nLive order path: BLOCKED"
  },
  "send-message": {
    assistant: "Preview only. No message sent.",
    console: "AI_OS> assistant message blocked\nPreview only. No message sent.\nNo backend calls."
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

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;
    setActiveTab(target);
    updateOutput(target);
  });
});

actionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const action = button.dataset.action;
    actionButtons.forEach((item) => item.classList.toggle("active", item === button));
    if (button.dataset.tab) {
      setActiveTab(button.dataset.tab);
    }
    if (action === "send-message") {
      mockMessage.value = "Preview only. No message sent.";
    }
    updateOutput(action);
  });
});

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
