const tabButtons = document.querySelectorAll("[data-tab]");
const actionButtons = document.querySelectorAll("[data-action]");
const panels = document.querySelectorAll(".panel");
const commandWorkspaces = document.querySelectorAll("[data-command-workspace]");
const assistantOutput = document.getElementById("assistantOutput");
const consoleOutput = document.getElementById("consoleOutput");
const mockMessage = document.getElementById("mockMessage");
const assistantModeButtons = document.querySelectorAll("[data-assistant-mode]");
const assistantModeLabel = document.querySelector("[data-assistant-mode-label]");
const assistantModeHelper = document.querySelector("[data-assistant-mode-helper]");
const assistantContextFieldsContainer = document.querySelector("[data-assistant-context-fields]");
const assistantContextOutput = document.querySelector("[data-context-packet-output]");
const contextRailTitle = document.querySelector("[data-context-rail-title]");
const contextRailSummary = document.querySelector("[data-context-rail-summary]");
const contextRailList = document.querySelector("[data-context-rail-list]");
const personalRailList = document.querySelector("[data-personal-rail-list]");
const detailKicker = document.querySelector("[data-detail-kicker]");
const detailTitle = document.querySelector("[data-detail-title]");
const detailSubtitle = document.querySelector("[data-detail-subtitle]");
const detailStatus = document.querySelector("[data-detail-status]");
const detailNote = document.querySelector("[data-detail-note]");
const detailList = document.querySelector("[data-detail-list]");
const projectHubPanel = document.querySelector("[data-project-hub]");
const personalGalleryPanel = document.querySelector("[data-personal-gallery]");
const personalAppsPanel = document.querySelector("[data-personal-apps]");
const refreshGuardMessage = document.querySelector("[data-refresh-guard-message]");
const sidebarToggle = document.querySelector(".command-sidebar .sidebar-toggle");
const drawerReopen = document.querySelector(".drawer-reopen");
const drawerBackdrop = document.querySelector(".drawer-backdrop");
const personalRailToggles = document.querySelectorAll("[data-action='toggle-personal-rail']");
const mobileSidebarQuery = window.matchMedia("(max-width: 1120px)");
const tapTargets = document.querySelectorAll("button, .glass-card, .chart-card, .work-card, .workspace-panel, .vault-card, .guide-card, .status-card, .status-panel-button, .registry-chip, .app-card");
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
const youtubeRadioPreviewNote = document.querySelector("[data-youtube-radio-preview-note]");
const youtubeRadioControls = document.querySelectorAll("[data-youtube-radio-control]");
const youtubeRadioVolumeControls = document.querySelectorAll("[data-youtube-radio-volume]");
const drawerStateKey = "aios.drawer.closed";
const personalRailStateKey = "aios.personalRail.closed";
const dashboardThemeKey = "aios.dashboard.theme";
const youtubeDockCollapsedKey = "aios.youtubeDockCollapsed";
const youtubeRadioStateKey = "AIOS_YOUTUBE_DOCK_STATE_V1";
const dashboardWorkspaceStateKey = "AIOS_COMMAND_CENTER_STATE_V1";
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
const personalGalleryManifestPath = "private-media/service-gallery/gallery.local.json";
const youtubeRadioVideoId = "VFzsSbdS7Sk";
const youtubeRadioPlaylistId = "RDVFzsSbdS7Sk";
const youtubeRadioLocalFileFallback = "Embedded playback unavailable in local file preview. Use local server preview or External Handoff.";
const youtubeRadioLocalServerCommand = "Local HTTP preview: python -m http.server 8080";
const youtubeRadioResumeMessage = "Press Play to resume";
let youtubeRadioPlayer = null;
let youtubeRadioScriptLoading = false;
let youtubeRadioShouldPlay = false;
let youtubeRadioPendingAction = null;
let youtubeRadioEmbedMode = "playlist";
let youtubeRadioSingleFallbackAttempted = false;
let youtubeRadioMuted = false;
let youtubeRadioRestoreState = null;
let youtubeRadioRestoreApplied = false;
let youtubeRadioLastKnownPlaying = false;
let activeWorkspaceId = "work-table";
let activeDetailItemId = "project-brief";
let activeAssistantMode = "tour-guide";
let refreshGuardMessageTimer = null;
let musicCompanionWindow = null;

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

