const tabButtons = document.querySelectorAll("[data-tab]");
const actionButtons = document.querySelectorAll("[data-action]");
const panels = document.querySelectorAll(".panel");
const assistantOutput = document.getElementById("assistantOutput");
const consoleOutput = document.getElementById("consoleOutput");
const mockMessage = document.getElementById("mockMessage");
const tapTargets = document.querySelectorAll("button, .glass-card, .chart-card, .work-card, .registry-chip, .app-card");

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

function pulseTap(target) {
  target.classList.add("tap-pop");
  window.setTimeout(() => target.classList.remove("tap-pop"), 520);
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;
    setActiveTab(target);
    updateOutput(button.dataset.action || target);
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