const workspaceDetailConfig = {
  "work-table": {
    title: "Work Table",
    summary: "Project packet tools for planning, instructions, output, approvals, and validation.",
    overview: "Choose a Work Table tool from the tab to build a focused project packet before APPLY.",
    items: [
      detailItem("project-brief", "Project Brief", "SCOPE", "Define the project goal, allowed files, source evidence, and expected result before APPLY.", "APPLY remains blocked until the brief is reviewed.", ["Set objective and boundaries.", "List allowed files.", "Name the expected result."]),
      detailItem("prompt-stack", "Prompt Stack", "REQUEST", "Capture the approved operator prompt, constraints, and acceptance notes in one readable packet.", "No prompt is sent to a backend from this static preview.", ["Keep the newest request visible.", "Mark unknown facts.", "Preserve safety constraints."]),
      detailItem("build-instructions", "Build Instructions", "BUILD", "Record exact file scope, validators, preview command, and stop conditions.", "File edits require explicit APPLY approval.", ["Confirm inspected files.", "Define validation commands.", "State stop condition."]),
      detailItem("tool-output", "Tool Output", "OUTPUT", "Summarize terminal output, validation results, mismatch labels, and blocked-action notes.", "Hidden errors are not allowed in the final report.", ["Summarize command results.", "List failures.", "Keep evidence text-based."]),
      detailItem("approval-gate", "Approval Gate", "APPROVAL", "Show whether APPLY, commit, publish, persistence, or integration work is allowed.", "Default state is blocked until the user approves.", ["APPLY approval required.", "Commit/push approval required.", "Production activation blocked."]),
      detailItem("validation-queue", "Validation Queue", "VALIDATION", "Queue path checks, syntax checks, unsafe scans, preview checks, and final git status.", "Validation stays local and static.", ["Run syntax checks.", "Check diff names.", "Report git status."]),
      detailItem("assistant-notes", "Assistant Notes", "GUIDANCE", "Keep beginner-readable guidance, current constraints, and the next safe action in view.", "No message is sent from this static preview.", ["Use simple instructions.", "Include exact next action.", "Avoid unrelated changes."])
    ]
  },
  "trading-bot": {
    title: "Trading Bot",
    summary: "Planning tools for strategy, signal rules, risk, backtests, and locked deployment readiness.",
    overview: "Choose a Trading Bot tool from the tab. This workspace is planning only and cannot place trades.",
    items: [
      detailItem("strategy-builder", "Strategy Builder", "STRATEGY", "Draft strategy ideas, assumptions, source evidence, and review notes.", "No live trading logic is enabled.", ["Describe market idea.", "Mark assumptions.", "Require backtest evidence."]),
      detailItem("signal-rules", "Signal Rules", "SIGNALS", "Plan entry, exit, filter, and invalidation rules without execution.", "Signals do not connect to any broker.", ["Entry rules.", "Exit rules.", "Invalidation rules."]),
      detailItem("backtest-files", "Backtest Files", "FILES", "Plan future approved backtest file references and result review.", "No file writer or file sync runs here.", ["Source files later.", "Result summaries.", "Review gaps."]),
      detailItem("risk-policy", "Risk Policy", "RISK", "Record risk limits, blocked actions, drawdown rules, and approval gates.", "Risk policy cannot enable live trading.", ["Max risk concept.", "Drawdown stop.", "Approval requirement."]),
      detailItem("broker-status", "Broker Status Locked", "LOCKED", "Show broker connector status as locked and non-executable.", "No OANDA, broker API key, order placement, or live trading path is active.", ["Broker API blocked.", "Orders blocked.", "Credentials not stored."]),
      detailItem("deployment-readiness", "Deployment Readiness", "READINESS", "Track dry-run readiness and deployment blockers.", "Production deployment remains blocked.", ["Dry-run checklist.", "Paper review later.", "Deployment locked."]),
      detailItem("trading-validation", "Validation Queue", "VALIDATION", "Review backtest, risk, source log, and paper-trade readiness checks later.", "Validation cannot place trades.", ["Backtest review.", "Risk review.", "Source evidence."])
    ]
  },
  "social-vault": {
    title: "Social Vault",
    summary: "Launch-only planning for social accounts with connectors locked and no passwords stored.",
    overview: "Choose a social item from the tab. This workspace does not store passwords or tokens.",
    items: [
      detailItem("facebook", "Facebook", "ACCOUNT", "Launch-only planning card for Facebook account access.", "No password stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("instagram", "Instagram", "ACCOUNT", "Launch-only planning card for Instagram account access.", "No password stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("x", "X", "ACCOUNT", "Launch-only planning card for X account access.", "No password stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("youtube", "YouTube", "ACCOUNT", "Launch-only planning card for YouTube account access.", "No password stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("social-connector-status", "Connector Status Locked", "LOCKED", "Show social connectors as locked until a future approved secure OAuth setup.", "No real OAuth or social API connection is active.", ["OAuth later.", "API calls blocked.", "Tokens not stored."]),
      detailItem("social-security-notes", "Security Notes", "SECURITY", "Keep account-safety notes and credential boundaries visible.", "Passwords, tokens, and recovery codes must stay out of dashboard files and localStorage.", ["No passwords.", "No tokens.", "No recovery codes."])
    ]
  },
  "onedrive-vault": {
    title: "OneDrive Vault",
    summary: "Important file planning with access locked and no OneDrive token storage.",
    overview: "Choose a file planning item from the tab. This workspace does not connect to OneDrive.",
    items: [
      detailItem("important-documents", "Important Documents", "DOCUMENTS", "Plan which important documents need review, organization, and protection.", "No file sync or cloud connection is active.", ["List document groups.", "Mark protected items.", "Plan review order."]),
      detailItem("aios-project-files", "AI_OS Project Files", "AI_OS", "Organize AI_OS project docs and work packets by approved paths.", "No file writer runs from this panel.", ["Project docs.", "Work packets.", "Source logs."]),
      detailItem("trading-files", "Trading Files", "TRADING", "Separate trading planning files from execution or broker files.", "No broker files or credentials are touched.", ["Planning only.", "Execution separated.", "Risk docs later."]),
      detailItem("backups", "Backups", "BACKUPS", "Plan backup categories and checkpoint timing.", "No backup writer is active.", ["Backup categories.", "Checkpoint timing.", "Restore notes."]),
      detailItem("onedrive-access-status", "Access Status Locked", "LOCKED", "Show OneDrive/file access as locked.", "No OneDrive password, token, or file access is stored.", ["Access locked.", "No token.", "No sync."]),
      detailItem("microsoft-graph-later", "Microsoft Graph Later", "LATER", "Placeholder for a future approved Microsoft Graph or file picker setup.", "Secure auth setup must be designed later.", ["Graph later.", "File picker later.", "Approval required."])
    ]
  },
  "apps-tools": {
    title: "Apps / Tools",
    summary: "Secondary apps and tool lanes for static review only.",
    overview: "Choose an app or tool lane from the tab. Installs and providers remain locked.",
    items: [
      detailItem("planning-tool", "Planning Tool", "CHATGPT", "Planning, explanation, and work packet drafting only.", "No autonomous execution is enabled.", ["Plan tasks.", "Draft reports.", "Review constraints."]),
      detailItem("code-tool", "Code Tool", "CODEX", "Approved local file edits after DRY_RUN and APPLY approval.", "Commits and pushes require separate approval.", ["Inspect files.", "Patch approved scope.", "Run validators."]),
      detailItem("source-control", "Source Control", "GITHUB", "Source control and PR planning lane.", "Commits, pushes, PRs, and publishing require explicit approval.", ["Review diff.", "Plan commit.", "Approval before push."]),
      detailItem("file-tools", "File Tools", "FILES", "Approved local inspection only.", "Deletes, moves, and renames stay blocked.", ["Inspect approved paths.", "No destructive actions.", "Report status."]),
      detailItem("calendar-app", "Calendar App", "CALENDAR", "Static planning example for review windows and checkpoints.", "No provider API connected.", ["Review windows.", "Checkpoint reminders.", "Provider locked."]),
      detailItem("notes-app", "Notes App", "NOTES", "Future instruction and context lane.", "No persistence or file writer active.", ["Instruction notes.", "Context notes.", "Writer locked."]),
      detailItem("apps-diagnostics", "Diagnostics", "DIAGNOSTICS", "Static diagnostics planning for app/tool lanes.", "No automatic repair is active.", ["Static checks.", "Fixture checks.", "Status summary."]),
      detailItem("future-connectors", "Future Connectors", "CONNECTORS", "Placeholder for approved connector design later.", "Credentials and provider APIs remain blocked.", ["Design later.", "No tokens.", "Approval required."])
    ]
  },
  reports: {
    title: "Reports",
    summary: "Checkpoint, validation, health, and export planning without active report writers.",
    overview: "Choose a report lane from the tab. Report writing remains inactive.",
    items: [
      detailItem("daily-reports", "Daily Reports", "DAILY", "Summaries of fixed items, errors, mistakes, and prevention notes.", "Protected root edits require approval.", ["Fixed items.", "Errors.", "Prevention notes."]),
      detailItem("checkpoints", "Checkpoints", "CHECKPOINTS", "Human-readable save points before risky phases.", "Checkpoint writing is not automatic.", ["Current state.", "Next action.", "Stop condition."]),
      detailItem("validation-results", "Validation Results", "VALIDATION", "Static checks, preview notes, and git status summaries.", "Validation results stay text-based.", ["Syntax checks.", "Diff names.", "Git status."]),
      detailItem("health-reports", "Health Reports", "HEALTH", "Mock-only health visibility for local dashboard status.", "No telemetry writer is active.", ["Local status.", "Fixture status.", "Unknowns."]),
      detailItem("metrics", "Metrics", "METRICS", "Planning area for future local metrics summaries.", "No metrics persistence is active.", ["Metric ideas.", "Source evidence.", "Unknowns."]),
      detailItem("export-planning", "Export Planning", "EXPORT", "Plan future report export boundaries.", "No export writer is active.", ["Export format later.", "Protected files.", "Approval required."])
    ]
  },
  safety: {
    title: "Safety",
    summary: "Protected files, locked actions, approval rules, secret rules, and risk boundaries.",
    overview: "Choose a safety topic from the tab before any risky action.",
    items: [
      detailItem("protected-files", "Protected Files", "PROTECTED", "Critical project files require extra care and approval.", "Do not overwrite protected files without approval and backup when required.", ["README/AGENTS/RISK.", "Logs and reports.", "White paper docs."]),
      detailItem("locked-actions", "Locked Actions", "LOCKED", "Deletes, moves, renames, pushes, merges, auth changes, and live execution remain blocked.", "User approval is mandatory for protected actions.", ["No delete.", "No move/rename.", "No push/merge."]),
      detailItem("approval-rules", "Approval Rules", "APPROVAL", "DRY_RUN first, then explicit APPLY approval.", "No default APPLY without approval.", ["Inspect.", "DRY_RUN.", "APPLY only after approval."]),
      detailItem("blocked-execution", "Blocked Execution", "EXECUTION", "Live trading, broker orders, automatic redirects, and production activation are blocked.", "No broker connection or order path is active.", ["No live trading.", "No broker orders.", "No automatic redirect."]),
      detailItem("secret-rules", "Secret Rules", "SECRETS", "Passwords, tokens, API keys, broker keys, and recovery codes must not be stored.", "Secrets stay out of dashboard files, localStorage, and mock data.", ["No passwords.", "No tokens.", "No recovery codes."]),
      detailItem("safety-risk-policy", "Risk Policy", "RISK", "Risk and safety boundaries for AI_OS and future trading work.", "Trading execution is separate and locked.", ["Separate AI_OS/trading.", "Risk review.", "Approval gates."])
    ]
  },
  admin: {
    title: "Admin",
    summary: "Dashboard settings, local preview, diagnostics, mock data status, and safe system info.",
    overview: "Choose an admin topic from the tab. This dashboard does not change system settings.",
    items: [
      detailItem("dashboard-settings", "Dashboard Settings", "SETTINGS", "Static settings overview for dashboard behavior.", "No system or browser policy settings are changed.", ["Static preview.", "Local only.", "No system changes."]),
      detailItem("theme", "Theme", "THEME", "Theme selector controls the visual dashboard theme.", "Theme is the only dashboard UI preference stored locally.", ["Default dark.", "Terminal green.", "High contrast."]),
      detailItem("local-preview", "Local Preview", "PREVIEW", "Use local HTTP preview for embedded YouTube.", "Preview command: python -m http.server 8080", ["Open apps/dashboard.", "Run server.", "Visit 127.0.0.1:8080."]),
      detailItem("diagnostics", "Diagnostics", "DIAGNOSTICS", "Static checklist for syntax, diff, preview, and safety checks.", "No automatic repair or system changes.", ["Syntax check.", "Diff check.", "Git status."]),
      detailItem("mock-data-status", "Mock Data Status", "MOCK DATA", "Fixture visibility and static fallback status.", "No backend data connection is active.", ["Fixtures only.", "Fallback safe.", "Unknowns reported."]),
      detailItem("system-info", "System Info", "SYSTEM", "Safe local preview boundaries and status notes.", "Registry, firewall, VPN, browser policies, and security settings are not changed.", ["Local preview.", "No registry edits.", "No security changes."])
    ]
  }
};

const railDetailConfig = {
  build: {
    title: "Work Tab",
    summary: "Productive work, DevOps, app building, projects, reports, safety, and approval-safe build lanes.",
    overview: "Choose a Build tab item to open one focused project or DevOps detail panel.",
    items: [
      detailItem("start-here", "Start Here", "GUIDE", "Begin with a simple command-center overview: pick a tab item, review the purpose, and keep APPLY blocked until approved.", "Static guide only. No backend or execution logic runs here.", ["Choose one tab item.", "Review purpose and locks.", "Use Soft Refresh for dashboard-only updates."]),
      detailItem("projects", "Projects", "PROJECTS", "Open active project folders for AI_OS, Trading Bot, App Builder, Web Dev, and future projects.", "Projects are static folders with mock telemetry, reports, validation, files, risks, and next actions.", ["Open a project folder.", "Review project telemetry.", "Keep execution locked."]),
      detailItem("work-table", "Work Table", "PROJECT", "Start or continue a guided project packet with brief, prompt stack, build instructions, tool output, approval gate, and validation queue.", "File edits remain blocked until explicit APPLY approval.", ["Define scope.", "Confirm allowed files.", "List validation steps."]),
      detailItem("code-tools", "Code Tools", "CODE", "Use approved local coding tools for inspected files, syntax checks, and focused patches.", "Commits and pushes require separate explicit approval.", ["Inspect first.", "Patch approved scope.", "Run syntax checks."]),
      detailItem("source-control", "Source Control", "GIT", "Review git status, diff names, checkpoint needs, and future commit planning.", "No commit, push, merge, reset, or clean is performed from this static dashboard.", ["Check git status.", "Review diff names.", "Ask before commit or push."]),
      detailItem("reports", "Reports", "REPORTS", "Track daily reports, checkpoints, validation results, health summaries, metrics, and export planning.", "Report writers remain inactive until approved.", ["Summarize changes.", "List errors.", "Capture next safe action."]),
      detailItem("safety", "Safety", "LOCKS", "Review protected files, locked actions, approval rules, blocked execution, secret rules, and risk boundaries.", "Secrets, destructive actions, and live execution stay blocked.", ["No secrets.", "No destructive actions.", "Approval before protected work."]),
      detailItem("admin", "Admin", "SETTINGS", "Manage static dashboard settings, theme guidance, local preview notes, diagnostics, mock data status, and safe system information.", "No system settings, registry, browser policy, firewall, VPN, or security setting is changed.", ["Theme is local UI only.", "Preview stays local.", "Diagnostics are static."]),
      detailItem("deployment-readiness", "Deployment Readiness", "READINESS", "Check deployment blockers, preview status, validation gates, and approval requirements.", "Production deployment remains blocked.", ["Confirm validators.", "Review blockers.", "Require approval."]),
      detailItem("validation-queue", "Validation Queue", "VALIDATION", "Queue syntax checks, diff checks, preview checks, safety scans, and final git status.", "Validation stays local and text-based.", ["Run checks.", "Report failures.", "Show git status."])
    ]
  },
  personal: {
    title: "Personal Tab",
    summary: "Social accounts, documents, personal apps, data, backups, and locked connector planning.",
    overview: "Choose a Personal tab item to open one focused Social, Vault, or personal data detail panel.",
    items: [
      detailItem("personal-apps", "Personal Apps", "APPS", "Open connector-locked social, OneDrive, calendar, and notes planning cards.", "No external app login, API, OAuth, file sync, or persistence is enabled.", ["Open app cards.", "No passwords stored.", "Connectors locked."]),
      detailItem("important-documents", "Important Documents", "DOCUMENTS", "Plan important document groups, review priority, and protected-file boundaries.", "No file access or cloud sync runs from this dashboard.", ["List document groups.", "Mark protected items.", "Plan review order."]),
      detailItem("personal-gallery", "Personal Gallery", "LOCAL MEDIA", "Personal Gallery / Service Photos. Local-only private media area for service photos and approved personal images.", "Place images in apps/dashboard/private-media/service-gallery/. Do not add ID cards, credentials, documents, addresses, account screenshots, recovery codes, or sensitive identity files.", ["Local-only media.", "Manifest later: private-media/service-gallery/gallery.local.json.", "Sensitive images require REDACT REQUIRED."]),
      detailItem("backups", "Backups", "BACKUPS", "Plan backup categories, checkpoint timing, and restore notes for important work.", "No backup writer or file mover is active.", ["Backup categories.", "Checkpoint timing.", "Restore notes."]),
      detailItem("account-security", "Account Security", "SECURITY", "Keep account safety boundaries visible for social, OneDrive, and personal apps.", "Passwords, tokens, recovery codes, and private keys must stay out of dashboard files and localStorage.", ["No passwords.", "No tokens.", "No recovery codes."]),
      detailItem("connector-status-locked", "Connector Status Locked", "LOCKED", "Show all personal connectors as locked until a future approved secure setup.", "No OAuth, API calls, token storage, or real account connection is active.", ["OAuth later.", "API calls blocked.", "Tokens not stored."])
    ]
  }
};

const personalAppsItems = [
  detailItem("facebook", "Facebook", "ACCOUNT", "Facebook account planning card for future secure launch or connector design.", "No password stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("instagram", "Instagram", "ACCOUNT", "Instagram account planning card for future secure launch or connector design.", "No password stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("x", "X", "ACCOUNT", "X account planning card for future secure launch or connector design.", "No password stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("youtube", "YouTube", "ACCOUNT", "YouTube account planning and music workspace boundary notes.", "No YouTube account password or token is stored.", ["No credential capture.", "Music controls preserved.", "Connector locked."]),
  detailItem("onedrive-vault", "OneDrive Vault", "FILES", "OneDrive file planning and future approved Microsoft Graph/File Picker setup.", "No OneDrive password, Microsoft Graph token, or file sync is active.", ["Plan file groups.", "Keep access locked.", "Graph/File Picker later."]),
  detailItem("calendar", "Calendar", "CALENDAR", "Static calendar planning for review windows, checkpoints, and reminders.", "No Google, Microsoft, Outlook, or notification provider is connected.", ["Plan dates.", "Review checkpoints.", "Provider locked."]),
  detailItem("notes", "Notes", "NOTES", "Static notes planning for personal reminders, project context, and future instruction packets.", "No note writer or persistence is active.", ["Draft notes.", "Keep secrets out.", "Writer locked."])
];

const legacyWorkspaceRailMap = {
  "work-table": { rail: "build", detail: "work-table" },
  "trading-bot": { rail: "build", detail: "trading-bot" },
  "apps-tools": { rail: "build", detail: "app-builder" },
  reports: { rail: "build", detail: "reports" },
  safety: { rail: "build", detail: "safety" },
  admin: { rail: "build", detail: "admin" },
  "social-vault": { rail: "personal", detail: "social-vault" },
  "onedrive-vault": { rail: "personal", detail: "onedrive-vault" }
};

const assistantModes = {
  "tour-guide": {
    label: "Tour Guide",
    helper: "Explains the dashboard, buttons, rails, and workflows. Mock-only. Backend not connected.",
    placeholder: "Ask how to use this AI_OS screen..."
  },
  "work-table-builder": {
    label: "Work Table Builder",
    helper: "Helps shape project packets, Codex prompts, DRY_RUN/APPLY scope, and validation plans. Mock-only.",
    placeholder: "Describe the project packet you want to build..."
  },
  "research-chat": {
    label: "Research / Chat",
    helper: "Simple conversation, explanations, notes, and research planning. Mock-only.",
    placeholder: "Ask a question or draft notes..."
  },
  "system-engineer": {
    label: "System Engineer",
    helper: "Plans PC, PowerShell, Git, local server, and dashboard troubleshooting steps. Mock-only.",
    placeholder: "Describe the local system issue..."
  },
  "trading-lab": {
    label: "Trading Lab",
    helper: "Trading bot planning, strategy notes, risk policy, and validation planning only. No trading execution.",
    placeholder: "Plan a trading bot idea without execution..."
  }
};

const assistantContextConfigs = {
  "tour-guide": {
    title: "Tour Guide Context",
    required: ["screen", "target", "level", "desiredOutput"],
    fields: [
      { id: "screen", label: "What screen am I on?", type: "input" },
      { id: "target", label: "What button/rail do I need explained?", type: "input" },
      { id: "level", label: "Beginner or advanced explanation?", type: "select", options: ["Beginner", "Advanced", "Quick orientation"] },
      { id: "desiredOutput", label: "Desired output", type: "select", options: ["Walkthrough", "Quick answer", "Step list"] }
    ]
  },
  "work-table-builder": {
    title: "Full Context Intake Packet",
    required: ["userGoal", "project", "filesOrArea", "desiredOutput", "approvalState"],
    fields: [
      { id: "userGoal", label: "What am I trying to do?", type: "textarea" },
      { id: "project", label: "Which project?", type: "input" },
      { id: "filesOrArea", label: "What files or app area?", type: "input" },
      { id: "desiredOutput", label: "What result do I want?", type: "input" },
      { id: "constraints", label: "Any special constraints?", type: "textarea" },
      { id: "evidence", label: "Any screenshots/logs/files involved?", type: "input" },
      { id: "approvalState", label: "Is this DRY_RUN only or APPLY-ready?", type: "select", options: ["DRY_RUN only", "APPLY-ready after approval", "Question / planning only"] }
    ]
  },
  "research-chat": {
    title: "Research / Chat Packet",
    required: ["researchTopic", "freshSources", "depthLevel", "outputFormat"],
    fields: [
      { id: "researchTopic", label: "Research topic", type: "textarea" },
      { id: "freshSources", label: "Current/fresh sources required?", type: "select", options: ["Yes, current sources required", "No, general explanation is okay", "Unsure"] },
      { id: "depthLevel", label: "Depth level", type: "select", options: ["Quick", "Standard", "Deep"] },
      { id: "outputFormat", label: "Output format", type: "input" },
      { id: "notes", label: "Notes to include", type: "textarea" },
      { id: "citationRequirement", label: "Source/citation requirement", type: "input" }
    ]
  },
  "system-engineer": {
    title: "System Engineer Packet",
    required: ["deviceArea", "toolInvolved", "desiredFix", "riskLevel", "permissionNeeded"],
    fields: [
      { id: "deviceArea", label: "Device or OS area", type: "input" },
      { id: "toolInvolved", label: "App/tool involved", type: "input" },
      { id: "errorOutput", label: "Error/log/command output", type: "textarea" },
      { id: "desiredFix", label: "Desired fix", type: "input" },
      { id: "riskLevel", label: "Risk level", type: "select", options: ["Low", "Medium", "High / ask first"] },
      { id: "permissionNeeded", label: "Permission needed before action", type: "select", options: ["DRY_RUN only", "Ask before APPLY", "Ask before command"] }
    ]
  },
  "trading-lab": {
    title: "Trading Lab Planning Packet",
    required: ["market", "timeframe", "strategyIdea", "riskRule", "brokerStatus"],
    fields: [
      { id: "market", label: "Market/instrument", type: "input" },
      { id: "timeframe", label: "Timeframe", type: "input" },
      { id: "strategyIdea", label: "Strategy idea", type: "textarea" },
      { id: "indicatorRules", label: "Indicators/rules", type: "textarea" },
      { id: "riskRule", label: "Risk rule", type: "input" },
      { id: "backtestEvidence", label: "Backtest evidence", type: "textarea" },
      { id: "brokerStatus", label: "Broker/execution status", type: "select", options: ["Locked / planning only", "Paper planning only", "UNKNOWN"] }
    ]
  }
};

const projectHubConfig = [
  {
    title: "AI_OS",
    summary: "System-level dashboard, rails, assistant console, local preview, and safe orchestration workspace.",
    telemetry: ["AI_OS telemetry", "LOCAL MOCK", "Validation queued", "Next actions static"]
  },
  {
    title: "Trading Bot",
    summary: "Strategy planning, signal notes, risk policy, backtest files, and deployment readiness. No live execution.",
    telemetry: ["Trading Bot telemetry", "Broker locked", "Risk review", "Validation queued"]
  },
  {
    title: "App Builder",
    summary: "Generated app planning, UI packets, static previews, and future approval-safe app work.",
    telemetry: ["App Builder telemetry", "Mock reports", "Files planned", "Risks locked"]
  },
  {
    title: "Web Dev",
    summary: "Dashboard UI, local server preview, responsive checks, and browser-safe development packets.",
    telemetry: ["Web Dev telemetry", "Local preview", "Diff checks", "Next actions static"]
  },
  {
    title: "Future Project",
    summary: "Reserved folder for the next approved project packet.",
    telemetry: ["Future telemetry", "Not started", "Reports empty", "Validation pending"]
  }
];

const projectSections = ["Project Brief", "Work Packets", "Telemetry", "Reports", "Validation", "Files / Paths", "Risks / Safety", "Next Actions"];

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
  "trading-bot": {
    assistant: "Trading Bot: static planning workspace for strategy, signals, backtest files, risk policy, deployment readiness, and validation. Broker connector status is locked.",
    console: "Ai_Os> Trading Bot workspace\nBroker connector: LOCKED\nLive trading: BLOCKED\nSecrets/tokens/API keys: NOT STORED"
  },
  "social-vault": {
    assistant: "Social Vault: launch-only planning cards for Facebook, Instagram, X, and YouTube. Connectors are locked and no passwords or OAuth tokens are stored.",
    console: "Ai_Os> Social Vault workspace\nAccount passwords: NOT STORED\nOAuth/API setup: REQUIRED LATER\nConnectors: LOCKED"
  },
  "onedrive-vault": {
    assistant: "OneDrive Vault: static file organization workspace for important documents, AI_OS files, trading files, and backups. Microsoft Graph and file picker setup are later locked steps.",
    console: "Ai_Os> OneDrive Vault workspace\nOneDrive secrets: NOT STORED\nFile access: LOCKED\nMicrosoft Graph/File Picker: LATER"
  },
  "apps-tools": {
    assistant: "Apps / Tools: static review workspace for secondary apps and tool lanes. Installs, providers, credentials, and execution remain locked.",
    console: "Ai_Os> Apps / Tools workspace\nInstalls: BLOCKED\nProvider APIs: NONE\nCredentials/execution: BLOCKED"
  },
  reports: {
    assistant: "Reports: daily reports, checkpoints, validation results, mismatch notes, and safe next actions. Report writers remain inactive.",
    console: "Ai_Os> Reports workspace\nReport writer: INACTIVE\nCheckpoints: STATIC\nProtected root edits: BLOCKED"
  },
  telemetry: {
    assistant: "Telemetry: future system health/event visibility using approved fixtures first. No telemetry writer and no persistence are enabled.",
    console: "Ai_Os> Telemetry selected\nTelemetry writer: INACTIVE\nPersistence: BLOCKED\nPrivate data: BLOCKED"
  },
  admin: {
    assistant: "Admin: dashboard settings, local preview status, diagnostic planning, and safe system status. This static preview cannot change system settings.",
    console: "Ai_Os> Admin workspace\nLocal preview: python -m http.server 8080\nSystem changes: BLOCKED\nLive automation: BLOCKED"
  },
  safety: {
    assistant: "Safety: protected files, locked actions, approvals, blocked execution, and credential boundaries remain visible before APPLY.",
    console: "Ai_Os> Safety workspace\nSecrets: BLOCKED\nDeletes/moves/renames: BLOCKED\nLive execution/trading: BLOCKED"
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

function detailItem(id, title, status, body, note, checklist = []) {
  return { id, title, status, body, note, checklist };
}

function setActiveTab(target, selectedItemId) {
  tabButtons.forEach((button) => button.classList.toggle("active", button.dataset.tab === target));
  panels.forEach((panel) => panel.classList.toggle("active", panel.id === target));
  commandWorkspaces.forEach((workspace) => {
    const isDetailPanel = workspace.dataset.commandWorkspace === "detail-panel";
    workspace.classList.toggle("active", isDetailPanel);
    workspace.hidden = !isDetailPanel;
  });
  const railTarget = resolveRailTarget(target, selectedItemId);
  renderRailSelection(railTarget.rail, railTarget.detail);
  saveCommandCenterState();
}

function updateOutput(action) {
  const message = messages[action];
  if (!message) return;
  if (assistantOutput) assistantOutput.textContent = message.assistant;
  if (consoleOutput) consoleOutput.textContent = message.console;
}

function renderWorkspaceRail(workspaceId, selectedItemId) {
  const railTarget = resolveRailTarget(workspaceId, selectedItemId);
  renderRailSelection(railTarget.rail, railTarget.detail);
}

function resolveRailTarget(target, selectedItemId) {
  if (railDetailConfig[target]) {
    return {
      rail: target,
      detail: selectedItemId || railDetailConfig[target].items[0].id
    };
  }
  if (legacyWorkspaceRailMap[target]) {
    return {
      rail: legacyWorkspaceRailMap[target].rail,
      detail: selectedItemId || legacyWorkspaceRailMap[target].detail
    };
  }
  return { rail: "build", detail: selectedItemId || "start-here" };
}

function findRailItem(railId, itemId) {
  const rail = railDetailConfig[railId] || railDetailConfig.build;
  return rail.items.find((item) => item.id === itemId) || rail.items[0];
}

function renderRailSelection(railId, selectedItemId) {
  const rail = railDetailConfig[railId] || railDetailConfig.build;
  const selectedItem = findRailItem(railId, selectedItemId);
  activeWorkspaceId = railDetailConfig[railId] ? railId : "build";
  activeDetailItemId = selectedItem.id;

  renderRailButtons(contextRailList, "build", selectedItem.id);
  renderRailButtons(personalRailList, "personal", selectedItem.id);

  if (contextRailTitle) contextRailTitle.textContent = railDetailConfig.build.title;
  if (contextRailSummary) contextRailSummary.textContent = railDetailConfig.build.summary;

  if (mobileSidebarQuery.matches) {
    if (activeWorkspaceId === "build") {
      document.body.classList.remove("personal-rail-open");
    } else {
      document.body.classList.remove("sidebar-open");
      document.body.classList.add("personal-rail-open");
    }
    syncSidebarState();
    syncPersonalRailState();
  }

  renderDetailPanel(rail, selectedItem);
}

function renderRailButtons(container, railId, selectedItemId) {
  if (!container) return;
  const rail = railDetailConfig[railId];
  container.replaceChildren();
  rail.items.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = railId === "personal" ? "rail-nav-button personal-rail-button" : "rail-nav-button context-rail-button";
    button.dataset.rail = railId;
    button.dataset.contextItem = item.id;
    button.textContent = item.title;
    if (item.id === selectedItemId) button.classList.add("active");
    button.addEventListener("click", () => {
      renderRailSelection(railId, item.id);
      saveCommandCenterState();
    });
    container.append(button);
  });
}

function renderDetailPanel(workspace, item) {
  hideProjectHub();
  hidePersonalGallery();
  hidePersonalApps();
  if (detailKicker) detailKicker.textContent = workspace.title;
  if (detailTitle) detailTitle.textContent = item.title;
  if (detailSubtitle) detailSubtitle.textContent = workspace.overview;
  if (detailStatus) detailStatus.textContent = item.status;
  if (assistantOutput) assistantOutput.textContent = item.body;
  if (detailNote) detailNote.textContent = item.note;
  if (consoleOutput) {
    consoleOutput.textContent = `Ai_Os> ${workspace.title}\nAi_Os> ${item.title}\nAi_Os> Static mock-only detail panel`;
  }
  if (detailList) {
    detailList.replaceChildren(...item.checklist.map((entry) => {
      const listItem = document.createElement("li");
      listItem.textContent = entry;
      return listItem;
    }));
  }
  if (item.id === "personal-gallery") {
    renderPersonalGallery();
  }
  if (item.id === "projects") {
    renderProjectHub();
  }
  if (item.id === "personal-apps") {
    renderPersonalApps();
  }
}

function hideProjectHub() {
  if (!projectHubPanel) return;
  projectHubPanel.hidden = true;
  projectHubPanel.replaceChildren();
}

function renderProjectHub() {
  if (!projectHubPanel) return;
  projectHubPanel.hidden = false;
  const notice = document.createElement("div");
  notice.className = "project-hub-notice";
  notice.textContent = "Project folders are mock-only. Telemetry, reports, validation, files, risks, and next actions are static planning views with no backend, API, broker, file writer, or execution state.";

  const grid = document.createElement("div");
  grid.className = "project-card-grid";
  projectHubConfig.forEach((project) => {
    const card = document.createElement("article");
    card.className = "project-card";
    const title = document.createElement("h3");
    title.textContent = project.title;
    const summary = document.createElement("p");
    summary.textContent = project.summary;
    const sections = document.createElement("div");
    sections.className = "project-section-list";
    projectSections.forEach((section) => {
      const chip = document.createElement("span");
      chip.textContent = section;
      sections.append(chip);
    });
    const telemetry = document.createElement("div");
    telemetry.className = "project-telemetry-row";
    project.telemetry.forEach((item) => {
      const chip = document.createElement("span");
      chip.textContent = item;
      telemetry.append(chip);
    });
    card.append(title, summary, sections, telemetry);
    grid.append(card);
  });
  projectHubPanel.replaceChildren(notice, grid);
}

function hidePersonalApps() {
  if (!personalAppsPanel) return;
  personalAppsPanel.hidden = true;
  personalAppsPanel.replaceChildren();
}

function renderPersonalApps() {
  if (!personalAppsPanel) return;
  personalAppsPanel.hidden = false;

  const notice = document.createElement("div");
  notice.className = "personal-apps-notice";
  const noticeTitle = document.createElement("strong");
  noticeTitle.textContent = "Connector-locked personal apps";
  const noticeBody = document.createElement("span");
  noticeBody.textContent = "Launch and connector planning only. No passwords, OAuth, API calls, OneDrive tokens, social tokens, or persistence are enabled.";
  notice.append(noticeTitle, noticeBody);

  const grid = document.createElement("div");
  grid.className = "personal-apps-grid";

  personalAppsItems.forEach((app) => {
    const card = document.createElement("article");
    card.className = "personal-app-card";

    const label = document.createElement("span");
    label.className = "card-label";
    label.textContent = app.status;

    const title = document.createElement("strong");
    title.textContent = app.title;

    const body = document.createElement("p");
    body.textContent = app.body;

    const lock = document.createElement("small");
    lock.textContent = app.note;

    card.append(label, title, body, lock);
    grid.append(card);
  });

  personalAppsPanel.replaceChildren(notice, grid);
}

function setAssistantMode(modeId) {
  const mode = assistantModes[modeId] || assistantModes["tour-guide"];
  activeAssistantMode = assistantModes[modeId] ? modeId : "tour-guide";
  assistantModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.assistantMode === activeAssistantMode);
    button.setAttribute("aria-pressed", String(button.dataset.assistantMode === activeAssistantMode));
  });
  if (assistantModeLabel) assistantModeLabel.textContent = mode.label;
  if (assistantModeHelper) assistantModeHelper.textContent = mode.helper;
  renderAssistantContextForm();
  if (mockMessage) {
    mockMessage.placeholder = mode.placeholder;
    if (!mockMessage.value || mockMessage.value === "Preview only. No message sent.") {
      mockMessage.value = mode.placeholder;
    }
  }
}

function renderAssistantContextForm() {
  if (!assistantContextFieldsContainer) return;
  const config = assistantContextConfigs[activeAssistantMode] || assistantContextConfigs["tour-guide"];
  assistantContextFieldsContainer.replaceChildren();
  config.fields.forEach((fieldConfig) => {
    const label = document.createElement("label");
    const labelText = document.createElement("span");
    labelText.textContent = fieldConfig.label;
    let control;
    if (fieldConfig.type === "textarea") {
      control = document.createElement("textarea");
      control.rows = 2;
    } else if (fieldConfig.type === "select") {
      control = document.createElement("select");
      (fieldConfig.options || []).forEach((optionValue) => {
        const option = document.createElement("option");
        option.value = optionValue;
        option.textContent = optionValue;
        control.append(option);
      });
    } else {
      control = document.createElement("input");
      control.type = "text";
    }
    control.dataset.contextField = fieldConfig.id;
    label.append(labelText, control);
    assistantContextFieldsContainer.append(label);
  });
  if (assistantContextOutput) {
    assistantContextOutput.textContent = `${config.title} not generated yet.`;
  }
}

function sendMockAssistantMessage() {
  const mode = assistantModes[activeAssistantMode] || assistantModes["tour-guide"];
  const message = mockMessage?.value?.trim() || mode.placeholder;
  if (assistantOutput) {
    assistantOutput.textContent = `${mode.label}: backend is not connected yet. Mock-only preview received: ${message}`;
  }
  if (consoleOutput) {
    consoleOutput.textContent = `Ai_Os> AI_OS Assistant Console\nMode: ${mode.label}\nEndpoint: /api/assistant/chat (planned only)\nBackend: NOT CONNECTED\nSecrets/API keys: SERVER-SIDE ONLY\nMessage: ${message}`;
  }
  if (mockMessage) mockMessage.value = mode.placeholder;
}

function readAssistantContextFields() {
  return Array.from(document.querySelectorAll("[data-context-field]")).reduce((result, field) => {
    result[field.dataset.contextField] = field.value.trim();
    return result;
  }, {});
}

function setContextMissingState(field, isMissing) {
  const wrapper = field.closest("label");
  if (wrapper) wrapper.classList.toggle("missing-context", isMissing);
}

function generateContextPacket() {
  if (!assistantContextOutput) return;
  const mode = assistantModes[activeAssistantMode] || assistantModes["tour-guide"];
  const config = assistantContextConfigs[activeAssistantMode] || assistantContextConfigs["tour-guide"];
  const values = readAssistantContextFields();
  const requiredFields = config.required || [];
  const missing = requiredFields.filter((fieldName) => !values[fieldName]);

  document.querySelectorAll("[data-context-field]").forEach((field) => {
    setContextMissingState(field, missing.includes(field.dataset.contextField));
  });

  const packet = {
    "Project identity": values.project || values.market || values.researchTopic || "Missing context required",
    "Assistant mode": mode.label,
    "Current workspace": activeWorkspaceId || "UNKNOWN",
    "Current selected rail/detail item": activeDetailItemId || "UNKNOWN",
    "User goal": values.userGoal || values.researchTopic || values.strategyIdea || values.desiredFix || values.target || "Missing context required",
    "Files/app area": values.filesOrArea || values.toolInvolved || values.screen || values.market || "Missing context required",
    "Desired output": values.desiredOutput || values.outputFormat || values.desiredFix || "Missing context required",
    "Safety rules": "Local mock-only. Do not store secrets, tokens, passwords, API keys, broker keys, social tokens, OneDrive tokens, approvals, or execution state.",
    "Allowed actions": "Explain, plan, draft prompts, organize DRY_RUN/APPLY scope, and propose validation steps.",
    "Blocked actions": "No backend/API call, no trading execution, no broker connection, no credential capture, no location.reload().",
    "Folder ownership": "ACTIVE_REPO dashboard files only unless future approval expands scope.",
    "Current repo state": "Use git status before APPLY. Preserve existing user changes.",
    "Toolchain": "Static dashboard preview, local HTTP server, browser UI, Codex-approved file edits only.",
    "Verification rules": "Run syntax checks, diff checks, safe keyword scans, and report git status.",
    "Output format": "Beginner-readable action plan with exact next safe action.",
    "Required approvals": values.approvalState || values.permissionNeeded || "Mock-only; approval required before APPLY.",
    "Stop conditions": "Stop before secrets, live execution, broker actions, destructive file actions, commits, pushes, or unclear scope.",
    "Known unknowns": values.evidence || values.errorOutput || values.backtestEvidence || "No screenshots/logs/files listed.",
    "Special constraints": values.constraints || values.riskRule || values.citationRequirement || "None listed.",
    "Mode-specific fields": Object.entries(values).map(([key, value]) => `${key}=${value || "Missing context required"}`).join("; "),
    "Next safe action": missing.length ? "Fill missing context required fields before APPLY." : "Review generated packet, then request DRY_RUN or APPLY explicitly."
  };

  assistantContextOutput.textContent = [
    missing.length ? `Missing context required: ${missing.join(", ")}` : "Context packet generated locally.",
    "",
    ...Object.entries(packet).map(([key, value]) => `${key}: ${value}`)
  ].join("\n");
}

function hidePersonalGallery() {
  if (!personalGalleryPanel) return;
  personalGalleryPanel.hidden = true;
  personalGalleryPanel.replaceChildren();
}

function createPersonalGalleryNotice() {
  const notice = document.createElement("div");
  notice.className = "personal-gallery-notice";
  const title = document.createElement("strong");
  title.textContent = "Local-only private media";
  const body = document.createElement("span");
  body.textContent = "Images load only from apps/dashboard/private-media/service-gallery/. Do not add ID cards, credentials, addresses, account screenshots, recovery codes, or sensitive identity files.";
  notice.append(title, body);
  return notice;
}

function createPersonalGalleryEmpty(message) {
  const empty = document.createElement("div");
  empty.className = "personal-gallery-empty";
  empty.textContent = message;
  return empty;
}

function normalizePersonalGalleryImages(data) {
  const images = Array.isArray(data?.images) ? data.images : [];
  return images
    .map((image, index) => ({
      src: typeof image?.src === "string" ? image.src.trim() : "",
      title: typeof image?.title === "string" && image.title.trim() ? image.title.trim() : `Service photo ${index + 1}`,
      category: typeof image?.category === "string" && image.category.trim() ? image.category.trim() : ""
    }))
    .filter((image) => image.src && image.src.startsWith("private-media/service-gallery/"));
}

function getArmyGalleryCategory(data) {
  const categories = Array.isArray(data?.categories) ? data.categories : [];
  const armyCategory = categories.find((category) => {
    const id = typeof category?.id === "string" ? category.id.trim().toLowerCase() : "";
    const title = typeof category?.title === "string" ? category.title.trim().toLowerCase() : "";
    return id === "army" || title === "army";
  });

  return {
    id: "army",
    title: typeof armyCategory?.title === "string" && armyCategory.title.trim() ? armyCategory.title.trim() : "Army",
    description: typeof armyCategory?.description === "string" && armyCategory.description.trim()
      ? armyCategory.description.trim()
      : "Local-only Army service photos."
  };
}

function getArmyGalleryImages(images) {
  return images.filter((image) => image.category.trim().toLowerCase() === "army");
}

function createPersonalGalleryCategoryCard(category, images) {
  const grid = document.createElement("div");
  grid.className = "personal-gallery-category-grid";

  const button = document.createElement("button");
  button.className = "personal-gallery-category-card";
  button.type = "button";
  button.setAttribute("aria-label", `Open ${category.title} gallery`);

  const label = document.createElement("span");
  label.className = "card-label";
  label.textContent = "CATEGORY";

  const title = document.createElement("strong");
  title.textContent = category.title;

  const description = document.createElement("span");
  description.textContent = category.description;

  const count = document.createElement("small");
  count.textContent = `${images.length} local photo${images.length === 1 ? "" : "s"}`;

  button.append(label, title, description, count);
  button.addEventListener("click", () => {
    personalGalleryPanel.replaceChildren(
      createPersonalGalleryNotice(),
      createPersonalGalleryBackButton(category),
      images.length
        ? renderPersonalGalleryImages(images)
        : createPersonalGalleryEmpty("No Army service photos found.")
    );
  });

  grid.append(button);
  return grid;
}

function createPersonalGalleryBackButton(category) {
  const button = document.createElement("button");
  button.className = "personal-gallery-back";
  button.type = "button";
  button.textContent = `Back to ${category.title} category`;
  button.addEventListener("click", () => {
    renderPersonalGallery();
  });
  return button;
}

function renderPersonalGalleryImages(images) {
  const grid = document.createElement("div");
  grid.className = "personal-gallery-grid";
  images.forEach((image) => {
    const card = document.createElement("article");
    card.className = "personal-gallery-card";
    const thumbnail = document.createElement("img");
    thumbnail.src = image.src;
    thumbnail.alt = image.title;
    thumbnail.loading = "lazy";
    const title = document.createElement("span");
    title.textContent = image.title;
    card.append(thumbnail, title);
    grid.append(card);
  });
  return grid;
}

async function renderPersonalGallery() {
  if (!personalGalleryPanel) return;
  personalGalleryPanel.hidden = false;
  personalGalleryPanel.replaceChildren(createPersonalGalleryNotice(), createPersonalGalleryEmpty("Loading local gallery manifest..."));

  try {
    const response = await fetch(personalGalleryManifestPath, { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Gallery manifest unavailable.");
    }
    const data = await response.json();
    const images = normalizePersonalGalleryImages(data);
    const armyCategory = getArmyGalleryCategory(data);
    const armyImages = getArmyGalleryImages(images);
    personalGalleryPanel.replaceChildren(createPersonalGalleryNotice());
    if (!images.length) {
      personalGalleryPanel.append(createPersonalGalleryEmpty("No local service photos found."));
      return;
    }
    personalGalleryPanel.append(createPersonalGalleryCategoryCard(armyCategory, armyImages));
  } catch (error) {
    personalGalleryPanel.replaceChildren(
      createPersonalGalleryNotice(),
      createPersonalGalleryEmpty("Local gallery manifest not found. Add images to private-media/service-gallery and create gallery.local.json.")
    );
  }
}

function readCommandCenterState() {
  try {
    const parsed = JSON.parse(window.sessionStorage.getItem(dashboardWorkspaceStateKey) || "{}");
    if (!parsed) return null;
    if (railDetailConfig[parsed.rail]) {
      const hasRailDetail = railDetailConfig[parsed.rail].items.some((item) => item.id === parsed.detail);
      return {
        rail: parsed.rail,
        workspace: parsed.rail,
        detail: hasRailDetail ? parsed.detail : undefined
      };
    }
    const legacyTarget = resolveRailTarget(parsed.workspace, parsed.detail);
    const hasDetail = railDetailConfig[legacyTarget.rail].items.some((item) => item.id === legacyTarget.detail);
    return {
      rail: legacyTarget.rail,
      workspace: legacyTarget.rail,
      detail: hasDetail ? legacyTarget.detail : undefined
    };
  } catch (error) {
    return null;
  }
}

function saveCommandCenterState() {
  try {
    window.sessionStorage.setItem(dashboardWorkspaceStateKey, JSON.stringify({
      rail: activeWorkspaceId,
      workspace: activeWorkspaceId,
      detail: activeDetailItemId
    }));
  } catch (error) {
    // UI-only state; ignore unavailable storage.
  }
}

function runSoftRefresh() {
  const state = readCommandCenterState() || { workspace: activeWorkspaceId, detail: activeDetailItemId };
  hideRefreshGuardMessage();
  setActiveTab(state.workspace || "work-table", state.detail);
  setYouTubeDockCollapsed(readSavedYouTubeDockCollapsed());
  syncYouTubeAudioControls();
  setYouTubeRadioPreviewNote(youtubeRadioLocalServerCommand);
  if (!youtubeRadioPlayer && !isYouTubeRadioLocalFilePreview()) {
    setYouTubeRadioState(youtubeRadioResumeMessage);
  }
}

function showRefreshGuardMessage() {
  if (!refreshGuardMessage) return;
  refreshGuardMessage.textContent = "Music is playing. Use Soft Refresh to keep audio running.";
  refreshGuardMessage.hidden = false;
  window.clearTimeout(refreshGuardMessageTimer);
  refreshGuardMessageTimer = window.setTimeout(() => {
    hideRefreshGuardMessage();
  }, 5200);
}

function hideRefreshGuardMessage() {
  if (!refreshGuardMessage) return;
  refreshGuardMessage.hidden = true;
}

function openMusicCompanion() {
  const companionUrl = new URL("AIOS_MUSIC_COMPANION.html", window.location.href).href;
  const features = "popup=yes,width=430,height=620,resizable=yes,scrollbars=yes";

  if (musicCompanionWindow && !musicCompanionWindow.closed) {
    musicCompanionWindow.focus();
    return;
  }

  musicCompanionWindow = window.open(companionUrl, "AIOS_MUSIC_COMPANION", features);
  if (musicCompanionWindow) {
    musicCompanionWindow.focus();
  }
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

function isYouTubeRadioLocalFilePreview() {
  return window.location.protocol === "file:";
}

function setYouTubeRadioPreviewNote(message) {
  if (youtubeRadioPreviewNote) youtubeRadioPreviewNote.textContent = message;
}

function setYouTubeRadioLocalFileFallback() {
  setYouTubeRadioState(youtubeRadioLocalFileFallback);
  setYouTubeRadioPreviewNote(youtubeRadioLocalServerCommand);
  setYouTubePlayButton(false);
}

function setYouTubePlayButton(isPlaying) {
  document.querySelectorAll('[data-youtube-radio-control="play"]').forEach((button) => {
    const label = isPlaying ? "Pause" : "Play";
    const readableState = button.querySelector("[data-youtube-radio-readable-state]");
    if (button.classList.contains("youtube-radio-mini-button")) {
      button.classList.toggle("is-playing", isPlaying);
      button.setAttribute("aria-label", `${label} YouTube Radio`);
      button.setAttribute("title", label);
      if (readableState) readableState.textContent = label;
    } else {
      button.textContent = label;
    }
  });
}

function setYouTubeMuteButton(isMuted) {
  youtubeRadioMuted = isMuted;
  document.querySelectorAll('[data-youtube-radio-control="mute"]').forEach((button) => {
    const label = isMuted ? "Unmute" : "Mute";
    const readableState = button.querySelector("[data-youtube-radio-readable-state]");
    if (button.classList.contains("youtube-radio-mini-button")) {
      button.classList.toggle("is-muted", isMuted);
      button.setAttribute("aria-label", `${label} YouTube Radio`);
      button.setAttribute("title", label);
      if (readableState) readableState.textContent = label;
    } else {
      button.textContent = label;
    }
  });
}

function syncYouTubeVolumeControls(value) {
  const normalized = Math.max(0, Math.min(100, Number(value) || 0));
  youtubeRadioVolumeControls.forEach((control) => {
    control.value = String(normalized);
  });
}

function syncYouTubeAudioControls() {
  if (!youtubeRadioPlayer) return;

  try {
    if (typeof youtubeRadioPlayer.getVolume === "function") {
      syncYouTubeVolumeControls(youtubeRadioPlayer.getVolume());
    }
    if (typeof youtubeRadioPlayer.isMuted === "function") {
      setYouTubeMuteButton(youtubeRadioPlayer.isMuted());
    }
  } catch (error) {
    // YouTube state can be unavailable during player startup.
  }
}

function setYouTubeDockCollapsed(isCollapsed) {
  if (!youtubeRadioDock) return;
  youtubeRadioDock.classList.toggle("is-collapsed", isCollapsed);
  const collapseButton = youtubeRadioDock.querySelector('[data-youtube-radio-control="collapse"]');
  if (collapseButton) {
    collapseButton.textContent = isCollapsed ? "+" : "−";
    collapseButton.setAttribute("aria-label", isCollapsed ? "Expand YouTube Radio" : "Collapse YouTube Radio");
  }
}

function readSavedYouTubeDockCollapsed() {
  try {
    const value = window.localStorage.getItem(youtubeDockCollapsedKey);
    if (value === "true") return true;
    if (value === "false") return false;
    return false;
  } catch (error) {
    return false;
  }
}

function saveYouTubeDockCollapsed(isCollapsed) {
  try {
    window.localStorage.setItem(youtubeDockCollapsedKey, String(isCollapsed));
  } catch (error) {
    // Visual preference only; ignore unavailable storage.
  }
}

function readSavedYouTubeRadioState() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(youtubeRadioStateKey) || "{}");
    if (!parsed || typeof parsed !== "object") return null;
    return {
      time: Math.max(0, Number(parsed.time) || 0),
      volume: Math.max(0, Math.min(100, Number(parsed.volume) || 70)),
      muted: parsed.muted === true,
      collapsed: parsed.collapsed === true,
      wasPlaying: parsed.wasPlaying === true,
      savedAt: Number(parsed.savedAt) || 0
    };
  } catch (error) {
    return null;
  }
}

function getYouTubeRadioPlayerState() {
  if (!youtubeRadioPlayer || !window.YT?.PlayerState) {
    return { isPlaying: youtubeRadioLastKnownPlaying };
  }

  try {
    const state = typeof youtubeRadioPlayer.getPlayerState === "function" ? youtubeRadioPlayer.getPlayerState() : null;
    return {
      isPlaying: state === window.YT.PlayerState.PLAYING,
      time: typeof youtubeRadioPlayer.getCurrentTime === "function" ? youtubeRadioPlayer.getCurrentTime() : 0,
      volume: typeof youtubeRadioPlayer.getVolume === "function" ? youtubeRadioPlayer.getVolume() : 70,
      muted: typeof youtubeRadioPlayer.isMuted === "function" ? youtubeRadioPlayer.isMuted() : youtubeRadioMuted
    };
  } catch (error) {
    return { isPlaying: youtubeRadioLastKnownPlaying };
  }
}

function saveYouTubeRadioState() {
  try {
    const playerState = getYouTubeRadioPlayerState();
    const collapsed = youtubeRadioDock ? youtubeRadioDock.classList.contains("is-collapsed") : false;
    window.localStorage.setItem(youtubeRadioStateKey, JSON.stringify({
      time: Math.max(0, Number(playerState.time) || 0),
      volume: Math.max(0, Math.min(100, Number(playerState.volume) || Number(youtubeRadioVolumeControls[0]?.value) || 70)),
      muted: playerState.muted === true,
      wasPlaying: playerState.isPlaying === true,
      collapsed,
      savedAt: Date.now()
    }));
  } catch (error) {
    // Safe UI/player state only; ignore unavailable storage.
  }
}

function applyYouTubeRadioRestoreState() {
  if (!youtubeRadioPlayer || youtubeRadioRestoreApplied) return;
  const saved = youtubeRadioRestoreState || readSavedYouTubeRadioState();
  if (!saved) return;

  try {
    if (typeof youtubeRadioPlayer.setVolume === "function") {
      youtubeRadioPlayer.setVolume(saved.volume);
      syncYouTubeVolumeControls(saved.volume);
    }
    if (saved.muted && typeof youtubeRadioPlayer.mute === "function") {
      youtubeRadioPlayer.mute();
      setYouTubeMuteButton(true);
    }
    if (!saved.muted && typeof youtubeRadioPlayer.unMute === "function") {
      youtubeRadioPlayer.unMute();
      setYouTubeMuteButton(false);
    }
    if (saved.time > 0 && typeof youtubeRadioPlayer.seekTo === "function") {
      youtubeRadioPlayer.seekTo(saved.time, true);
    }
    setYouTubeDockCollapsed(saved.collapsed);
    setYouTubeRadioState(youtubeRadioResumeMessage);
    youtubeRadioRestoreApplied = true;
  } catch (error) {
    setYouTubeRadioState(youtubeRadioResumeMessage);
  }
}

function loadYouTubeRadioApi() {
  if (window.YT?.Player || youtubeRadioScriptLoading) return;
  youtubeRadioScriptLoading = true;
  const script = document.createElement("script");
  script.src = "https://www.youtube.com/iframe_api";
  script.async = true;
  document.head.appendChild(script);
}

function getYouTubeRadioPlayerVars() {
  const playerVars = {
    autoplay: 0,
    playsinline: 1,
    rel: 0
  };
  // Muted autoplay is intentionally not enabled; browser policy still controls startup media.

  if (youtubeRadioEmbedMode === "playlist") {
    playerVars.list = youtubeRadioPlaylistId;
    playerVars.listType = "playlist";
  }

  return playerVars;
}

function retryYouTubeRadioSingleVideo() {
  if (!youtubeRadioPlayer || youtubeRadioSingleFallbackAttempted) return false;
  youtubeRadioSingleFallbackAttempted = true;
  youtubeRadioEmbedMode = "video";
  setYouTubeRadioState("Playlist unavailable - trying video");

  try {
    youtubeRadioPlayer.loadVideoById(youtubeRadioVideoId);
    return true;
  } catch (error) {
    return false;
  }
}

function runYouTubeRadioPlayerAction(action) {
  if (!youtubeRadioPlayer || !window.YT?.PlayerState) return;

  try {
    if (action === "play") {
      const state = youtubeRadioPlayer.getPlayerState();
      if (state === window.YT.PlayerState.PLAYING) {
        youtubeRadioPlayer.pauseVideo();
      } else {
        youtubeRadioPlayer.playVideo();
      }
    }

    if (action === "restart" && typeof youtubeRadioPlayer.seekTo === "function") {
      youtubeRadioPlayer.seekTo(0, true);
      if (typeof youtubeRadioPlayer.playVideo === "function") {
        youtubeRadioPlayer.playVideo();
      }
    }

    if (action === "next") {
      youtubeRadioPlayer.nextVideo();
    }

    if (action === "back") {
      youtubeRadioPlayer.previousVideo();
    }

    if (action === "mute") {
      const isMuted = typeof youtubeRadioPlayer.isMuted === "function" && youtubeRadioPlayer.isMuted();
      if (isMuted) {
        youtubeRadioPlayer.unMute();
        setYouTubeMuteButton(false);
      } else {
        youtubeRadioPlayer.mute();
        setYouTubeMuteButton(true);
      }
    }
    saveYouTubeRadioState();
  } catch (error) {
    setYouTubeRadioState("YouTube control unavailable.");
  }
}

window.onYouTubeIframeAPIReady = function onYouTubeIframeAPIReady() {
  if (!youtubeRadioDock || youtubeRadioPlayer) return;
  youtubeRadioEmbedMode = "playlist";
  youtubeRadioSingleFallbackAttempted = false;
  youtubeRadioPlayer = new window.YT.Player("youtubeRadioPlayer", {
    height: "200",
    width: "320",
    videoId: youtubeRadioVideoId,
    playerVars: getYouTubeRadioPlayerVars(),
    events: {
      onReady: () => {
        setYouTubeRadioState(youtubeRadioResumeMessage);
        applyYouTubeRadioRestoreState();
        syncYouTubeAudioControls();
        if (youtubeRadioShouldPlay && youtubeRadioPendingAction) {
          runYouTubeRadioPlayerAction(youtubeRadioPendingAction);
          youtubeRadioPendingAction = null;
          youtubeRadioShouldPlay = false;
        }
      },
      onError: () => {
        if (youtubeRadioEmbedMode === "playlist" && retryYouTubeRadioSingleVideo()) return;
        setYouTubeRadioState("Embed unavailable inside AI_OS — external handoff requires approval.");
        setYouTubePlayButton(false);
      },
      onStateChange: (event) => {
        if (event.data === window.YT.PlayerState.PLAYING) {
          youtubeRadioLastKnownPlaying = true;
          setYouTubeRadioState("Playing inside AI_OS");
          setYouTubePlayButton(true);
          syncYouTubeAudioControls();
          saveYouTubeRadioState();
        }
        if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
          youtubeRadioLastKnownPlaying = false;
          setYouTubeRadioState("Paused");
          setYouTubePlayButton(false);
          syncYouTubeAudioControls();
          saveYouTubeRadioState();
        }
      }
    }
  });
};

function ensureYouTubeRadioPlayer(action) {
  if (youtubeRadioPlayer) return true;
  if (isYouTubeRadioLocalFilePreview()) {
    youtubeRadioPendingAction = null;
    youtubeRadioShouldPlay = false;
    setYouTubeRadioLocalFileFallback();
    return false;
  }
  youtubeRadioPendingAction = action;
  youtubeRadioShouldPlay = true;
  setYouTubeRadioState("Loading inside AI_OS");
  setYouTubeRadioPreviewNote(youtubeRadioLocalServerCommand);
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
    const isCollapsed = !youtubeRadioDock.classList.contains("is-collapsed");
    setYouTubeDockCollapsed(isCollapsed);
    saveYouTubeDockCollapsed(isCollapsed);
    saveYouTubeRadioState();
    return;
  }

  if (action === "open") {
    setYouTubeRadioState("External handoff requires approval.");
    setYouTubeRadioPreviewNote(youtubeRadioLocalServerCommand);
    return;
  }

  const hasPlayer = ensureYouTubeRadioPlayer(action);
  if (!hasPlayer) return;

  runYouTubeRadioPlayerAction(action);
}

function handleYouTubeRadioVolume(value) {
  const volume = Math.max(0, Math.min(100, Number(value) || 0));
  syncYouTubeVolumeControls(volume);

  if (!youtubeRadioPlayer) {
    saveYouTubeRadioState();
    if (isYouTubeRadioLocalFilePreview()) {
      setYouTubeRadioLocalFileFallback();
    }
    return;
  }

  try {
    if (typeof youtubeRadioPlayer.setVolume === "function") {
      youtubeRadioPlayer.setVolume(volume);
    }
    if (volume > 0 && typeof youtubeRadioPlayer.isMuted === "function" && youtubeRadioPlayer.isMuted()) {
      youtubeRadioPlayer.unMute();
      setYouTubeMuteButton(false);
    }
    saveYouTubeRadioState();
  } catch (error) {
    setYouTubeRadioState("Volume control unavailable.");
  }
}

function isTypingTarget(target) {
  if (!target) return false;
  const element = target.nodeType === Node.ELEMENT_NODE ? target : target.parentElement;
  if (!element) return false;
  return Boolean(element.closest("input, textarea, select, [contenteditable='true'], [contenteditable='']"));
}

function getDashboardMusicVolumeDelta(delta) {
  let currentVolume = Number(youtubeRadioVolumeControls[0]?.value) || 70;
  if (youtubeRadioPlayer && typeof youtubeRadioPlayer.getVolume === "function") {
    try {
      currentVolume = Number(youtubeRadioPlayer.getVolume()) || currentVolume;
    } catch (error) {
      // Use the current slider value when the YouTube player is not ready.
    }
  }
  return Math.max(0, Math.min(100, currentVolume + delta));
}

function sendMusicCompanionCommand(command, value) {
  if (!musicCompanionWindow || musicCompanionWindow.closed) return false;
  try {
    musicCompanionWindow.postMessage({
      source: "AI_OS_DASHBOARD",
      type: "music-command",
      command,
      value
    }, window.location.origin);
    return true;
  } catch (error) {
    return false;
  }
}

function runDashboardMusicShortcut(command, value) {
  if (command === "volume") {
    const volume = Math.max(0, Math.min(100, Number(value) || 0));
    if (sendMusicCompanionCommand("volume", volume)) return;
    handleYouTubeRadioVolume(volume);
    return;
  }

  const companionCommandMap = {
    play: "playPause",
    back: "previous",
    next: "next",
    restart: "restart",
    mute: "mute"
  };

  if (sendMusicCompanionCommand(companionCommandMap[command] || command)) return;
  handleYouTubeRadioControl(command);
}

function handleDashboardMusicKeyboardShortcut(event) {
  if (isTypingTarget(event.target)) return false;
  if (event.ctrlKey || event.metaKey || event.altKey) return false;

  const key = event.key;
  const lowerKey = key.toLowerCase();

  if (key === " " || key === "Spacebar") {
    event.preventDefault();
    runDashboardMusicShortcut("play");
    return true;
  }
  if (key === "ArrowLeft") {
    event.preventDefault();
    runDashboardMusicShortcut("back");
    return true;
  }
  if (key === "ArrowRight") {
    event.preventDefault();
    runDashboardMusicShortcut("next");
    return true;
  }
  if (lowerKey === "r") {
    event.preventDefault();
    runDashboardMusicShortcut("restart");
    return true;
  }
  if (lowerKey === "m") {
    event.preventDefault();
    runDashboardMusicShortcut("mute");
    return true;
  }
  if (key === "ArrowUp") {
    event.preventDefault();
    runDashboardMusicShortcut("volume", getDashboardMusicVolumeDelta(5));
    return true;
  }
  if (key === "ArrowDown") {
    event.preventDefault();
    runDashboardMusicShortcut("volume", getDashboardMusicVolumeDelta(-5));
    return true;
  }

  return false;
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

function readSavedPersonalRailClosed() {
  try {
    const value = window.sessionStorage.getItem(personalRailStateKey);
    if (value === "true") return true;
    if (value === "false") return false;
    return null;
  } catch (error) {
    return null;
  }
}

function savePersonalRailClosed(isClosed) {
  try {
    window.sessionStorage.setItem(personalRailStateKey, String(isClosed));
  } catch (error) {
    // The rail still works without persisted UI state.
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
  const workOpenerLabel = "Work Tab";
  const workOpenerAria = expanded ? "Toggle Work Tab" : "Open Work Tab";
  sidebarToggle.setAttribute("aria-expanded", String(expanded));
  sidebarToggle.setAttribute("aria-label", expanded ? "Hide Work Tab" : "Open Work Tab");
  sidebarToggle.textContent = expanded ? "Hide Work" : "Work Tab";
  drawerReopen.setAttribute("aria-expanded", String(expanded));
  drawerReopen.setAttribute("aria-label", workOpenerAria);
  const drawerReopenLabel = drawerReopen.querySelector("span");
  if (drawerReopenLabel) {
    drawerReopenLabel.textContent = workOpenerLabel;
  } else {
    drawerReopen.textContent = workOpenerLabel;
  }
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
    document.body.classList.remove("personal-rail-open");
    document.body.classList.add("personal-rail-collapsed");
  } else {
    document.body.classList.remove("sidebar-collapsed");
  }
  saveDrawerClosed(false);
  syncSidebarState();
  syncPersonalRailState();
}

function closeMobileSidebar() {
  closeSidebar();
}

function toggleBuildRail() {
  if (mobileSidebarQuery.matches) {
    const shouldOpen = !document.body.classList.contains("sidebar-open");
    document.body.classList.toggle("sidebar-open", shouldOpen);
    document.body.classList.toggle("sidebar-collapsed", !shouldOpen);
    document.body.classList.remove("personal-rail-open");
    document.body.classList.add("personal-rail-collapsed");
    saveDrawerClosed(!shouldOpen);
  } else {
    const shouldCollapse = !document.body.classList.contains("sidebar-collapsed");
    document.body.classList.toggle("sidebar-collapsed", shouldCollapse);
    saveDrawerClosed(shouldCollapse);
  }
  syncSidebarState();
  syncPersonalRailState();
}

function applySavedPersonalRailState() {
  const savedClosed = readSavedPersonalRailClosed();
  document.body.classList.remove("personal-rail-open");
  document.body.classList.toggle("personal-rail-collapsed", savedClosed === true || mobileSidebarQuery.matches);
}

function syncPersonalRailState() {
  const isMobile = mobileSidebarQuery.matches;
  const isOpen = document.body.classList.contains("personal-rail-open");
  const isCollapsed = document.body.classList.contains("personal-rail-collapsed");
  const expanded = isMobile ? isOpen : !isCollapsed;
  personalRailToggles.forEach((button) => {
    const scope = button.dataset.railToggleScope || "";
    const isInternalToggle = scope === "personal-internal";
    button.setAttribute("aria-expanded", String(expanded));
    const personalLabel = isInternalToggle ? "Hide Personal" : "Personal Tab";
    button.setAttribute("aria-label", isInternalToggle ? "Hide Personal Tab" : (expanded ? "Toggle Personal Tab" : "Open Personal Tab"));
    const textTarget = button.querySelector("span");
    if (textTarget) {
      textTarget.textContent = personalLabel;
    } else {
      button.textContent = personalLabel;
    }
  });
}

function togglePersonalRail() {
  if (mobileSidebarQuery.matches) {
    const shouldOpen = !document.body.classList.contains("personal-rail-open");
    document.body.classList.remove("sidebar-open");
    document.body.classList.toggle("personal-rail-open", shouldOpen);
    document.body.classList.toggle("personal-rail-collapsed", !shouldOpen);
    savePersonalRailClosed(!shouldOpen);
  } else {
    const shouldCollapse = !document.body.classList.contains("personal-rail-collapsed");
    document.body.classList.toggle("personal-rail-collapsed", shouldCollapse);
    savePersonalRailClosed(shouldCollapse);
  }
  syncSidebarState();
  syncPersonalRailState();
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.tab;
    setActiveTab(target);
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
    if (action === "soft-refresh") {
      runSoftRefresh();
      return;
    }
    if (action === "open-music-companion") {
      openMusicCompanion();
      return;
    }
    if (action === "toggle-personal-rail") {
      togglePersonalRail();
      return;
    }
    if (item.dataset.tab) {
      actionButtons.forEach((target) => {
        if (target.dataset.tab) {
          target.classList.toggle("active", target === item);
        }
      });
      setActiveTab(item.dataset.tab);
      return;
    }
    if (action === "send-message") {
      sendMockAssistantMessage();
      return;
    }
    if (action === "generate-context-packet") {
      generateContextPacket();
      return;
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

assistantModeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setAssistantMode(button.dataset.assistantMode);
  });
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

youtubeRadioVolumeControls.forEach((control) => {
  control.addEventListener("input", () => {
    handleYouTubeRadioVolume(control.value);
  });
});

sidebarToggle.addEventListener("click", closeSidebar);
drawerReopen.addEventListener("click", () => {
  if (mobileSidebarQuery.matches) {
    toggleBuildRail();
    return;
  }
  openSidebar();
});
drawerBackdrop.addEventListener("click", closeMobileSidebar);
mobileSidebarQuery.addEventListener("change", () => {
  applySavedDrawerState();
  applySavedPersonalRailState();
  syncSidebarState();
  syncPersonalRailState();
});

document.addEventListener("keydown", (event) => {
  const isKeyboardRefresh = event.key === "F5" || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "r");
  if (isKeyboardRefresh && youtubeRadioLastKnownPlaying) {
    event.preventDefault();
    showRefreshGuardMessage();
    saveYouTubeRadioState();
    return;
  }

  if (handleDashboardMusicKeyboardShortcut(event)) return;

  if (event.key === "Escape" && mobileSidebarQuery.matches) {
    closeMobileSidebar();
  }
});

applyDashboardTheme(readSavedDashboardTheme());
const savedCommandCenterState = readCommandCenterState();
if (savedCommandCenterState) {
  setActiveTab(savedCommandCenterState.rail || savedCommandCenterState.workspace, savedCommandCenterState.detail);
} else {
  renderRailSelection("build", "start-here");
}
youtubeRadioRestoreState = readSavedYouTubeRadioState();
setYouTubeDockCollapsed(youtubeRadioRestoreState?.collapsed ?? readSavedYouTubeDockCollapsed());
if (isYouTubeRadioLocalFilePreview()) {
  setYouTubeRadioLocalFileFallback();
} else {
  setYouTubeRadioPreviewNote(youtubeRadioLocalServerCommand);
  if (youtubeRadioRestoreState?.time > 0) {
    setYouTubeRadioState(youtubeRadioResumeMessage);
    syncYouTubeVolumeControls(youtubeRadioRestoreState.volume);
    setYouTubeMuteButton(youtubeRadioRestoreState.muted);
  }
}
applySavedDrawerState();
applySavedPersonalRailState();
syncSidebarState();
syncPersonalRailState();
setAssistantMode(activeAssistantMode);
loadStatusOverview();
loadToolRegistryStatus();
loadWorkTableAiInsights();

window.setInterval(() => {
  if (youtubeRadioLastKnownPlaying) {
    saveYouTubeRadioState();
  }
}, 5000);

window.addEventListener("pagehide", () => {
  saveCommandCenterState();
  saveYouTubeRadioState();
});

window.addEventListener("beforeunload", (event) => {
  saveCommandCenterState();
  saveYouTubeRadioState();
  if (youtubeRadioLastKnownPlaying) {
    event.preventDefault();
    event.returnValue = "";
  }
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
