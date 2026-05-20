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
const welcomeStartScreen = document.querySelector("[data-welcome-start]");
const welcomeActionButtons = document.querySelectorAll("[data-welcome-action]");
const detailKicker = document.querySelector("[data-detail-kicker]");
const detailTitle = document.querySelector("[data-detail-title]");
const detailSubtitle = document.querySelector("[data-detail-subtitle]");
const detailStatus = document.querySelector("[data-detail-status]");
const detailNote = document.querySelector("[data-detail-note]");
const detailList = document.querySelector("[data-detail-list]");
const tradingLabNextActionCard = document.querySelector("[data-trading-lab-next-action]");
const devopsControlWindowPanel = document.querySelector("[data-devops-control-window]");
const projectHubPanel = document.querySelector("[data-project-hub]");
const personalGalleryPanel = document.querySelector("[data-personal-gallery]");
const personalAppsPanel = document.querySelector("[data-personal-apps]");
const refreshGuardMessage = document.querySelector("[data-refresh-guard-message]");
const sidebarToggle = document.querySelector(".command-sidebar .sidebar-toggle");
const drawerReopen = document.querySelector(".drawer-reopen");
const drawerBackdrop = document.querySelector(".drawer-backdrop");
const personalRailToggles = document.querySelectorAll("[data-action='toggle-personal-rail']");
const mobileSidebarQuery = window.matchMedia("(max-width: 1120px)");
const commandMain = document.querySelector(".command-main");
const dashboardShell = document.querySelector(".dashboard-shell");
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
const _devopsControlWindowFixturePath = "mock-data/aios-devops-control-window-v1.example.json";
const _workIntelligenceQueueFixturePath = "mock-data/work-intelligence-queue-v1.example.json";
const orchestratorWindowFixturePath = "mock-data/aios-orchestrator-window-v1.example.json";
const workerRegistryFixturePath = "mock-data/aios-worker-registry-v1.example.json";
const workerQueueFixturePath = "mock-data/aios-worker-queue-v1.example.json";
const validatorStateFixturePath = "mock-data/aios-validator-state-v1.example.json";
const commandCenterStateFixturePath = "mock-data/aios-command-center-state-v1.example.json";
const commandCenterApprovalInboxFixturePath = "mock-data/aios-approval-inbox-v1.example.json";
const commandCenterMergeQueueFixturePath = "mock-data/aios-merge-readiness-queue-v1.example.json";
const commandCenterConflictCenterFixturePath = "mock-data/aios-conflict-center-v1.example.json";
const commandCenterOperatorGuidanceFixturePath = "mock-data/aios-operator-guidance-v1.example.json";
const commandCenterWorkerAgeFixturePath = "mock-data/aios-worker-age-tracking-v1.example.json";
const _tradingLabNextActionFixturePath = "mock-data/trading-lab-next-action.example.json";
const tradingLabWorkspaceFixturePath = "mock-data/trading-lab-workspace.example.json";
const tradingLabWorkstationFixturePath = "mock-data/trading-lab-workstation.example.json";
const paperTradingBotStatusFixturePath = "mock-data/paper-trading-bot-status.example.json";
const phase23PaperSignalNormalizationFixturePath = "mock-data/phase-23-paper-signal-normalization.example.json";
const phase25LatencyMeasurementCoreFixturePath = "mock-data/phase-25-latency-measurement-core.example.json";
const phase28TvTpPaperHandoffFixturePath = "mock-data/phase-28-tv-tp-paper-handoff.example.json";
const tradingLabPaperRunnerFixturePath = "mock-data/trading-lab-paper-runner.example.json";
const aiosOrchestrationControlRoomFixturePath = "mock-data/aios-orchestration-control-room.example.json";
const paperBotCoreFixturePath = "mock-data/paper-bot-core.example.json";
const tradingLabWindowSystemFixturePath = "mock-data/trading-lab-window-system.example.json";
const aiosOperatorWorkbenchFixturePath = "mock-data/aios-operator-workbench.example.json";
const aiosConfidenceTimelineFixturePath = "mock-data/aios-confidence-timeline.example.json";
const aiosPortfolioHeatFixturePath = "mock-data/aios-portfolio-heat.example.json";
const aiosMacroOverlayFixturePath = "mock-data/aios-macro-overlay.example.json";
const aiosChaosAlertsFixturePath = "mock-data/aios-chaos-alerts.example.json";
const aiosReplayWorkbenchFixturePath = "mock-data/aios-replay-workbench.example.json";
const aiosFreezeTimelineFixturePath = "mock-data/aios-freeze-timeline.example.json";
const aiosEdgeDecayVisibilityFixturePath = "mock-data/aios-edge-decay-visibility.example.json";
const aiosSurvivabilityTimelineFixturePath = "mock-data/aios-survivability-timeline.example.json";
const aiosReplayScenariosFixturePath = "mock-data/aios-replay-scenarios.example.json";
const aiosRiskEscalationFixturePath = "mock-data/aios-risk-escalation.example.json";
const aiosNextSafeActionFlowFixturePath = "mock-data/aios-next-safe-action-flow.example.json";
const aiosOperatorGuidanceFixturePath = "mock-data/aios-operator-guidance.example.json";
const aiosSurvivabilityGuidanceFixturePath = "mock-data/aios-survivability-guidance.example.json";
const aiosConfidenceGuidanceFixturePath = "mock-data/aios-confidence-guidance.example.json";
const aiosRiskReductionGuidanceFixturePath = "mock-data/aios-risk-reduction-guidance.example.json";
const aiosNextSafeActionGuidanceFixturePath = "mock-data/aios-next-safe-action-guidance.example.json";
const lifetimeTelemetryFixturePath = "mock-data/lifetime-telemetry-fixture.example.json";
const personalGalleryManifestPath = "private-media/service-gallery/gallery.local.json";
const youtubeRadioTracks = [
  { videoId: "VFzsSbdS7Sk", playlistId: "RDVFzsSbdS7Sk" },
  { videoId: "g5VSkAHGgF8", playlistId: "RDAMVMLwd7WQ8L5dQ" },
  { videoId: "nZpdxwnQmjI", playlistId: "RDAMVMLwd7WQ8L5dQ", title: "97Kickstvr - Waiting For You" },
  { videoId: "UaB9JBzgPPA", playlistId: "RDAMVMLwd7WQ8L5dQ", title: "Last Memory" }
];
const youtubeRadioDefaultTrack = youtubeRadioTracks[0];
const youtubeRadioVideoId = youtubeRadioDefaultTrack.videoId;
const youtubeRadioPlaylistId = youtubeRadioDefaultTrack.playlistId;
const youtubeRadioLocalFileFallback = "Embedded playback unavailable in local file preview. Use local server preview.";
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
let mobileRailScrollLockY = 0;
let mobileRailScrollLockActive = false;
let mobileRailLastTouchY = null;
let mobileRailTouchStartX = null;
let mobileRailTouchStartY = null;

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

const _workspaceDetailConfig = {
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
    title: "Trading Lab",
    summary: "Paper-only workspace for signal intake, latency, regime, risk gate, paper results, scorecard, validator status, and next action.",
    overview: "Review the Trading Lab flow. This workspace uses mock data only and cannot place trades.",
    items: [
      detailItem("trading-bot", "Trading Lab Workspace", "MOCK ONLY", "A paper-only command workspace for signal review, latency notes, regime tags, risk gate status, paper result, scorecard, validator status, and the next safe action.", "MOCK ONLY. PAPER ONLY. Live Execution: BLOCKED. Broker: BLOCKED.", ["Review mock signal intake.", "Check risk gate stays blocked.", "Use Next Action for the safest follow-up."]),
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
    summary: "Launch-only planning for social accounts with connectors locked and no credentials stored.",
    overview: "Choose a social item from the tab. This workspace does not store credentials or access keys.",
    items: [
      detailItem("facebook", "Facebook", "ACCOUNT", "Launch-only planning card for Facebook account access.", "No credentials stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("instagram", "Instagram", "ACCOUNT", "Launch-only planning card for Instagram account access.", "No credentials stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("x", "X", "ACCOUNT", "Launch-only planning card for X account access.", "No credentials stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("youtube", "YouTube", "ACCOUNT", "Launch-only planning card for YouTube account access.", "No credentials stored. OAuth/API setup required later.", ["Connector locked.", "No credential capture.", "Setup later."]),
      detailItem("social-connector-status", "Connector Status Locked", "LOCKED", "Show social connectors as locked until a future approved secure OAuth setup.", "No real OAuth or social API connection is active.", ["OAuth later.", "API calls blocked.", "Tokens not stored."]),
      detailItem("social-security-notes", "Security Notes", "SECURITY", "Keep account-safety notes and credential boundaries visible.", "Credentials and recovery codes must stay out of dashboard files and localStorage.", ["No credentials.", "No access keys.", "No recovery codes."])
    ]
  },
  "onedrive-vault": {
    title: "OneDrive Vault",
    summary: "Important file planning with access locked and no OneDrive credential storage.",
    overview: "Choose a file planning item from the tab. This workspace does not connect to OneDrive.",
    items: [
      detailItem("important-documents", "Important Docs", "DOCUMENTS", "Plan which important documents need review, organization, and protection.", "No file sync or cloud connection is active.", ["List document groups.", "Mark protected items.", "Plan review order."]),
      detailItem("aios-project-files", "AI_OS Project Files", "AI_OS", "Organize AI_OS project docs and work packets by approved paths.", "No file writer runs from this panel.", ["Project docs.", "Work packets.", "Source logs."]),
      detailItem("trading-files", "Trading Files", "TRADING", "Separate trading planning files from execution or broker files.", "No broker files or credentials are touched.", ["Planning only.", "Execution separated.", "Risk docs later."]),
      detailItem("backups", "Backups", "BACKUPS", "Plan backup categories and checkpoint timing.", "No backup writer is active.", ["Backup categories.", "Checkpoint timing.", "Restore notes."]),
      detailItem("onedrive-access-status", "Access Status Locked", "LOCKED", "Show OneDrive/file access as locked.", "No OneDrive credentials or file access are stored.", ["Access locked.", "No access keys.", "No sync."]),
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
      detailItem("future-connectors", "Future Connectors", "CONNECTORS", "Placeholder for approved connector design later.", "Credentials and provider APIs remain blocked.", ["Design later.", "No access keys.", "Approval required."])
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
      detailItem("secret-rules", "Secret Rules", "SECRETS", "Credentials, API keys, broker keys, and recovery codes must not be stored.", "Secrets stay out of dashboard files, localStorage, and mock data.", ["No credentials.", "No access keys.", "No recovery codes."]),
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
    title: "Work",
    summary: "Productive work, DevOps, app building, projects, reports, safety, and approval-safe build lanes.",
    overview: "Choose a Work item to open one focused project or DevOps detail panel.",
    items: [
      detailItem("start-here", "Start Here", "GUIDE", "Begin with a simple Workspace overview: pick an item, review the purpose, and keep APPLY blocked until approved.", "Static guide only. No backend or execution logic runs here.", ["Choose one item.", "Review purpose and locks.", "Use Soft Refresh for dashboard-only updates."]),
      detailItem("projects", "Projects", "PROJECTS", "Open active project folders for AI_OS, Trading Bot, App Builder, Web Dev, and future projects.", "Projects are static folders with mock telemetry, reports, validation, files, risks, and next actions.", ["Open a project folder.", "Review project telemetry.", "Keep execution locked."]),
      detailItem("work-table", "Work Table", "PROJECT", "Start or continue a guided project packet with brief, prompt stack, build instructions, tool output, approval gate, and validation queue.", "File edits remain blocked until explicit APPLY approval.", ["Define scope.", "Confirm allowed files.", "List validation steps."]),
      detailItem("devops-control-window", "Command Center", "DISPLAY", "Visible AI_OS Command Center for workers, queue assignments, approvals, merge readiness, conflicts, stale evidence, and next safe actions.", "Display state only. No APPLY, shell execution, worker launch, commit, merge, or push.", ["Review active workers.", "Check approvals and conflicts.", "Use the Next Safe Action before any approval."]),
      detailItem("trading-bot", "Trading Bot", "MOCK LAB", "Mock-only Trading Lab card for strategy, signal, regime, risk, journal, and metrics planning.", "No broker, OANDA, API keys, or live orders.", ["Review one strategy.", "Score a mock signal.", "Keep execution blocked."]),
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
    title: "Gallery",
    summary: "Social accounts, documents, apps, data, backups, and locked connector planning.",
    overview: "Choose a Gallery item to open one focused Social, Vault, or data detail panel.",
    items: [
      detailItem("personal-apps", "Apps", "APPS", "Open connector-locked social, OneDrive, calendar, and notes planning cards.", "No external app login, API, OAuth, file sync, or persistence is enabled.", ["Open app cards.", "No credentials stored.", "Connectors locked."]),
      detailItem("important-documents", "Important Docs", "DOCUMENTS", "Plan important document groups, review priority, and protected-file boundaries.", "No file access or cloud sync runs from this dashboard.", ["List document groups.", "Mark protected items.", "Plan review order."]),
      detailItem("personal-gallery", "Gallery", "LOCAL MEDIA", "Gallery / Service Photos. Local-only private media area for service photos and approved local images.", "Place images in apps/dashboard/private-media/service-gallery/. Do not add ID cards, credentials, documents, addresses, account screenshots, recovery codes, or sensitive identity files.", ["Local-only media.", "Manifest later: private-media/service-gallery/gallery.local.json.", "Sensitive images require REDACT REQUIRED."]),
      detailItem("backups", "Backups", "BACKUPS", "Plan backup categories, checkpoint timing, and restore notes for important work.", "No backup writer or file mover is active.", ["Backup categories.", "Checkpoint timing.", "Restore notes."]),
      detailItem("account-security", "Account Security", "SECURITY", "Keep account safety boundaries visible for social, OneDrive, and apps.", "Credentials, recovery codes, and private keys must stay out of dashboard files and localStorage.", ["No credentials.", "No access keys.", "No recovery codes."]),
      detailItem("connector-status-locked", "Connector Status Locked", "LOCKED", "Show all Gallery connectors as locked until a future approved secure setup.", "No OAuth, API calls, credential storage, or real account connection is active.", ["OAuth later.", "API calls blocked.", "Credentials not stored."])
    ]
  }
};

const personalAppsItems = [
  detailItem("facebook", "Facebook", "ACCOUNT", "Facebook account planning card for future secure launch or connector design.", "No credentials stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("instagram", "Instagram", "ACCOUNT", "Instagram account planning card for future secure launch or connector design.", "No credentials stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("x", "X", "ACCOUNT", "X account planning card for future secure launch or connector design.", "No credentials stored. OAuth/API setup required later.", ["No credential capture.", "Connector locked.", "Setup later."]),
  detailItem("youtube", "YouTube", "ACCOUNT", "YouTube account planning and music workspace boundary notes.", "No YouTube account credentials are stored.", ["No credential capture.", "Music controls preserved.", "Connector locked."]),
  detailItem("onedrive-vault", "OneDrive Vault", "FILES", "OneDrive file planning and future approved Microsoft Graph/File Picker setup.", "No OneDrive credentials, Microsoft Graph access key, or file sync is active.", ["Plan file groups.", "Keep access locked.", "Graph/File Picker later."]),
  detailItem("calendar", "Calendar", "CALENDAR", "Static calendar planning for review windows, checkpoints, and reminders.", "No Google, Microsoft, Outlook, or notification provider is connected.", ["Plan dates.", "Review checkpoints.", "Provider locked."]),
  detailItem("notes", "Notes", "NOTES", "Static notes planning for reminders, project context, and future instruction packets.", "No note writer or persistence is active.", ["Draft notes.", "Keep secrets out.", "Writer locked."])
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
    assistant: "Work Table: static Workspace for project briefs, prompt stacks, build instructions, tool output, approval gates, and validation queues.",
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
    console: "Ai_Os> Trading Bot workspace\nBroker connector: LOCKED\nLive trading: BLOCKED\nSecrets/API keys: NOT STORED"
  },
  "social-vault": {
    assistant: "Social Vault: launch-only planning cards for Facebook, Instagram, X, and YouTube. Connectors are locked and no credentials are stored.",
    console: "Ai_Os> Social Vault workspace\nAccount credentials: NOT STORED\nOAuth/API setup: REQUIRED LATER\nConnectors: LOCKED"
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

function _renderWorkspaceRail(workspaceId, selectedItemId) {
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

  renderDetailPanel(rail, selectedItem);
}

function setRailOwnership(railId) {
  if (railId === "personal") {
    document.body.classList.add("rail-owner-personal");
    document.body.classList.remove("rail-owner-build");
    document.body.classList.remove("sidebar-open");
    document.body.classList.add("sidebar-collapsed");
    return;
  }

  document.body.classList.add("rail-owner-build");
  document.body.classList.remove("rail-owner-personal");
  document.body.classList.remove("personal-rail-open");
  document.body.classList.add("personal-rail-collapsed");
}

function closeRailsAfterRouteSelection() {
  document.body.classList.remove("sidebar-open");
  document.body.classList.remove("personal-rail-open");
  document.body.classList.add("sidebar-collapsed");
  document.body.classList.add("personal-rail-collapsed");
  syncSidebarState();
  syncPersonalRailState();
  syncMobileRailScrollLock();
}

function routeWorkspaceModule(railId, item) {
  if (!item) return;
  setRailOwnership(railId);
  renderRailSelection(railId, item.id);
  clearFocusedStartView();
  focusMainWorkspace();
  closeRailsAfterRouteSelection();
  saveCommandCenterState();
}

function showWelcomeStart() {
  if (!welcomeStartScreen) return;
  clearFocusedStartView();
  welcomeStartScreen.hidden = false;
  document.body.classList.add("welcome-start-active");
  try {
    window.sessionStorage.removeItem(dashboardWorkspaceStateKey);
  } catch {
    // UI-only state; ignore unavailable storage.
  }
}

function hideWelcomeStart() {
  if (!welcomeStartScreen) return;
  welcomeStartScreen.hidden = true;
  document.body.classList.remove("welcome-start-active");
}

function isWelcomeStartVisible() {
  return Boolean(welcomeStartScreen && !welcomeStartScreen.hidden);
}

function setFocusedStartView(route = "") {
  const isFocused = Boolean(route);
  document.body.classList.remove("focused-route-start-project", "focused-route-archives", "focused-route-trading-lab");
  document.body.classList.toggle("focused-start-view-active", isFocused);
  if (isFocused) {
    document.body.classList.add(`focused-route-${route}`);
    document.body.dataset.focusedStartRoute = route;
  } else {
    delete document.body.dataset.focusedStartRoute;
  }
}

function clearFocusedStartView() {
  document.body.classList.remove("focused-start-view-active");
  document.body.classList.remove("focused-route-start-project", "focused-route-archives", "focused-route-trading-lab");
  delete document.body.dataset.focusedStartRoute;
}

function routeWelcomeAction(action) {
  const routeMap = {
    "start-here": { rail: "build", detail: "start-here", focusedRoute: "" },
    "start-project": { rail: "build", detail: "work-table", focusedRoute: "start-project" },
    "view-archives": { rail: "build", detail: "projects", focusedRoute: "archives" },
    "trading-lab": { rail: "build", detail: "trading-bot", focusedRoute: "trading-lab" }
  };
  const route = routeMap[action];
  if (!route) return;
  if (action === "start-here") {
    renderRailSelection(route.rail, route.detail);
    closeRailsAfterRouteSelection();
    showWelcomeStart();
    focusMainWorkspace();
    return;
  }
  routeWorkspaceModule(route.rail, findRailItem(route.rail, route.detail));
  hideWelcomeStart();
  setFocusedStartView(route.focusedRoute);
  focusMainWorkspace();
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
    const icon = document.createElement("span");
    icon.className = "rail-button-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = item.title.trim().slice(0, 1) || "?";
    const label = document.createElement("span");
    label.className = "rail-button-label";
    label.textContent = item.title;
    button.append(icon, label);
    if (item.id === selectedItemId) button.classList.add("active");
    button.addEventListener("click", () => {
      hideWelcomeStart();
      clearFocusedStartView();
      routeWorkspaceModule(railId, item);
      if (mobileSidebarQuery.matches) {
        closeActiveMobileRailAfterSelection();
      }
    });
    container.append(button);
  });
}

function renderDetailPanel(workspace, item) {
  hideTradingLabNextActionCard();
  hideDevOpsControlWindow();
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
  if (item.id === "devops-control-window") {
    renderDevOpsControlWindow();
  }
  if (item.id === "personal-apps") {
    renderPersonalApps();
  }
  if (item.id === "trading-bot") {
    renderTradingLabNextActionCard();
  }
}

function hideDevOpsControlWindow() {
  if (!devopsControlWindowPanel) return;
  devopsControlWindowPanel.hidden = true;
  devopsControlWindowPanel.replaceChildren();
}

function createDevOpsTextElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  element.textContent = text ?? "UNKNOWN";
  return element;
}

function createDevOpsStatusPill(value = "UNKNOWN") {
  const pill = document.createElement("span");
  const normalized = String(value).toLowerCase();
  pill.className = "devops-status-pill";
  if (normalized.includes("blocked") || normalized.includes("fail")) {
    pill.classList.add("is-blocked");
  } else if (normalized.includes("ready") || normalized.includes("pass")) {
    pill.classList.add("is-ready");
  } else if (normalized.includes("review") || normalized.includes("pending")) {
    pill.classList.add("is-review");
  }
  pill.textContent = value || "UNKNOWN";
  return pill;
}

function createDevOpsMetric(label, value) {
  const metric = document.createElement("div");
  metric.className = "devops-metric";
  metric.append(
    createDevOpsTextElement("span", "", label),
    createDevOpsTextElement("strong", "", value ?? "UNKNOWN")
  );
  return metric;
}

function createDevOpsField(label, value) {
  const field = document.createElement("div");
  field.className = "devops-field";
  field.append(
    createDevOpsTextElement("span", "", label),
    createDevOpsTextElement("strong", "", value || "UNKNOWN")
  );
  return field;
}

function createDevOpsPanel(title, children = []) {
  const panel = document.createElement("section");
  panel.className = "devops-card";
  const heading = document.createElement("div");
  heading.className = "devops-card-head";
  heading.append(createDevOpsTextElement("strong", "", title));
  panel.append(heading, ...children.filter(Boolean));
  return panel;
}

function createDevOpsDetailsPanel(title, children = []) {
  const details = document.createElement("details");
  details.className = "devops-card command-center-details";
  const summary = document.createElement("summary");
  summary.append(createDevOpsTextElement("strong", "", title));
  details.append(summary, ...children.filter(Boolean));
  return details;
}

function renderDevOpsQueue(queueItems = []) {
  const queue = document.createElement("div");
  queue.className = "devops-queue-list";
  const header = document.createElement("div");
  header.className = "devops-queue-row devops-queue-row-head";
  header.append(
    createDevOpsTextElement("span", "devops-queue-rank", "Rank"),
    createDevOpsTextElement("strong", "devops-queue-title", "Workload"),
    createDevOpsTextElement("span", "devops-queue-label", "Priority"),
    createDevOpsTextElement("span", "devops-queue-label", "Status"),
    createDevOpsTextElement("span", "devops-queue-lane", "Lane"),
    createDevOpsTextElement("p", "devops-queue-action", "Recommended action")
  );
  queue.append(header);
  queueItems.slice(0, 6).forEach((item) => {
    const row = document.createElement("article");
    row.className = "devops-queue-row";
    row.append(
      createDevOpsTextElement("span", "devops-queue-rank", `#${item.queue_rank ?? "?"}`),
      createDevOpsTextElement("strong", "devops-queue-title", item.title || "UNKNOWN"),
      createDevOpsStatusPill(item.priority || "UNKNOWN"),
      createDevOpsStatusPill(item.status || "UNKNOWN"),
      createDevOpsTextElement("span", "devops-queue-lane", item.suggested_worker_lane || "UNKNOWN"),
      createDevOpsTextElement("p", "devops-queue-action", item.recommended_action || "UNKNOWN")
    );
    queue.append(row);
  });
  if (queue.childElementCount === 1) {
    header.remove();
    queue.append(createDevOpsTextElement("p", "devops-muted", "No queue evidence available."));
  }
  return queue;
}

function renderDevOpsValidation(validation = {}) {
  const grid = document.createElement("div");
  grid.className = "devops-validation-grid";
  [
    ["Work Intelligence", validation.work_intelligence_validator],
    ["Parallel Workers", validation.parallel_worker_validator],
    ["git diff --check", validation.git_diff_check],
    ["git status", validation.git_status]
  ].forEach(([label, item]) => {
    const card = document.createElement("div");
    card.className = "devops-validation-item";
    card.append(
      createDevOpsTextElement("span", "", label),
      createDevOpsStatusPill(item?.state || "UNKNOWN"),
      createDevOpsTextElement("small", "", item?.detail || "UNKNOWN")
    );
    grid.append(card);
  });
  return grid;
}

function renderDevOpsCommitPackage(commitPackage = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = "devops-commit-package";
  const note = createDevOpsTextElement("p", "devops-muted", commitPackage.note || "Display-only exact-file staging preview. No execution buttons.");
  const commandList = document.createElement("pre");
  commandList.className = "devops-command-preview";
  const commands = Array.isArray(commitPackage.git_add_commands) ? commitPackage.git_add_commands : [];
  commandList.textContent = commands.length ? commands.join("\n") : "No git add commands available.";
  wrapper.append(note, commandList);
  return wrapper;
}

function renderDevOpsMorningWorkflow(morning = {}) {
  const list = document.createElement("div");
  list.className = "devops-morning-list";
  (morning.checks || []).forEach((check) => {
    const item = document.createElement("div");
    item.className = "devops-morning-item";
    item.append(
      createDevOpsStatusPill(check.state || "UNKNOWN"),
      createDevOpsTextElement("span", "", check.label || "UNKNOWN")
    );
    list.append(item);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "Morning workflow evidence unavailable."));
  }
  return list;
}

function renderDevOpsSafetyStrip(locks = []) {
  const strip = document.createElement("div");
  strip.className = "devops-safety-strip";
  const visibleLocks = locks.length ? locks : [
    "APPLY REQUIRES APPROVAL",
    "COMMIT REQUIRES APPROVAL",
    "PUSH REQUIRES APPROVAL",
    "MERGE REQUIRES APPROVAL"
  ];
  visibleLocks.forEach((lock) => strip.append(createDevOpsTextElement("strong", "", lock)));
  return strip;
}

function renderDevOpsSafetyLocks(safetyLocks = {}) {
  const list = document.createElement("div");
  list.className = "devops-safety-lock-grid";
  Object.entries(safetyLocks).forEach(([label, state]) => {
    const item = document.createElement("div");
    item.className = "devops-safety-lock";
    item.append(
      createDevOpsTextElement("span", "", label.replaceAll("_", " ")),
      createDevOpsStatusPill(state || "UNKNOWN")
    );
    list.append(item);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "Safety lock evidence unavailable."));
  }
  return list;
}

function renderDevOpsQueueMeta(queueData = {}) {
  const meta = document.createElement("div");
  meta.className = "devops-queue-meta";
  meta.append(
    createDevOpsField("Source", queueData.source || "UNKNOWN"),
    createDevOpsField("Mode", queueData.mode || "UNKNOWN"),
    createDevOpsField("Queue Count", queueData.queue_count ?? (Array.isArray(queueData.queue_items) ? queueData.queue_items.length : "UNKNOWN"))
  );
  return meta;
}

function _renderOrchestratorWorkerRegistry(workers = []) {
  const list = document.createElement("div");
  list.className = "orchestrator-worker-grid";
  workers.forEach((worker) => {
    const card = document.createElement("article");
    card.className = "orchestrator-worker-card";
    const head = document.createElement("div");
    head.className = "orchestrator-worker-head";
    head.append(
      createDevOpsTextElement("strong", "", worker.worker_id || "UNKNOWN"),
      createDevOpsStatusPill(worker.status || "UNKNOWN")
    );
    const meta = document.createElement("div");
    meta.className = "orchestrator-worker-meta";
    meta.append(
      createDevOpsField("Lane", worker.lane),
      createDevOpsField("Branch", worker.branch),
      createDevOpsField("Worktree", worker.worktree),
      createDevOpsField("Task", worker.current_task),
      createDevOpsField("Validator", worker.validator_state),
      createDevOpsField("Approval", worker.approval_state),
      createDevOpsField("Blocked", worker.blocked_reason || "NONE"),
      createDevOpsField("Last Report", worker.last_report)
    );
    card.append(head, meta);
    list.append(card);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No worker registry evidence available."));
  }
  return list;
}

function _renderOrchestratorQueue(queueItems = []) {
  const list = document.createElement("div");
  list.className = "orchestrator-queue-list";
  queueItems.forEach((item) => {
    const row = document.createElement("article");
    row.className = "orchestrator-queue-row";
    const title = createDevOpsTextElement("strong", "devops-queue-title", `#${item.queue_rank ?? "?"} ${item.task_id || "UNKNOWN"}`);
    const meta = document.createElement("div");
    meta.className = "orchestrator-inline-meta";
    meta.append(
      createDevOpsStatusPill(item.priority || "UNKNOWN"),
      createDevOpsStatusPill(item.status || "UNKNOWN"),
      createDevOpsTextElement("span", "devops-queue-lane", item.assigned_worker || "UNKNOWN"),
      createDevOpsTextElement("span", "devops-queue-lane", item.lane || "UNKNOWN")
    );
    row.append(title, meta, createDevOpsTextElement("p", "devops-queue-action", item.next_safe_action || "UNKNOWN"));
    if (String(item.status || "").toUpperCase() === "BLOCKED" || item.blocked_reason) {
      row.append(createDevOpsTextElement("p", "orchestrator-blocked-reason", `Blocked: ${item.blocked_reason || "UNKNOWN"}`));
    }
    list.append(row);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No queue assignment evidence available."));
  }
  return list;
}

function renderOrchestratorValidators(validators = []) {
  const grid = document.createElement("div");
  grid.className = "devops-validation-grid";
  validators.forEach((validator) => {
    const item = document.createElement("div");
    item.className = "devops-validation-item";
    item.append(
      createDevOpsTextElement("span", "", validator.validator_name || "UNKNOWN"),
      createDevOpsStatusPill(validator.state || "UNKNOWN"),
      createDevOpsTextElement("small", "", validator.summary || "UNKNOWN"),
      createDevOpsField("Last Run", validator.last_run),
      createDevOpsField("Operator Action", validator.operator_action_required)
    );
    grid.append(item);
  });
  if (!grid.childElementCount) {
    grid.append(createDevOpsTextElement("p", "devops-muted", "Validator state evidence unavailable."));
  }
  return grid;
}

function _renderOrchestratorAlerts(alerts = []) {
  const list = document.createElement("div");
  list.className = "orchestrator-alert-list";
  alerts.forEach((alert) => {
    const item = document.createElement("div");
    item.className = "orchestrator-alert-item";
    item.append(
      createDevOpsStatusPill(alert.state || "UNKNOWN"),
      createDevOpsTextElement("span", "", alert.label || "UNKNOWN")
    );
    list.append(item);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No active conflict or stale-worker alerts."));
  }
  return list;
}

function _renderOrchestratorCommitState(commitState = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = "devops-commit-package";
  wrapper.append(
    createDevOpsField("Readiness", commitState.readiness),
    createDevOpsField("Approved Files", commitState.approved_file_count ?? "UNKNOWN"),
    createDevOpsField("Blocked Files", commitState.blocked_file_count ?? "UNKNOWN"),
    createDevOpsTextElement("p", "devops-muted", commitState.summary || "Exact-file commit package is display-only and requires operator approval.")
  );
  return wrapper;
}

function getWorkerAge(workerId, workerAge = {}) {
  return (workerAge.worker_age_tracking || []).find((item) => item.worker_id === workerId) || {};
}

function renderCommandCenterWorkers(workers = [], workerAge = {}) {
  const list = document.createElement("div");
  list.className = "command-center-worker-grid";
  workers.forEach((worker) => {
    const age = getWorkerAge(worker.worker_id, workerAge);
    const card = document.createElement("article");
    card.className = "command-center-worker-card";
    const head = document.createElement("div");
    head.className = "orchestrator-worker-head";
    head.append(
      createDevOpsTextElement("strong", "", worker.worker_id || "UNKNOWN"),
      createDevOpsStatusPill(worker.status || "UNKNOWN")
    );
    card.append(
      head,
      createDevOpsField("Lane", worker.lane),
      createDevOpsField("Task", worker.current_task),
      createDevOpsField("Validator", worker.validator_state),
      createDevOpsField("Blocked", worker.blocked_reason || "NONE"),
      createDevOpsField("Last Report Age", age.last_report_age || "UNKNOWN"),
      createDevOpsTextElement("p", "devops-muted", age.next_safe_action || worker.next_safe_action || "Review worker state before approval.")
    );
    const advanced = document.createElement("details");
    advanced.className = "command-center-advanced";
    advanced.append(
      createDevOpsTextElement("summary", "", "Advanced worker details"),
      createDevOpsField("Branch", worker.branch),
      createDevOpsField("Worktree", worker.worktree),
      createDevOpsField("Approval", worker.approval_state),
      createDevOpsField("Last Report", worker.last_report)
    );
    card.append(advanced);
    list.append(card);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No worker evidence available."));
  }
  return list;
}

function renderCommandCenterMergeQueue(mergeQueue = {}) {
  const list = document.createElement("div");
  list.className = "command-center-list";
  (mergeQueue.merge_readiness_queue || []).forEach((item) => {
    const row = document.createElement("article");
    row.className = "orchestrator-queue-row";
    row.append(
      createDevOpsTextElement("strong", "devops-queue-title", item.package_id || "UNKNOWN"),
      createDevOpsStatusPill(item.state || "UNKNOWN"),
      createDevOpsField("Lane", item.lane),
      createDevOpsField("Worker", item.worker_id),
      createDevOpsTextElement("p", "devops-queue-action", item.next_safe_action || "UNKNOWN")
    );
    list.append(row);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No merge readiness evidence available."));
  }
  return list;
}

function renderCommandCenterConflicts(conflictCenter = {}) {
  const list = document.createElement("div");
  list.className = "command-center-list";
  (conflictCenter.conflicts || []).forEach((item) => {
    const row = document.createElement("article");
    row.className = "orchestrator-queue-row";
    row.append(
      createDevOpsTextElement("strong", "devops-queue-title", item.file_path || "UNKNOWN"),
      createDevOpsStatusPill(item.conflict_severity || "UNKNOWN"),
      createDevOpsField("Owning Worker", item.owning_worker),
      createDevOpsField("Blocked Worker", item.blocked_worker),
      createDevOpsTextElement("p", "orchestrator-blocked-reason", item.operator_required_action || "UNKNOWN")
    );
    list.append(row);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No unresolved conflicts in mock data."));
  }
  return list;
}

function renderCommandCenterApprovalInbox(approvalInbox = {}) {
  const list = document.createElement("div");
  list.className = "command-center-list";
  (approvalInbox.approval_requests || []).forEach((item) => {
    const row = document.createElement("article");
    row.className = "orchestrator-queue-row";
    row.append(
      createDevOpsTextElement("strong", "devops-queue-title", item.request_id || "UNKNOWN"),
      createDevOpsStatusPill(item.status || "UNKNOWN"),
      createDevOpsField("Type", item.request_type),
      createDevOpsField("Evidence", item.required_evidence),
      createDevOpsTextElement("p", "devops-queue-action", item.next_safe_action || "UNKNOWN")
    );
    list.append(row);
  });
  if (!list.childElementCount) {
    list.append(createDevOpsTextElement("p", "devops-muted", "No approval requests available."));
  }
  return list;
}

function renderCommandCenterGuidance(guidance = {}) {
  const panel = document.createElement("div");
  panel.className = "command-center-guidance";
  panel.append(
    createDevOpsStatusPill(guidance.warning_state || "UNKNOWN"),
    createDevOpsField("Safe", guidance.what_is_safe),
    createDevOpsField("Blocked", guidance.what_is_blocked),
    createDevOpsTextElement("p", "devops-muted", guidance.next_recommended_action || "UNKNOWN")
  );
  return panel;
}

function renderCommandCenterSafetyBanner() {
  const banner = document.createElement("section");
  banner.className = "command-center-safety-banner";
  banner.append(
    createDevOpsTextElement("strong", "", "LIVE EXECUTION BLOCKED"),
    createDevOpsTextElement("strong", "", "PAPER / LOCAL DEVELOPMENT ONLY")
  );
  return banner;
}

function renderOrchestratorWindowData(orchestrator = {}, registry = {}, queue = {}, validatorState = {}, commandCenter = {}, approvalInbox = {}, mergeQueue = {}, conflictCenter = {}, guidance = {}, workerAge = {}) {
  if (!devopsControlWindowPanel) return;
  const workers = registry.workers || [];
  const queueItems = queue.queue_items || [];
  const validators = validatorState.validator_states || [];
  const conflictItems = conflictCenter.conflicts || [];
  const conflictExists = conflictItems.length > 0 || queueItems.some((item) => String(item.status || "").toUpperCase() === "BLOCKED" || item.blocked_reason);
  const staleWorkers = workers.filter((worker) => String(worker.status || "").toUpperCase() === "STALE");
  const blockedWorkers = workers.filter((worker) => String(worker.status || "").toUpperCase() === "BLOCKED" || worker.blocked_reason);

  const header = document.createElement("section");
  header.className = "devops-window-header orchestrator-window-header";
  const title = createDevOpsTextElement("h3", "", commandCenter.title || orchestrator.title || "AI_OS Command Center");
  const summary = createDevOpsTextElement("p", "", commandCenter.summary || orchestrator.summary || "Single-pane operator surface for worker visibility, queue supervision, approvals, merge readiness, conflicts, stale evidence, and next safe actions.");
  const badges = document.createElement("div");
  badges.className = "devops-header-badges";
  badges.append(
    createDevOpsStatusPill(commandCenter.command_center_status || orchestrator.orchestrator_status || "REVIEW"),
    createDevOpsStatusPill(commandCenter.mode || orchestrator.mode || "display_only"),
    createDevOpsStatusPill(conflictExists ? "WORKER CONFLICT BLOCKED" : "CONFLICTS CLEAR")
  );
  header.append(title, summary, badges);

  const overview = document.createElement("section");
  overview.className = "orchestrator-overview";
  const counts = commandCenter.global_status || {};
  overview.append(
    createDevOpsMetric("Total Workers", counts.total_workers ?? workers.length),
    createDevOpsMetric("Active Workers", counts.active_workers ?? workers.length),
    createDevOpsMetric("Blocked Workers", counts.blocked_workers ?? blockedWorkers.length),
    createDevOpsMetric("Stale Workers", counts.stale_workers ?? staleWorkers.length),
    createDevOpsMetric("Merge Ready", counts.merge_ready_count ?? "UNKNOWN"),
    createDevOpsMetric("Approval Required", counts.approval_required_count ?? "UNKNOWN")
  );

  const registryPanel = createDevOpsPanel("Active Worker Grid", [renderCommandCenterWorkers(workers, workerAge)]);
  const mergePanel = createDevOpsPanel("Merge Readiness Queue", [renderCommandCenterMergeQueue(mergeQueue)]);
  const conflictPanel = createDevOpsPanel("Conflict Center", [renderCommandCenterConflicts(conflictCenter)]);
  const approvalPanel = createDevOpsPanel("Approval Inbox", [renderCommandCenterApprovalInbox(approvalInbox)]);
  const guidancePanel = createDevOpsPanel("Operator Guidance", [renderCommandCenterGuidance(guidance)]);
  const validatorPanel = createDevOpsDetailsPanel("Advanced Validator Supervision", [renderOrchestratorValidators(validators)]);
  const nextActionPanel = createDevOpsPanel("Next Safe Action", [
    createDevOpsTextElement("p", "devops-muted", commandCenter.next_safe_action || guidance.next_recommended_action || orchestrator.next_safe_action || queue.next_safe_action || "Review mock data only. No backend execution.")
  ]);

  const safetyLocks = orchestrator.approval_locks || [
    "APPLY REQUIRES APPROVAL",
    "COMMIT REQUIRES APPROVAL",
    "PUSH REQUIRES APPROVAL",
    "MERGE REQUIRES APPROVAL"
  ];
  const safetyStrip = renderDevOpsSafetyStrip(conflictExists ? [...safetyLocks, "WORKER CONFLICT BLOCKED"] : safetyLocks);

  const grid = document.createElement("div");
  grid.className = "devops-window-grid orchestrator-window-grid";
  grid.append(registryPanel, mergePanel, conflictPanel, approvalPanel, guidancePanel, validatorPanel);

  devopsControlWindowPanel.hidden = false;
  devopsControlWindowPanel.replaceChildren(renderCommandCenterSafetyBanner(), header, overview, nextActionPanel, grid, safetyStrip);
}

function _renderDevOpsControlData(data = {}, queueData = {}) {
  if (!devopsControlWindowPanel) return;
  const queueItems = queueData.queue_items || queueData.queue || data.work_queue || [];
  const header = document.createElement("section");
  header.className = "devops-window-header";
  const title = createDevOpsTextElement("h3", "", data.title || "DevOps Control Window");
  const summary = createDevOpsTextElement("p", "", data.summary || "Local mock-data DevOps state. Display only.");
  const badges = document.createElement("div");
  badges.className = "devops-header-badges";
  badges.append(
    createDevOpsStatusPill(data.control_window_status || "REVIEW"),
    createDevOpsStatusPill(data.mode || "display_only")
  );
  header.append(title, summary, badges);

  const nextWorkload = data.next_approved_workload || queueItems[0] || {};
  const nextWorkloadPanel = createDevOpsPanel("Next Approved Workload", [
    createDevOpsField("Rank", nextWorkload.queue_rank ? `#${nextWorkload.queue_rank}` : "UNKNOWN"),
    createDevOpsField("Title", nextWorkload.title),
    createDevOpsField("Priority", nextWorkload.priority),
    createDevOpsField("Status", nextWorkload.status),
    createDevOpsField("Lane", nextWorkload.suggested_worker_lane),
    createDevOpsTextElement("p", "devops-muted", nextWorkload.recommended_action || "UNKNOWN")
  ]);

  const queuePanel = createDevOpsPanel("Work Queue", [renderDevOpsQueueMeta(queueData), renderDevOpsQueue(queueItems)]);
  const validationPanel = createDevOpsPanel("Validation Status", [renderDevOpsValidation(data.validation_status)]);
  const commitPanel = createDevOpsPanel("Commit Package Preview", [renderDevOpsCommitPackage(data.commit_package_preview)]);
  const morningPanel = createDevOpsPanel("Morning Workflow Status", [renderDevOpsMorningWorkflow(data.morning_workflow_status)]);
  const safetyPanel = createDevOpsPanel("Safety Locks", [renderDevOpsSafetyLocks(data.safety_locks)]);
  const nextActionPanel = createDevOpsPanel("Next Safe Action", [
    createDevOpsTextElement("p", "devops-muted", data.next_safe_action || queueData.next_safe_action || "Review mock data only. No backend execution.")
  ]);
  const safetyStrip = renderDevOpsSafetyStrip(data.approval_locks || [
    "APPLY REQUIRES APPROVAL",
    "COMMIT REQUIRES APPROVAL",
    "PUSH REQUIRES APPROVAL"
  ]);

  const grid = document.createElement("div");
  grid.className = "devops-window-grid";
  grid.append(nextWorkloadPanel, queuePanel, validationPanel, commitPanel, morningPanel, safetyPanel, nextActionPanel);

  devopsControlWindowPanel.hidden = false;
  devopsControlWindowPanel.replaceChildren(header, grid, safetyStrip);
}

async function renderDevOpsControlWindow() {
  if (!devopsControlWindowPanel) return;
  devopsControlWindowPanel.hidden = false;
  devopsControlWindowPanel.textContent = "Loading AI_OS Orchestrator Window mock data...";
  try {
    const [orchestratorResponse, registryResponse, queueResponse, validatorResponse, commandCenterResponse, approvalResponse, mergeResponse, conflictResponse, guidanceResponse, workerAgeResponse] = await Promise.all([
      fetch(orchestratorWindowFixturePath, { cache: "no-store" }),
      fetch(workerRegistryFixturePath, { cache: "no-store" }),
      fetch(workerQueueFixturePath, { cache: "no-store" }),
      fetch(validatorStateFixturePath, { cache: "no-store" }),
      fetch(commandCenterStateFixturePath, { cache: "no-store" }),
      fetch(commandCenterApprovalInboxFixturePath, { cache: "no-store" }),
      fetch(commandCenterMergeQueueFixturePath, { cache: "no-store" }),
      fetch(commandCenterConflictCenterFixturePath, { cache: "no-store" }),
      fetch(commandCenterOperatorGuidanceFixturePath, { cache: "no-store" }),
      fetch(commandCenterWorkerAgeFixturePath, { cache: "no-store" })
    ]);
    const orchestratorData = orchestratorResponse.ok ? await orchestratorResponse.json() : {};
    const registryData = registryResponse.ok ? await registryResponse.json() : {};
    const queueData = queueResponse.ok ? await queueResponse.json() : {};
    const validatorData = validatorResponse.ok ? await validatorResponse.json() : {};
    const commandCenterData = commandCenterResponse.ok ? await commandCenterResponse.json() : {};
    const approvalData = approvalResponse.ok ? await approvalResponse.json() : {};
    const mergeData = mergeResponse.ok ? await mergeResponse.json() : {};
    const conflictData = conflictResponse.ok ? await conflictResponse.json() : {};
    const guidanceData = guidanceResponse.ok ? await guidanceResponse.json() : {};
    const workerAgeData = workerAgeResponse.ok ? await workerAgeResponse.json() : {};
    renderOrchestratorWindowData(orchestratorData, registryData, queueData, validatorData, commandCenterData, approvalData, mergeData, conflictData, guidanceData, workerAgeData);
  } catch {
    renderOrchestratorWindowData({
      title: "AI_OS Command Center",
      summary: "Mock data unavailable. All actions remain blocked.",
      orchestrator_status: "UNKNOWN",
      mode: "display_only",
      approval_locks: ["APPLY REQUIRES APPROVAL", "COMMIT REQUIRES APPROVAL", "PUSH REQUIRES APPROVAL", "MERGE REQUIRES APPROVAL"]
    }, { workers: [] }, { queue_items: [] }, { validator_states: [] });
  }
}

function hideTradingLabNextActionCard() {
  if (!tradingLabNextActionCard) return;
  tradingLabNextActionCard.hidden = true;
  tradingLabNextActionCard.replaceChildren();
}

function _createTradingLabField(label, value) {
  const item = document.createElement("div");
  item.className = "trading-lab-field";
  const fieldLabel = document.createElement("span");
  fieldLabel.textContent = label;
  const fieldValue = document.createElement("strong");
  fieldValue.textContent = value || "UNKNOWN";
  item.append(fieldLabel, fieldValue);
  return item;
}

function getTradingLabStateClass(status = "") {
  const value = String(status).toLowerCase();
  if (value.includes("blocked")) return "is-blocked";
  if (value.includes("review") || value.includes("pending")) return "is-review";
  if (value.includes("ready") || value.includes("pass") || value.includes("simulated")) return "is-ready";
  return "is-unknown";
}

function createTradingLabSafetyChip(label, value) {
  const chip = document.createElement("span");
  chip.className = "trading-lab-safety-chip";
  chip.textContent = `${label}: ${value}`;
  return chip;
}

const progressValueKeys = [
  "progress_percent",
  "progressPercent",
  "completion_percent",
  "completionPercent",
  "readiness_percent",
  "readinessPercent",
  "validation_percent",
  "validationPercent",
  "paper_workflow_percent",
  "paperWorkflowPercent",
  "safety_gate_percent",
  "safetyGatePercent"
];

function normalizeProgressValue(source, fallback = "Pending validation") {
  if (typeof source === "number" && Number.isFinite(source)) {
    return `${Math.max(0, Math.min(100, Math.round(source)))}%`;
  }
  if (typeof source === "string") {
    const trimmed = source.trim();
    if (/^\d{1,3}%$/.test(trimmed)) {
      const numeric = Number(trimmed.replace("%", ""));
      return `${Math.max(0, Math.min(100, numeric))}%`;
    }
    return fallback;
  }
  if (!source || typeof source !== "object") {
    return fallback;
  }
  for (const key of progressValueKeys) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      return normalizeProgressValue(source[key], fallback);
    }
  }
  return fallback;
}

function createProgressBadge(label, source, fallback = "Pending validation") {
  const badge = document.createElement("span");
  badge.className = "progress-badge";
  badge.textContent = `${label}: ${normalizeProgressValue(source, fallback)}`;
  return badge;
}

function createTradingLabWorkspaceCard(card, index, total) {
  const item = document.createElement("details");
  item.className = `trading-lab-workspace-card ${getTradingLabStateClass(card.status)}`;
  item.setAttribute("aria-label", `${card.title} status card`);
  if (index === 0 || card.id === "next_action") {
    item.open = true;
  }

  const summary = document.createElement("summary");
  summary.className = "trading-lab-card-summary";
  const step = document.createElement("span");
  step.className = "trading-lab-step";
  step.textContent = `Step ${index + 1}`;

  const title = document.createElement("h3");
  title.textContent = card.title || "Trading Lab Step";

  const status = document.createElement("strong");
  status.className = "trading-lab-card-status";
  status.textContent = card.status || "UNKNOWN";
  summary.append(step, title, status, createProgressBadge("Phase", card, "Pending validation"));

  const body = document.createElement("div");
  body.className = "trading-lab-card-detail";
  const meaning = document.createElement("p");
  meaning.textContent = card.meaning || "Status needs review.";

  const nextAction = document.createElement("small");
  nextAction.textContent = card.next_action || "Review mock-only status.";

  body.append(meaning, nextAction);
  item.append(summary, body);

  if (index < total - 1) {
    const flow = document.createElement("span");
    flow.className = "trading-lab-flow-arrow";
    flow.setAttribute("aria-hidden", "true");
    flow.textContent = "->";
    item.append(flow);
  }

  return item;
}

function createPaperBotCoreStep(step) {
  const card = document.createElement("details");
  card.className = `paper-bot-core-step ${getTradingLabStateClass(step.status)}`;
  if (step.id === "signal" || step.id === "next_action") {
    card.open = true;
  }

  const summary = document.createElement("summary");
  const title = document.createElement("strong");
  title.textContent = step.title || "Paper Bot Step";
  const status = document.createElement("span");
  status.textContent = step.status || "UNKNOWN";
  const progress = createProgressBadge("Progress", step, "Pending validation");
  const text = document.createElement("p");
  text.textContent = step.summary || "Review this paper-only step.";
  summary.append(title, status, progress, text);

  const detail = document.createElement("small");
  detail.textContent = step.detail || "No detail provided.";
  card.append(summary, detail);
  return card;
}

function renderPaperBotCorePanel(data) {
  const panel = document.createElement("section");
  panel.className = "paper-bot-core-panel";
  panel.setAttribute("aria-label", "Paper Bot Core");

  const head = document.createElement("div");
  head.className = "paper-bot-core-head";
  const title = document.createElement("strong");
  title.textContent = data.title || "Paper Bot Core";
  const badge = document.createElement("span");
  badge.textContent = data.badge || "PAPER ONLY";
  const summary = document.createElement("p");
  summary.textContent = data.summary || "Paper-only bot core summary.";
  head.append(title, badge, summary);

  const safety = document.createElement("div");
  safety.className = "paper-bot-core-safety";
  [
    ["Live Execution", data.live_execution_status || "BLOCKED"],
    ["Broker", data.broker_status || "BLOCKED"],
    ["OANDA", data.oanda_status || "BLOCKED"],
    ["Secrets/API keys", data.api_key_status || "BLOCKED"]
  ].forEach(([label, value]) => {
    safety.append(createTradingLabSafetyChip(label, value));
  });

  const grid = document.createElement("div");
  grid.className = "paper-bot-core-grid";
  (Array.isArray(data.steps) ? data.steps : []).forEach((step) => {
    grid.append(createPaperBotCoreStep(step));
  });

  const blocked = document.createElement("div");
  blocked.className = "paper-bot-core-blocked";
  const blockedTitle = document.createElement("strong");
  blockedTitle.textContent = "Blocked";
  const blockedText = document.createElement("p");
  blockedText.textContent = (data.blocked_actions || []).join(" | ");
  blocked.append(blockedTitle, blockedText);

  panel.append(head, safety, grid, blocked);
  return panel;
}

function createPaperRunnerField(label, value) {
  const item = document.createElement("div");
  item.className = "paper-runner-field";
  const fieldLabel = document.createElement("span");
  fieldLabel.textContent = label;
  const fieldValue = document.createElement("strong");
  const normalizedValue = value === null || value === undefined || value === "" ? "UNKNOWN" : String(value);
  fieldValue.textContent = normalizedValue;
  item.append(fieldLabel, fieldValue);
  return item;
}

function createPaperRunnerCard(title, status, fields, note = "") {
  const card = document.createElement("article");
  card.className = `paper-runner-card ${getTradingLabStateClass(status)}`;

  const head = document.createElement("div");
  head.className = "paper-runner-card-head";
  const heading = document.createElement("strong");
  heading.textContent = title;
  const badge = document.createElement("span");
  badge.textContent = status || "UNKNOWN";
  head.append(heading, badge, createProgressBadge("Validation", fields, "Not measured"));

  const grid = document.createElement("div");
  grid.className = "paper-runner-field-grid";
  fields.forEach(([label, value]) => {
    grid.append(createPaperRunnerField(label, value));
  });

  card.append(head, grid);
  if (note) {
    const noteText = document.createElement("p");
    noteText.className = "paper-runner-note";
    noteText.textContent = note;
    card.append(noteText);
  }
  return card;
}

function renderTradingLabPaperRunnerPanel(data) {
  if (!data) return null;
  const panel = document.createElement("section");
  panel.className = "paper-runner-panel";
  panel.setAttribute("aria-label", "Trading Lab Paper Runner");

  const head = document.createElement("div");
  head.className = "paper-runner-head";
  const title = document.createElement("strong");
  title.textContent = data.panel_title || "Trading Lab Paper Runner";
  const badge = document.createElement("span");
  badge.textContent = data.paper_decision || data.paper_runner_status || "UNKNOWN";
  const progress = createProgressBadge("Paper workflow", data, "Pending validation");
  const summary = document.createElement("p");
  summary.textContent = `Source: ${data.source || "local fixture-only"}. The dashboard reads mock data only.`;
  head.append(title, badge, progress, summary);

  const safety = document.createElement("div");
  safety.className = "paper-runner-safety";
  [
    ["Live Execution", data.live_execution_status || "BLOCKED"],
    ["Broker", data.broker_status || "BLOCKED"],
    ["OANDA", data.oanda_status || "BLOCKED"],
    ["API Keys", data.api_key_status || "BLOCKED"],
    ["Secrets", data.secrets_status || "BLOCKED"],
    ["Real Webhooks", data.real_webhook_status || "BLOCKED"],
    ["Real Orders", data.real_order_status || "BLOCKED"]
  ].forEach(([label, value]) => {
    safety.append(createTradingLabSafetyChip(label, value));
  });

  const signal = data.signal || {};
  const latency = data.latency || {};
  const regime = data.regime || {};
  const riskGate = data.risk_gate || {};
  const decision = data.decision || {};
  const paperResult = data.paper_result || {};
  const scorecard = data.scorecard || {};
  const validation = data.validation || {};
  const latencyWarning = Number(latency.latency_seconds) < 0 ? (latency.warning || "Timestamp needs review.") : "";

  const cards = document.createElement("div");
  cards.className = "paper-runner-card-grid";
  cards.append(
    createPaperRunnerCard("Signal In", data.paper_runner_status, [
      ["Signal ID", signal.signal_id || data.latest_signal_id],
      ["Symbol", signal.symbol],
      ["Direction", signal.direction],
      ["Confidence", signal.confidence],
      ["Source", signal.source],
      ["Received", signal.received_time]
    ]),
    createPaperRunnerCard("Latency", latency.stale_status, [
      ["Received", latency.received_time],
      ["Validation Start", latency.validation_start_time],
      ["Validation End", latency.validation_end_time],
      ["Latency Seconds", latency.latency_seconds],
      ["Stale Status", latency.stale_status]
    ], latencyWarning),
    createPaperRunnerCard("Regime Check", regime.regime_status, [
      ["Regime", regime.regime],
      ["Status", regime.regime_status],
      ["Reason", regime.reason]
    ]),
    createPaperRunnerCard("Risk Gate", riskGate.risk_gate_status, [
      ["Status", riskGate.risk_gate_status],
      ["Approved", riskGate.approved === true ? "true" : "false"],
      ["Reason", riskGate.reason],
      ["Blocked Reason", riskGate.blocked_reason]
    ]),
    createPaperRunnerCard("Paper Decision", decision.decision || data.paper_decision, [
      ["Decision", decision.decision || data.paper_decision],
      ["Simulated Result", decision.simulated_result_status],
      ["Blocked Reason", decision.blocked_reason || data.blocked_reason],
      ["Live Execution", decision.live_execution_status || data.live_execution_status]
    ]),
    createPaperRunnerCard("Paper Result", data.paper_decision, [
      ["Result ID", paperResult.result_id],
      ["Paper Entry", paperResult.paper_entry],
      ["Paper Stop", paperResult.paper_stop],
      ["Paper Target", paperResult.paper_target],
      ["Simulated PnL R", paperResult.simulated_pnl_r]
    ]),
    createPaperRunnerCard("Scorecard", scorecard.paper_simulated_trades > 0 ? "READY_FOR_REVIEW" : "REVIEW", [
      ["Total Paper Trades", scorecard.total_paper_trades],
      ["Blocked Trades", scorecard.blocked_trades],
      ["Paper Simulated", scorecard.paper_simulated_trades],
      ["Win Rate", scorecard.win_rate],
      ["Expectancy R", scorecard.expectancy_r],
      ["Profit Factor", scorecard.profit_factor],
      ["Avg Latency", scorecard.average_latency_seconds]
    ]),
    createPaperRunnerCard("Next Safe Action", validation.validator_status || data.paper_runner_status, [
      ["Next Action", data.next_safe_action],
      ["Validator", validation.validator_status],
      ["Report", validation.validation_report_id],
      ["Warnings", Array.isArray(validation.warnings) ? validation.warnings.join(" | ") : ""]
    ], "Safety reminder: paper-only, local fixture-only, no broker, no real webhook, no real order.")
  );

  panel.append(head, safety, cards);
  return panel;
}

function createAiosOrchestrationCard(card = {}) {
  const status = card.status || "UNKNOWN";
  const panel = createPaperRunnerCard(
    card.title || "Runtime Card",
    status,
    [
      ["Meaning", card.meaning || card.summary || "Local file-based orchestration status."],
      ["Source", card.source || "local mock-data"],
      ["Next", card.next_action || "Review the next safe action."]
    ],
    card.note || ""
  );
  panel.classList.add("aios-orchestration-card");
  return panel;
}

function renderAiosOrchestrationControlRoom(data) {
  if (!data) return null;
  const section = document.createElement("section");
  section.className = "paper-runner-panel";
  section.setAttribute("aria-label", "AI_OS Orchestration Control Room");

  const head = document.createElement("div");
  head.className = "paper-runner-head";
  const title = document.createElement("strong");
  title.textContent = data.title || "AI_OS Orchestration Control Room";
  const badge = document.createElement("span");
  badge.textContent = data.view_status || data.mode || "LOCAL MOCK";
  const summary = document.createElement("p");
  summary.textContent = data.summary || "Local queue, ownership, validator, and next-action view. It is mock-data only.";
  head.append(title, badge, summary);

  const locks = data.safety_locks || {};
  const safety = document.createElement("div");
  safety.className = "paper-runner-safety";
  [
    ["Live Execution", locks.live_execution_status || data.live_execution_status || "BLOCKED"],
    ["Broker", locks.broker_status || data.broker_status || "BLOCKED"],
    ["OANDA", locks.oanda_status || data.oanda_status || "BLOCKED"],
    ["API Keys", locks.api_key_status || data.api_key_status || "BLOCKED"],
    ["Secrets", locks.secrets_status || data.secrets_status || "BLOCKED"],
    ["Real Webhooks", locks.real_webhook_status || data.real_webhook_status || "BLOCKED"],
    ["Real Orders", locks.real_order_status || data.real_order_status || "BLOCKED"],
    ["Background", locks.background_execution_status || data.background_execution_status || "BLOCKED"],
    ["Scheduled", locks.scheduled_automation_status || data.scheduled_automation_status || "BLOCKED"],
    ["Startup", locks.startup_persistence_status || data.startup_persistence_status || "BLOCKED"],
    ["External LLM", locks.external_llm_install_status || data.external_llm_install_status || "NOT_ENABLED"]
  ].forEach(([label, value]) => {
    safety.append(createTradingLabSafetyChip(label, value));
  });

  const cards = Array.isArray(data.cards) ? data.cards : [];
  const defaultCards = cards.filter((card) => card.default_visible !== false);
  const advancedCards = cards.filter((card) => card.default_visible === false);
  const cardGrid = document.createElement("div");
  cardGrid.className = "paper-runner-card-grid";
  defaultCards.forEach((card) => {
    cardGrid.append(createAiosOrchestrationCard(card));
  });

  const diagnostics = document.createElement("details");
  diagnostics.className = "paper-bot-core-step";
  const diagnosticsSummary = document.createElement("summary");
  const diagnosticsTitle = document.createElement("strong");
  diagnosticsTitle.textContent = "Advanced diagnostics";
  const diagnosticsStatus = document.createElement("span");
  diagnosticsStatus.textContent = "collapsed";
  diagnosticsSummary.append(diagnosticsTitle, diagnosticsStatus);
  const diagnosticsText = document.createElement("p");
  diagnosticsText.textContent = "Agent ownership, validator chain, and raw source references stay hidden until needed.";
  diagnostics.append(diagnosticsSummary, diagnosticsText);

  if (advancedCards.length) {
    const advancedGrid = document.createElement("div");
    advancedGrid.className = "paper-runner-card-grid";
    advancedCards.forEach((card) => {
      advancedGrid.append(createAiosOrchestrationCard(card));
    });
    diagnostics.append(advancedGrid);
  }

  const sourceRefs = Array.isArray(data.source_references) ? data.source_references : [];
  if (sourceRefs.length) {
    const sourceList = createTradingStackList(sourceRefs);
    sourceList.className = "trading-lab-window-safety";
    diagnostics.append(sourceList);
  }

  const nextAction = document.createElement("div");
  nextAction.className = "trading-lab-blocked-actions";
  const nextTitle = document.createElement("strong");
  nextTitle.textContent = "Next safe action";
  const nextText = document.createElement("p");
  nextText.textContent = data.next_safe_action || "Run the local orchestration control room validator.";
  nextAction.append(nextTitle, nextText);

  section.append(head, safety, cardGrid, diagnostics, nextAction);
  return section;
}

function createTradingLabWindow(key, windowData = {}, engineData = null, safetyData = null) {
  const panel = document.createElement("details");
  panel.className = `trading-lab-window ${key === "next_action" ? "is-next-action" : ""} ${getTradingLabStateClass(windowData.status)}`;
  if (windowData.expanded_by_default || key === "next_action") {
    panel.open = true;
  }

  const summary = document.createElement("summary");
  summary.className = "trading-lab-window-summary";

  const title = document.createElement("strong");
  title.textContent = windowData.title || key.replaceAll("_", " ");

  const status = document.createElement("span");
  status.textContent = windowData.status || "PLANNED";
  const progress = createProgressBadge("Phase", windowData, "Pending validation");

  const summaryText = document.createElement("p");
  summaryText.textContent = windowData.summary || "Paper trading workspace window.";

  summary.append(title, status, progress, summaryText);

  const body = document.createElement("div");
  body.className = "trading-lab-window-body";

  if (key === "tradingview_chart") {
    const chartPlaceholder = document.createElement("div");
    chartPlaceholder.className = "trading-lab-chart-placeholder";
    chartPlaceholder.textContent = "TradingView chart embed planned";
    body.append(chartPlaceholder);
  }

  const detail = document.createElement("p");
  detail.textContent = windowData.detail || "Details expand here when needed.";
  body.append(detail);

  if (key === "paper_trade_engine" && engineData) {
    const engineList = document.createElement("dl");
    engineList.className = "trading-lab-engine-list";
    [
      ["Signal", engineData.signal],
      ["Paper Risk Gate", engineData.risk_gate],
      ["Paper Decision", engineData.decision],
      ["Paper Trade Result", engineData.paper_trade_result],
      ["Paper Scorecard", engineData.scorecard],
      ["Next Safe Action", engineData.next_safe_action]
    ].forEach(([label, value]) => {
      const term = document.createElement("dt");
      term.textContent = label;
      const description = document.createElement("dd");
      description.textContent = value || "Review pending.";
      engineList.append(term, description);
    });
    body.append(engineList);
  }

  if (key === "status_telemetry" && safetyData) {
    const telemetry = document.createElement("div");
    telemetry.className = "trading-lab-window-telemetry";
    [
      ["Live Execution", safetyData.live_execution_status],
      ["Broker", safetyData.broker_status],
      ["OANDA", safetyData.oanda_status],
      ["Credentials", safetyData.credential_status],
      ["Real Orders", safetyData.real_order_status],
      ["Real Webhooks", safetyData.real_webhook_status]
    ].forEach(([label, value]) => {
      telemetry.append(createTradingLabSafetyChip(label, value || "BLOCKED"));
    });
    body.append(telemetry);
  }

  const safety = Array.isArray(windowData.safety) ? windowData.safety : [];
  if (safety.length) {
    const safetyList = createTradingStackList(safety);
    safetyList.className = "trading-lab-window-safety";
    body.append(safetyList);
  }

  panel.append(summary, body);
  return panel;
}

function createHandoffStatusChip(label, value) {
  const chip = document.createElement("span");
  chip.className = "trading-lab-handoff-chip";
  chip.textContent = `${label}: ${value === null || value === undefined || value === "" ? "BLOCKED" : value}`;
  return chip;
}

function createExternalHandoffCard(panelData = {}) {
  const card = document.createElement("article");
  card.className = `trading-lab-handoff-card ${getTradingLabStateClass(panelData.status)}`;

  const head = document.createElement("div");
  head.className = "trading-lab-handoff-card-head";
  const title = document.createElement("strong");
  title.textContent = panelData.title || "External Handoff Panel";
  const status = document.createElement("span");
  status.textContent = panelData.status || "MOCK ONLY";
  head.append(title, status, createProgressBadge("Validation", panelData, "Pending validation"));

  const summary = document.createElement("p");
  summary.textContent = panelData.summary || "Local mock-only handoff planning panel.";

  const fields = document.createElement("dl");
  fields.className = "trading-lab-handoff-fields";
  Object.entries(panelData.fields || {}).forEach(([label, value]) => {
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value === null || value === undefined || value === "" ? "UNKNOWN" : value;
    fields.append(term, description);
  });

  const nextAction = document.createElement("small");
  nextAction.textContent = panelData.next_action || "Keep this panel paper-only and mock-only.";

  card.append(head, summary, fields, nextAction);
  return card;
}

function renderExternalHandoffPanels(handoffData) {
  if (!handoffData) return null;
  const section = document.createElement("section");
  section.className = "trading-lab-handoff-system";
  section.setAttribute("aria-label", "Trading Lab External Handoff Panels");

  const head = document.createElement("div");
  head.className = "trading-lab-handoff-head";
  const title = document.createElement("strong");
  title.textContent = handoffData.title || "Paper Signal Handoff Path";
  const badge = document.createElement("span");
  badge.textContent = handoffData.status || handoffData.mode || "MOCK ONLY";
  const progress = createProgressBadge("Paper workflow", handoffData, "Pending validation");
  const summary = document.createElement("p");
  summary.textContent = handoffData.summary || "TradingView signal idea -> AI_OS validation -> TradersPost paper route preview.";
  head.append(title, badge, progress, summary);

  const blocked = document.createElement("div");
  blocked.className = "trading-lab-handoff-blocks";
  Object.entries(handoffData.blocked_fields || {}).forEach(([label, value]) => {
    blocked.append(createHandoffStatusChip(label.replaceAll("_", " "), value));
  });

  const grid = document.createElement("div");
  grid.className = "trading-lab-handoff-grid";
  (Array.isArray(handoffData.panels) ? handoffData.panels : []).forEach((panelData) => {
    grid.append(createExternalHandoffCard(panelData));
  });

  section.append(head, blocked, grid);
  return section;
}

function normalizePhase28PaperHandoff(data) {
  if (!data) return null;
  return {
    title: data.title || "Phase 28 TV/TP Paper Handoff",
    status: data.status || data.mode || "PAPER ONLY",
    mode: data.mode || "paper_only",
    summary: data.summary || "TradingView-style signal -> AI_OS validation -> TradersPost-style paper route preview.",
    blocked_fields: data.blocked_fields || {
      live_execution: data.live_execution || "BLOCKED",
      broker: data.broker || "BLOCKED",
      real_order: data.real_order || "BLOCKED",
      api_key_required: data.api_key_required === false ? "false" : "BLOCKED"
    },
    panels: Array.isArray(data.panels) ? data.panels : [
      {
        title: "Signal",
        status: data.payload_valid ? "VALID" : "PENDING VALIDATION",
        summary: "TradingView-style paper signal reviewed by AI_OS.",
        fields: {
          signal_id: data.signal_id,
          source_platform: data.source_platform,
          symbol: data.symbol,
          timeframe: data.timeframe,
          direction: data.direction,
          strategy_name: data.strategy_name
        },
        next_action: "Validate required payload fields."
      },
      {
        title: "Latency",
        status: data.stale_status || "Pending validation",
        summary: "Latency fields stay local and paper-only.",
        fields: {
          alert_created_time: data.alert_created_time || "Pending validation",
          alert_received_time: data.alert_received_time || "Pending validation",
          validation_start_time: data.validation_start_time || "Pending validation",
          validation_end_time: data.validation_end_time || "Pending validation",
          route_preview_time: data.route_preview_time || "Pending validation",
          total_delay_seconds: data.total_delay_seconds ?? "Pending validation"
        },
        next_action: "Measure timestamps locally before trusting route timing."
      },
      {
        title: "Paper Route",
        status: data.paper_route_status || "PREVIEW_ONLY",
        summary: "TradersPost-style paper route preview cannot execute orders.",
        fields: {
          route_style: data.route_style,
          risk_gate_status: data.risk_gate_status,
          operator_decision_required: data.operator_decision_required,
          live_execution: data.live_execution,
          broker: data.broker,
          real_order: data.real_order
        },
        next_action: "Operator decision is required before any future paper review."
      }
    ]
  };
}

function renderTradingLabWindowSystem(data) {
  if (!data) return null;
  const section = document.createElement("section");
  section.className = "trading-lab-window-system";
  section.setAttribute("aria-label", "Modular Trading Workspace");

  const head = document.createElement("div");
  head.className = "trading-lab-window-system-head";
  const title = document.createElement("strong");
  title.textContent = data.title || "Modular Trading Workspace";
  const badge = document.createElement("span");
  badge.textContent = data.layout_mode || "modular_windows";
  const progress = createProgressBadge("Readiness", data, "Pending validation");
  const summary = document.createElement("p");
  summary.textContent = data.summary || "Flexible paper trading workspace windows.";
  head.append(title, badge, progress, summary);

  const flexibility = document.createElement("div");
  flexibility.className = "trading-lab-window-flexibility";
  const flexibilityData = data.window_flexibility || {};
  [
    ["Resizable", flexibilityData.resizable_planned],
    ["Detachable", flexibilityData.detachable_planned],
    ["Layout Memory", flexibilityData.layout_memory_planned],
    ["Popout", flexibilityData.popout_planned]
  ].forEach(([label, planned]) => {
    const item = document.createElement("span");
    item.textContent = `${label}: ${planned ? "planned" : "not active"}`;
    flexibility.append(item);
  });

  const grid = document.createElement("div");
  grid.className = "trading-lab-window-grid";
  const windows = data.windows || {};
  ["tradingview_chart", "paper_trade_engine", "traderspost_route_preview", "status_telemetry", "next_action"].forEach((key) => {
    grid.append(createTradingLabWindow(key, windows[key], data.paper_trade_engine, data.safety));
  });

  const platformRule = document.createElement("div");
  platformRule.className = "trading-lab-window-platform-rule";
  const platformTitle = document.createElement("strong");
  platformTitle.textContent = "External platform placement";
  const platformText = document.createElement("p");
  platformText.textContent = data.external_platforms?.path || "Trading Lab -> Tools / Connectors -> External Trading Platforms";
  const platformStatus = document.createElement("small");
  platformStatus.textContent = "Hidden/collapsed by default. Planning-only. No login, credentials, broker, real route, or execution.";
  platformRule.append(platformTitle, platformText, platformStatus);

  const handoffPanels = renderExternalHandoffPanels(data.handoff_path);
  const children = [head, flexibility, grid];
  if (handoffPanels) {
    children.push(handoffPanels);
  }
  children.push(platformRule);
  section.append(...children);
  return section;
}

function createTradingStackList(items) {
  const list = document.createElement("ul");
  list.className = "trading-stack-list";
  items.forEach((item) => {
    const entry = document.createElement("li");
    entry.textContent = item;
    list.append(entry);
  });
  return list;
}

function createTradingStackPanel(title, status, items, footer) {
  const panel = document.createElement("article");
  panel.className = "trading-stack-panel";

  const heading = document.createElement("div");
  heading.className = "trading-stack-panel-head";
  const titleText = document.createElement("strong");
  titleText.textContent = title;
  const statusText = document.createElement("span");
  statusText.textContent = status;
  heading.append(titleText, statusText);

  const body = createTradingStackList(items);
  const note = document.createElement("p");
  note.className = "trading-stack-note";
  note.textContent = footer;

  panel.append(heading, body, note);
  return panel;
}

function renderTradingStackHub() {
  const hub = document.createElement("section");
  hub.className = "trading-stack-hub";
  hub.setAttribute("aria-label", "AI_OS Trading Stack Hub");

  const header = document.createElement("div");
  header.className = "trading-stack-hub-head";
  const title = document.createElement("strong");
  title.textContent = "AI_OS Trading Stack Hub";
  const badge = document.createElement("span");
  badge.textContent = "mock-only / paper-only";
  header.append(title, badge);

  const grid = document.createElement("div");
  grid.className = "trading-stack-grid";
  grid.append(
    createTradingStackPanel(
      "TradingView Chart Panel",
      "official widget placeholder",
      [
        "AI_OS-owned interface; no TradingView UI copied.",
        "Official widget/embed placeholder only.",
        "Symbol selector placeholder.",
        "Timeframe notes and strategy notes.",
        "Alert payload placeholder; no real webhook.",
        "Partner/referral placeholder pending approval."
      ],
      "No API keys, no broker connection, no orders."
    ),
    createTradingStackPanel(
      "AI_OS Validation Layer",
      "live execution BLOCKED",
      [
        "Signal intake review.",
        "Regime filter.",
        "Risk gate.",
        "Paper profitability scorecard.",
        "Blocked/unblocked status remains paper-only.",
        "No broker connected."
      ],
      "AI_OS validates; it does not place trades."
    ),
    createTradingStackPanel(
      "TradersPost Route Panel",
      "paper-only route status",
      [
        "Webhook JSON preview mock-only.",
        "Setup checklist placeholder.",
        "Manual external setup handoff placeholder.",
        "Partner/referral placeholder pending approval.",
        "No real webhook.",
        "No API keys or orders."
      ],
      "Routing stays blocked until separate approval."
    )
  );

  hub.append(header, grid);
  return hub;
}

function createWorkstationChip(label, value, state = "") {
  const chip = document.createElement("span");
  chip.className = `trading-workstation-chip ${getTradingLabStateClass(state || value)}`;
  chip.textContent = `${label}: ${value === null || value === undefined || value === "" ? "Pending validation" : value}`;
  return chip;
}

function createWorkstationList(items = [], formatter = (item) => String(item)) {
  const list = document.createElement("ul");
  list.className = "trading-workstation-list";
  items.forEach((item) => {
    const entry = document.createElement("li");
    entry.textContent = formatter(item);
    list.append(entry);
  });
  return list;
}

function createWorkstationPanel(title, children = []) {
  const panel = document.createElement("section");
  panel.className = "trading-workstation-panel";
  const heading = document.createElement("strong");
  heading.textContent = title;
  panel.append(heading, ...children.filter(Boolean));
  return panel;
}

function renderPhase23PaperSignalNormalization(data = {}) {
  const blocked = data.blocked_fields || {};
  return createWorkstationPanel(data.title || "Phase 23 Signal Normalization", [
    createWorkstationChip("Stage", "Stage 1 / Phase 23"),
    createWorkstationChip("Normalized signal", data.normalized_signal_id || "Pending validation"),
    createWorkstationChip("Source signal", data.source_signal_id || "Pending validation"),
    createWorkstationChip("Source", data.source_platform || "Pending validation"),
    createWorkstationChip("Received by", data.received_by || "AI_OS"),
    createWorkstationChip("Symbol", data.symbol || "Pending validation"),
    createWorkstationChip("Timeframe", data.timeframe || "Pending validation"),
    createWorkstationChip("Direction", data.direction || "Pending validation"),
    createWorkstationChip("Strategy", data.strategy_name || "Pending validation"),
    createWorkstationChip("Signal type", data.signal_type || "Pending validation"),
    createWorkstationChip("Confidence", data.confidence || "Not measured"),
    createWorkstationChip("Payload valid", data.payload_valid === true ? "true" : "false", data.payload_valid ? "READY" : "REVIEW_REQUIRED"),
    createWorkstationChip("Normalization", data.normalization_status || "Pending validation", data.normalization_status),
    createWorkstationChip("Risk gate", data.risk_gate_status || "REVIEW_REQUIRED", data.risk_gate_status),
    createWorkstationChip("Missing fields", Array.isArray(data.missing_fields) && data.missing_fields.length ? data.missing_fields.join(", ") : "None listed"),
    createWorkstationChip("Rejected reason", data.rejected_reason || "Pending validation"),
    createWorkstationList(data.downstream_targets || [], (item) => `Feeds: ${item}`),
    createWorkstationChip("Live execution", data.live_execution || blocked.live_execution || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Broker", data.broker || blocked.broker || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real order", data.real_order || blocked.real_order || "BLOCKED", "BLOCKED"),
    createWorkstationChip("API key required", data.api_key_required === false ? "false" : "BLOCKED", "BLOCKED")
  ]);
}

function renderPhase25LatencyMeasurementCore(data = {}) {
  const stepDelays = data.step_delays || {};
  const blocked = data.blocked_fields || {};
  return createWorkstationPanel(data.title || "Phase 25 Latency Measurement Core", [
    createWorkstationChip("Stage", "Stage 3 / Phase 25"),
    createWorkstationChip("Measurement", data.measurement_status || "Pending validation", data.measurement_status),
    createWorkstationChip("Signal", data.signal_id || "Pending validation"),
    createWorkstationChip("Alert created", data.alert_created_time || "Pending validation"),
    createWorkstationChip("Alert received", data.alert_received_time || "Pending validation"),
    createWorkstationChip("Validation", `${data.validation_start_time || "Pending"} -> ${data.validation_end_time || "validation"}`),
    createWorkstationChip("Route preview", data.route_preview_time || "Pending validation"),
    createWorkstationChip("Paper execution", data.paper_execution_time || "Pending validation"),
    createWorkstationChip("Journal write", data.journal_write_time || "Pending validation"),
    createWorkstationChip("Scorecard update", data.scorecard_update_time || "Pending validation"),
    createWorkstationChip("Total delay", data.total_delay_seconds === null || data.total_delay_seconds === undefined ? "Pending validation" : `${data.total_delay_seconds}s`, data.stale_status),
    createWorkstationChip("Stale status", data.stale_status || "Pending validation", data.stale_status),
    createWorkstationChip("Delayed reason", data.delayed_reason || "Not measured"),
    createWorkstationChip("Clock skew", data.clock_skew_status || "Pending validation", data.clock_skew_status),
    createWorkstationChip("Alert to receive", stepDelays.alert_to_receive_seconds === null || stepDelays.alert_to_receive_seconds === undefined ? "Not measured" : `${stepDelays.alert_to_receive_seconds}s`),
    createWorkstationChip("Receive to validation", stepDelays.receive_to_validation_start_seconds === null || stepDelays.receive_to_validation_start_seconds === undefined ? "Not measured" : `${stepDelays.receive_to_validation_start_seconds}s`),
    createWorkstationChip("Validation duration", stepDelays.validation_duration_seconds === null || stepDelays.validation_duration_seconds === undefined ? "Not measured" : `${stepDelays.validation_duration_seconds}s`),
    createWorkstationChip("Validation to route", stepDelays.validation_to_route_preview_seconds === null || stepDelays.validation_to_route_preview_seconds === undefined ? "Not measured" : `${stepDelays.validation_to_route_preview_seconds}s`),
    createWorkstationChip("Route to paper execution", stepDelays.route_preview_to_paper_execution_seconds === null || stepDelays.route_preview_to_paper_execution_seconds === undefined ? "Not measured" : `${stepDelays.route_preview_to_paper_execution_seconds}s`),
    createWorkstationChip("Paper execution to journal", stepDelays.paper_execution_to_journal_seconds === null || stepDelays.paper_execution_to_journal_seconds === undefined ? "Not measured" : `${stepDelays.paper_execution_to_journal_seconds}s`),
    createWorkstationChip("Journal to scorecard", stepDelays.journal_to_scorecard_seconds === null || stepDelays.journal_to_scorecard_seconds === undefined ? "Not measured" : `${stepDelays.journal_to_scorecard_seconds}s`),
    createWorkstationList(data.measurement_rules || [], (item) => `Rule: ${item}`),
    createWorkstationChip("Live execution", data.live_execution || blocked.live_execution || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Broker", data.broker || blocked.broker || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real order", data.real_order || blocked.real_order || "BLOCKED", "BLOCKED"),
    createWorkstationChip("API key required", data.api_key_required === false ? "false" : "BLOCKED", "BLOCKED")
  ]);
}

function renderPaperTradingBotStatus(data = {}) {
  return createWorkstationPanel("Paper Trading Bot Status", [
    createWorkstationChip("Decision", data.decision || "Pending validation", data.decision),
    createWorkstationChip("Bot status", data.bot_status || "Pending validation", data.bot_status),
    createWorkstationChip("Signal source", data.signal_source || "local sample"),
    createWorkstationChip("Symbol", data.symbol || "Pending validation"),
    createWorkstationChip("Timeframe", data.timeframe || "Pending validation"),
    createWorkstationChip("Direction", data.direction || "Pending validation"),
    createWorkstationChip("Strategy", data.strategy_id || "Pending validation"),
    createWorkstationChip("Validation", data.validation_status || "Pending validation", data.validation_status),
    createWorkstationChip("Paper route", data.paper_route_status || "Pending validation", data.paper_route_status),
    createWorkstationChip("Paper result", data.paper_result_status || "Pending validation", data.paper_result_status),
    createWorkstationChip("Status output", data.visible_status_output || "Pending validation"),
    createWorkstationChip("Live execution", data.live_execution_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Broker", data.broker_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("OANDA", data.oanda_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("API keys", data.api_key_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real webhooks", data.real_webhook_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real orders", data.real_order_status || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Next", data.next_safe_action || "Keep all execution paths blocked.")
  ]);
}

function renderTradingLabWorkstation(data = {}) {
  const section = document.createElement("section");
  section.className = "trading-workstation";
  section.setAttribute("aria-label", "Trading Lab Workstation");

  const top = document.createElement("div");
  top.className = "trading-workstation-topbar";
  const topBar = data.top_bar || {};
  [
    ["Session", topBar.session],
    ["Pair", topBar.selected_pair],
    ["Market", topBar.market_state],
    ["Latency", topBar.latency_status || data.latency?.stale_status],
    ["Risk", topBar.risk_status],
    ["Mode", topBar.paper_mode],
    ["Validation", topBar.validation_state]
  ].forEach(([label, value]) => top.append(createWorkstationChip(label, value, value)));

  const left = data.left_panel || {};
  const center = data.center_panel || {};
  const right = data.right_panel || {};
  const bottom = data.bottom_panel || {};
  const latency = data.latency || {};
  const safety = data.safety || {};

  const leftPanel = createWorkstationPanel("Forex Desk", [
    createWorkstationList(left.watchlist || [], (item) => `Watchlist: ${item}`),
    createWorkstationList(left.forex_pairs || [], (item) => `${item.pair}: ${item.bias} / ${item.spread_status}`),
    createWorkstationList(left.session_tracker || [], (item) => `${item.session}: ${item.status}`),
    createWorkstationList(left.economic_events || [], (item) => `${item.time} - ${item.event} (${item.impact})`),
    createWorkstationList(left.alerts || [], (item) => `${item.label}: ${item.status}`),
    createWorkstationList(left.workspace_profiles || [], (item) => `Profile: ${item}`)
  ]);

  const centerPanel = createWorkstationPanel("Active Workflow", [
    createWorkstationChip("Workflow", center.active_workflow || "Pending validation"),
    createWorkstationChip("Signal", center.signal_intake?.status || "Pending validation"),
    createWorkstationChip("Direction", center.signal_intake?.direction || "Pending validation"),
    createWorkstationChip("Regime", center.market_context?.regime || "Pending validation"),
    createWorkstationList(center.paper_execution_flow || [], (item) => `${item.step}: ${item.status}`),
    createWorkstationChip("AI Guidance", center.ai_guidance_summary || "Pending validation"),
    createWorkstationChip("Next", center.primary_next_action || data.next_safe_action)
  ]);

  const rightPanel = createWorkstationPanel("Risk Gate", [
    createWorkstationChip("Gate", right.risk_gate?.status || "Pending validation", right.risk_gate?.status),
    createWorkstationChip("Risk", right.risk_gate?.max_risk_per_trade || "Not measured"),
    createWorkstationChip("Entry", right.position_model?.entry || "Pending validation"),
    createWorkstationChip("Stop", right.position_model?.stop || "Pending validation"),
    createWorkstationChip("Target", right.position_model?.target || "Pending validation"),
    createWorkstationChip("Confluence", right.confluence_score?.score || "Not measured"),
    createWorkstationList(right.setup_checklist || [], (item) => `Check: ${item}`),
    createWorkstationChip("Live execution", right.blocked_live_execution_state || safety.live_trading || "BLOCKED", "BLOCKED")
  ]);

  const body = document.createElement("div");
  body.className = "trading-workstation-body";
  body.append(leftPanel, centerPanel, rightPanel);

  const latencyPanel = createWorkstationPanel("Latency Core", [
    createWorkstationChip("Signal source", latency.signal_source_time || "Pending validation"),
    createWorkstationChip("Alert received", latency.alert_received_time || "Pending validation"),
    createWorkstationChip("Validation", `${latency.validation_start_time || "Pending"} -> ${latency.validation_end_time || "validation"}`),
    createWorkstationChip("AI review", `${latency.ai_review_start_time || "Parallel"} -> ${latency.ai_review_end_time || "not blocking"}`),
    createWorkstationChip("Route preview", latency.route_preview_time || "Pending validation"),
    createWorkstationChip("Paper execution", latency.paper_execution_time || "Pending validation"),
    createWorkstationChip("Total delay", latency.total_delay_seconds === null || latency.total_delay_seconds === undefined ? "Pending validation" : `${latency.total_delay_seconds}s`, latency.stale_status),
    createWorkstationChip("Stale status", latency.stale_status || "Pending validation", latency.stale_status),
    createWorkstationChip("Decision time", latency.user_decision_time_seconds === null || latency.user_decision_time_seconds === undefined ? "Not measured" : `${latency.user_decision_time_seconds}s`)
  ]);

  const bottomPanel = createWorkstationPanel("Journal / Replay / Scorecard", [
    createWorkstationChip("Journal", bottom.journal?.status || "Pending validation"),
    createWorkstationChip("Replay", bottom.replay?.status || "Pending validation"),
    createWorkstationChip("Scorecard", bottom.scorecard?.status || "Pending validation"),
    createWorkstationChip("Paper trades", bottom.paper_metrics?.paper_trades ?? "Not measured"),
    createWorkstationChip("Average latency", bottom.paper_metrics?.average_latency_seconds || "Not measured"),
    createWorkstationList(bottom.validation_log || [], (item) => `Log: ${item}`)
  ]);

  const safetyPanel = createWorkstationPanel("Safety Locks", [
    createWorkstationChip("Live trading", safety.live_trading || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Broker", safety.broker || "BLOCKED", "BLOCKED"),
    createWorkstationChip("OANDA", safety.oanda || "BLOCKED", "BLOCKED"),
    createWorkstationChip("API keys", safety.api_keys || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real webhooks", safety.real_webhooks || "BLOCKED", "BLOCKED"),
    createWorkstationChip("Real orders", safety.real_orders || "BLOCKED", "BLOCKED"),
    createWorkstationChip("AI execution", safety.ai_assisted_execution || "BLOCKED", "BLOCKED")
  ]);

  const bottomGrid = document.createElement("div");
  bottomGrid.className = "trading-workstation-bottom";
  bottomGrid.append(latencyPanel, bottomPanel, safetyPanel);

  section.append(top, body, bottomGrid);
  return section;
}

function createTradingLabCompactNextAction(data = {}, windowSystemData = null, orchestrationData = null) {
  const nextCard = Array.isArray(data.cards) ? data.cards.find((card) => card.id === "next_action" || card.title === "Next Action") : null;
  const windowNext = windowSystemData?.windows?.next_action?.summary || windowSystemData?.windows?.next_action?.detail;
  const actionText = orchestrationData?.next_safe_action || windowNext || nextCard?.next_action || "Review the paper-only route preview and keep execution blocked.";
  const action = document.createElement("div");
  action.className = "trading-lab-compact-next-action";

  const title = document.createElement("strong");
  title.textContent = "Next safe action";

  const text = document.createElement("p");
  text.textContent = actionText;

  action.append(title, text);
  return action;
}

function createTradingLabEntryButton() {
  const button = document.createElement("button");
  button.className = "trading-lab-entry-button";
  button.type = "button";
  button.textContent = "Continue Paper Route";
  button.addEventListener("click", () => {
    const details = tradingLabNextActionCard?.querySelector(".trading-lab-advanced-diagnostics");
    if (details) {
      details.open = true;
      details.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  });
  return button;
}

function createTradingLabCompactStatusRow(data = {}, workstationData = null, paperRunnerData = null) {
  const row = document.createElement("div");
  row.className = "trading-lab-compact-status-row";
  const topBar = workstationData?.top_bar || {};
  [
    ["Signal", topBar.validation_state || data.validation_state || "pending"],
    ["Latency", topBar.latency_status || paperRunnerData?.latency_status || "pending"],
    ["Risk", topBar.risk_status || "review required"],
    ["Scorecard", paperRunnerData?.scorecard_status || "not ready"]
  ].forEach(([label, value]) => row.append(createWorkstationChip(label, value, value)));
  return row;
}

function createTradingLabAdvancedDiagnostics(items = []) {
  const details = document.createElement("details");
  details.className = "trading-lab-advanced-diagnostics";

  const summary = document.createElement("summary");
  const title = document.createElement("strong");
  title.textContent = "Trading Lab Details";
  const badge = document.createElement("span");
  badge.textContent = "collapsed";
  const note = document.createElement("p");
  note.textContent = "Latency, safety locks, risk gate, diagnostics, replay, checklist, and paper-only validation details stay here until opened.";
  summary.append(title, badge, note);

  const body = document.createElement("div");
  body.className = "trading-lab-advanced-diagnostics-body";
  items.filter(Boolean).forEach((item) => body.append(item));

  details.append(summary, body);
  return details;
}

function createOperatorWorkbenchMetric(label, value, reason = "") {
  const item = document.createElement("div");
  item.className = "operator-workbench-metric";
  const key = document.createElement("span");
  key.textContent = label;
  const state = document.createElement("strong");
  state.textContent = value || "UNKNOWN";
  item.append(key, state);
  if (reason) {
    const note = document.createElement("small");
    note.textContent = reason;
    item.append(note);
  }
  return item;
}

function createOperatorWorkbenchList(title, items = [], valueKey = "state") {
  const panel = document.createElement("div");
  panel.className = "operator-workbench-panel";
  const heading = document.createElement("strong");
  heading.textContent = title;
  const list = document.createElement("ul");
  list.className = "operator-workbench-list";
  items.slice(0, 3).forEach((item) => {
    const row = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = item.label || item.step || item.pair || "State";
    const state = document.createElement("b");
    state.textContent = item[valueKey] || item.state || item.heat_state || "WATCH";
    row.append(label, state);
    if (item.reason) {
      const reason = document.createElement("small");
      reason.textContent = item.reason;
      row.append(reason);
    }
    list.append(row);
  });
  panel.append(heading, list);
  return panel;
}

function createInteractiveSurfaceDetails(title, data = {}, items = []) {
  const details = document.createElement("details");
  details.className = "interactive-surface";
  const summary = document.createElement("summary");
  const label = document.createElement("strong");
  label.textContent = title;
  const state = document.createElement("span");
  state.textContent = data.warning_state || data.confidence_state || data.edge_state || data.replay_state || "WATCH";
  summary.append(label, state);

  const reason = document.createElement("p");
  reason.textContent = data.interaction_reason || data.replay_scrubber_placeholder || "Paper-only interaction reveals depth without execution controls.";

  const list = document.createElement("ul");
  list.className = "operator-workbench-list";
  items.slice(0, 4).forEach((item) => {
    const row = document.createElement("li");
    const itemLabel = document.createElement("span");
    itemLabel.textContent = item.label || item.step || "Interaction";
    const itemState = document.createElement("b");
    itemState.textContent = item.state || "WATCH";
    row.append(itemLabel, itemState);
    if (item.reason) {
      const itemReason = document.createElement("small");
      itemReason.textContent = item.reason;
      row.append(itemReason);
    }
    list.append(row);
  });

  details.append(summary, reason, list);
  return details;
}

function renderInteractiveSurfaces(freezeData = {}, edgeDecayData = {}, survivabilityData = {}, replayScenariosData = {}, riskEscalationData = {}, nextSafeActionData = {}) {
  const section = document.createElement("section");
  section.className = "interactive-surfaces";
  section.setAttribute("aria-label", "Interactive intelligence surfaces");

  const head = document.createElement("div");
  head.className = "interactive-surfaces-head";
  const title = document.createElement("strong");
  title.textContent = "Interactive Intelligence Surfaces";
  const note = document.createElement("span");
  note.textContent = "Compact drilldowns only - no autoplay, broker controls, execution controls, or hidden live routing.";
  head.append(title, note);

  const grid = document.createElement("div");
  grid.className = "interactive-surfaces-grid";
  grid.append(
    createInteractiveSurfaceDetails("Confidence freeze timeline", freezeData, freezeData.events || []),
    createInteractiveSurfaceDetails("Edge decay inspection", edgeDecayData, edgeDecayData.decay_points || []),
    createInteractiveSurfaceDetails("Survivability timeline", survivabilityData, survivabilityData.timeline || []),
    createInteractiveSurfaceDetails("Replay scenario switching", replayScenariosData, replayScenariosData.scenarios || []),
    createInteractiveSurfaceDetails("Risk escalation playback", riskEscalationData, riskEscalationData.playback_steps || []),
    createInteractiveSurfaceDetails("Next Safe Action", nextSafeActionData, nextSafeActionData.next_safe_actions || [])
  );

  section.append(head, grid);
  return section;
}

function createGuidanceCard(title, data = {}) {
  const card = document.createElement("article");
  card.className = "operator-guidance-card";
  const head = document.createElement("div");
  const label = document.createElement("strong");
  label.textContent = title;
  const state = document.createElement("span");
  state.textContent = data.guidance_state || data.warning_state || "WATCH";
  head.append(label, state);
  const reason = document.createElement("p");
  reason.textContent = data.guidance_reason || data.next_safe_action || "Guidance remains paper-only and defensive.";
  const action = document.createElement("small");
  action.textContent = data.next_safe_action || "Maintain paper-only mode.";
  card.append(head, reason, action);
  return card;
}

function renderOperatorGuidance(guidanceData = {}, survivabilityGuidanceData = {}, confidenceGuidanceData = {}, riskReductionGuidanceData = {}, nextSafeActionGuidanceData = {}) {
  const section = document.createElement("section");
  section.className = "operator-guidance";
  section.setAttribute("aria-label", "Adaptive operator guidance");

  const head = document.createElement("div");
  head.className = "operator-guidance-head";
  const title = document.createElement("strong");
  title.textContent = guidanceData.panel_title || "Adaptive Operator Guidance";
  const note = document.createElement("span");
  note.textContent = "Guidance only - no execution urgency, broker controls, autonomous controls, or hidden live routing.";
  head.append(title, note);

  const strip = document.createElement("div");
  strip.className = "operator-guidance-strip";
  [
    guidanceData.guidance_state || "WATCH",
    confidenceGuidanceData.confidence_state || "CONFIDENCE_FROZEN",
    survivabilityGuidanceData.macro_state || "ELEVATED_RISK",
    riskReductionGuidanceData.portfolio_state || "WATCH"
  ].forEach((item) => {
    const chip = document.createElement("span");
    chip.textContent = item;
    strip.append(chip);
  });

  const grid = document.createElement("div");
  grid.className = "operator-guidance-grid";
  grid.append(
    createGuidanceCard("Survivability", survivabilityGuidanceData),
    createGuidanceCard("Confidence", confidenceGuidanceData),
    createGuidanceCard("Risk reduction", riskReductionGuidanceData),
    createGuidanceCard("Next Safe Action", nextSafeActionGuidanceData)
  );

  section.append(head, strip, grid);
  return section;
}

function renderOperatorWorkbench(workbenchData = {}, confidenceData = {}, portfolioData = {}, macroData = {}, chaosData = {}, replayData = {}, freezeData = {}, edgeDecayData = {}, survivabilityData = {}, replayScenariosData = {}, riskEscalationData = {}, nextSafeActionData = {}, guidanceData = {}, survivabilityGuidanceData = {}, confidenceGuidanceData = {}, riskReductionGuidanceData = {}, nextSafeActionGuidanceData = {}) {
  const section = document.createElement("section");
  section.className = "operator-workbench";
  section.setAttribute("aria-label", "AI_OS Trading Lab Operator Workbench");

  const head = document.createElement("div");
  head.className = "operator-workbench-head";
  const title = document.createElement("strong");
  title.textContent = workbenchData.panel_title || "AI_OS Operator Workbench";
  const note = document.createElement("span");
  note.textContent = workbenchData.next_safe_action || "Next Safe Action: continue paper review; live execution remains blocked.";
  head.append(title, note);

  const strip = document.createElement("div");
  strip.className = "operator-workbench-strip";
  (workbenchData.top_status_strip || ["Paper only", "Live blocked", "Broker blocked", "No execution controls"]).forEach((item) => {
    const chip = document.createElement("span");
    chip.textContent = item;
    strip.append(chip);
  });

  const grid = document.createElement("div");
  grid.className = "operator-workbench-grid";
  grid.append(
    createOperatorWorkbenchMetric("Confidence", confidenceData.confidence_state || "CONFIDENCE_FROZEN", confidenceData.events?.[confidenceData.events.length - 1]?.reason),
    createOperatorWorkbenchMetric("Edge", confidenceData.edge_state || chaosData.alerts?.[0]?.state || "WEAK_EDGE", "Edge survivability visibility"),
    createOperatorWorkbenchMetric("Macro", macroData.macro_state || "ELEVATED_RISK", macroData.overlay_items?.[0]?.reason),
    createOperatorWorkbenchMetric("Portfolio", portfolioData.portfolio_state || "WATCH", portfolioData.heat_panels?.[0]?.reason),
    createOperatorWorkbenchMetric("Replay", replayData.replay_state || "PARTIAL_SURVIVAL", replayData.replay_scrubber_placeholder),
    createOperatorWorkbenchMetric("Warning", chaosData.warning_state || "WATCH", chaosData.alerts?.[0]?.reason)
  );

  const panels = document.createElement("div");
  panels.className = "operator-workbench-panels";
  panels.append(
    createOperatorWorkbenchList("Confidence timeline", confidenceData.events || []),
    createOperatorWorkbenchList("Replay timeline", replayData.replay_timeline || []),
    createOperatorWorkbenchList("Portfolio heat", portfolioData.heat_panels || [], "heat_state"),
    createOperatorWorkbenchList("Macro-risk overlay", macroData.overlay_items || []),
    createOperatorWorkbenchList("Chaos alerts", chaosData.alerts || [])
  );

  const details = document.createElement("details");
  details.className = "operator-workbench-details";
  const summary = document.createElement("summary");
  summary.textContent = "Workbench details";
  const detailBody = document.createElement("p");
  detailBody.textContent = "Progressive disclosure keeps advanced workbench context collapsed by default. No autoplay, execution controls, broker controls, autonomous controls, or network order routing are present.";
  details.append(summary, detailBody);

  section.append(head, strip, grid, panels, renderInteractiveSurfaces(freezeData, edgeDecayData, survivabilityData, replayScenariosData, riskEscalationData, nextSafeActionData), renderOperatorGuidance(guidanceData, survivabilityGuidanceData, confidenceGuidanceData, riskReductionGuidanceData, nextSafeActionGuidanceData), details);
  return section;
}

function renderTradingLabNextActionData(data, paperBotCoreData = null, windowSystemData = null, paperRunnerData = null, orchestrationData = null, workstationData = null, phase28HandoffData = null, phase23NormalizationData = null, phase25LatencyData = null, paperTradingBotStatusData = null, operatorWorkbenchData = null, confidenceTimelineData = null, portfolioHeatData = null, macroOverlayData = null, chaosAlertsData = null, replayWorkbenchData = null, freezeTimelineData = null, edgeDecayVisibilityData = null, survivabilityTimelineData = null, replayScenariosData = null, riskEscalationData = null, nextSafeActionFlowData = null, operatorGuidanceData = null, survivabilityGuidanceData = null, confidenceGuidanceData = null, riskReductionGuidanceData = null, nextSafeActionGuidanceData = null) {
  if (!tradingLabNextActionCard) return;
  tradingLabNextActionCard.hidden = false;
  const title = document.createElement("section");
  title.className = "trading-lab-workspace-head";
  const heading = document.createElement("strong");
  heading.textContent = "Trading Lab / Bot Builder";
  title.append(heading);

  const safety = document.createElement("div");
  safety.className = "trading-lab-safety-row";
  safety.append(
    createTradingLabSafetyChip("Paper only", data.paper_mode || "ACTIVE"),
    createTradingLabSafetyChip("Live blocked", data.live_execution_status || "BLOCKED"),
    createTradingLabSafetyChip("Broker blocked", data.broker_status || "BLOCKED"),
    createTradingLabSafetyChip("Real orders blocked", "BLOCKED")
  );

  const cards = Array.isArray(data.cards) && data.cards.length ? data.cards : [];
  const flowGrid = document.createElement("div");
  flowGrid.className = "trading-lab-workspace-grid";
  cards.forEach((card, index) => {
    flowGrid.append(createTradingLabWorkspaceCard(card, index, cards.length));
  });

  const blockedActions = document.createElement("div");
  blockedActions.className = "trading-lab-blocked-actions";
  const blockedTitle = document.createElement("strong");
  blockedTitle.textContent = "Blocked actions";
  const blockedList = document.createElement("p");
  blockedList.textContent = (data.blocked_actions || data.blocked || [
    "No broker",
    "No OANDA",
    "No API keys",
    "No real orders",
    "No real webhooks",
    "No live execution"
  ]).join(" | ");
  blockedActions.append(blockedTitle, blockedList);

  const advancedItems = [];
  if (paperTradingBotStatusData) {
    advancedItems.push(renderPaperTradingBotStatus(paperTradingBotStatusData));
  }
  if (phase23NormalizationData) {
    advancedItems.push(renderPhase23PaperSignalNormalization(phase23NormalizationData));
  }
  if (phase25LatencyData) {
    advancedItems.push(renderPhase25LatencyMeasurementCore(phase25LatencyData));
  }
  const phase28Handoff = normalizePhase28PaperHandoff(phase28HandoffData);
  const handoffDetails = phase28Handoff
    ? renderExternalHandoffPanels(phase28Handoff)
    : windowSystemData?.handoff_path
      ? renderExternalHandoffPanels(windowSystemData.handoff_path)
      : renderTradingStackHub();
  if (handoffDetails) {
    advancedItems.push(handoffDetails);
  }
  if (flowGrid.childElementCount) {
    advancedItems.push(flowGrid);
  }
  if (paperRunnerData) {
    advancedItems.push(renderTradingLabPaperRunnerPanel(paperRunnerData));
  }
  if (orchestrationData) {
    advancedItems.push(renderAiosOrchestrationControlRoom(orchestrationData));
  }
  if (windowSystemData) {
    advancedItems.push(renderTradingLabWindowSystem(windowSystemData));
  }
  if (paperBotCoreData) {
    advancedItems.push(renderPaperBotCorePanel(paperBotCoreData));
  }
  advancedItems.push(blockedActions);

  const children = [
    title,
    safety,
    renderOperatorWorkbench(operatorWorkbenchData || {}, confidenceTimelineData || {}, portfolioHeatData || {}, macroOverlayData || {}, chaosAlertsData || {}, replayWorkbenchData || {}, freezeTimelineData || {}, edgeDecayVisibilityData || {}, survivabilityTimelineData || {}, replayScenariosData || {}, riskEscalationData || {}, nextSafeActionFlowData || {}, operatorGuidanceData || {}, survivabilityGuidanceData || {}, confidenceGuidanceData || {}, riskReductionGuidanceData || {}, nextSafeActionGuidanceData || {}),
    createTradingLabCompactNextAction(data, windowSystemData, orchestrationData),
    createTradingLabEntryButton(data, windowSystemData, orchestrationData),
    createTradingLabCompactStatusRow(data, workstationData, paperRunnerData)
  ];
  if (workstationData) {
    advancedItems.unshift(renderTradingLabWorkstation(workstationData));
  }
  if (advancedItems.length) {
    children.push(createTradingLabAdvancedDiagnostics(advancedItems));
  }
  tradingLabNextActionCard.replaceChildren(...children);
}

async function renderTradingLabNextActionCard() {
  if (!tradingLabNextActionCard) return;
  tradingLabNextActionCard.hidden = false;
  tradingLabNextActionCard.textContent = "Loading Trading Lab mock workspace...";
  try {
    const [response, paperBotResponse, windowSystemResponse, paperRunnerResponse, orchestrationResponse, workstationResponse, phase28HandoffResponse, phase23NormalizationResponse, phase25LatencyResponse, paperTradingBotStatusResponse, operatorWorkbenchResponse, confidenceTimelineResponse, portfolioHeatResponse, macroOverlayResponse, chaosAlertsResponse, replayWorkbenchResponse, freezeTimelineResponse, edgeDecayVisibilityResponse, survivabilityTimelineResponse, replayScenariosResponse, riskEscalationResponse, nextSafeActionFlowResponse, operatorGuidanceResponse, survivabilityGuidanceResponse, confidenceGuidanceResponse, riskReductionGuidanceResponse, nextSafeActionGuidanceResponse] = await Promise.all([
      fetch(tradingLabWorkspaceFixturePath, { cache: "no-store" }),
      fetch(paperBotCoreFixturePath, { cache: "no-store" }),
      fetch(tradingLabWindowSystemFixturePath, { cache: "no-store" }),
      fetch(tradingLabPaperRunnerFixturePath, { cache: "no-store" }),
      fetch(aiosOrchestrationControlRoomFixturePath, { cache: "no-store" }),
      fetch(tradingLabWorkstationFixturePath, { cache: "no-store" }),
      fetch(phase28TvTpPaperHandoffFixturePath, { cache: "no-store" }),
      fetch(phase23PaperSignalNormalizationFixturePath, { cache: "no-store" }),
      fetch(phase25LatencyMeasurementCoreFixturePath, { cache: "no-store" }),
      fetch(paperTradingBotStatusFixturePath, { cache: "no-store" }),
      fetch(aiosOperatorWorkbenchFixturePath, { cache: "no-store" }),
      fetch(aiosConfidenceTimelineFixturePath, { cache: "no-store" }),
      fetch(aiosPortfolioHeatFixturePath, { cache: "no-store" }),
      fetch(aiosMacroOverlayFixturePath, { cache: "no-store" }),
      fetch(aiosChaosAlertsFixturePath, { cache: "no-store" }),
      fetch(aiosReplayWorkbenchFixturePath, { cache: "no-store" }),
      fetch(aiosFreezeTimelineFixturePath, { cache: "no-store" }),
      fetch(aiosEdgeDecayVisibilityFixturePath, { cache: "no-store" }),
      fetch(aiosSurvivabilityTimelineFixturePath, { cache: "no-store" }),
      fetch(aiosReplayScenariosFixturePath, { cache: "no-store" }),
      fetch(aiosRiskEscalationFixturePath, { cache: "no-store" }),
      fetch(aiosNextSafeActionFlowFixturePath, { cache: "no-store" }),
      fetch(aiosOperatorGuidanceFixturePath, { cache: "no-store" }),
      fetch(aiosSurvivabilityGuidanceFixturePath, { cache: "no-store" }),
      fetch(aiosConfidenceGuidanceFixturePath, { cache: "no-store" }),
      fetch(aiosRiskReductionGuidanceFixturePath, { cache: "no-store" }),
      fetch(aiosNextSafeActionGuidanceFixturePath, { cache: "no-store" })
    ]);
    if (!response.ok) throw new Error("Trading Lab fixture unavailable");
    const paperBotCoreData = paperBotResponse.ok ? await paperBotResponse.json() : null;
    const windowSystemData = windowSystemResponse.ok ? await windowSystemResponse.json() : null;
    const paperRunnerData = paperRunnerResponse.ok ? await paperRunnerResponse.json() : null;
    const orchestrationData = orchestrationResponse.ok ? await orchestrationResponse.json() : null;
    const workstationData = workstationResponse.ok ? await workstationResponse.json() : null;
    const phase28HandoffData = phase28HandoffResponse.ok ? await phase28HandoffResponse.json() : null;
    const phase23NormalizationData = phase23NormalizationResponse.ok ? await phase23NormalizationResponse.json() : null;
    const phase25LatencyData = phase25LatencyResponse.ok ? await phase25LatencyResponse.json() : null;
    const paperTradingBotStatusData = paperTradingBotStatusResponse.ok ? await paperTradingBotStatusResponse.json() : null;
    const operatorWorkbenchData = operatorWorkbenchResponse.ok ? await operatorWorkbenchResponse.json() : null;
    const confidenceTimelineData = confidenceTimelineResponse.ok ? await confidenceTimelineResponse.json() : null;
    const portfolioHeatData = portfolioHeatResponse.ok ? await portfolioHeatResponse.json() : null;
    const macroOverlayData = macroOverlayResponse.ok ? await macroOverlayResponse.json() : null;
    const chaosAlertsData = chaosAlertsResponse.ok ? await chaosAlertsResponse.json() : null;
    const replayWorkbenchData = replayWorkbenchResponse.ok ? await replayWorkbenchResponse.json() : null;
    const freezeTimelineData = freezeTimelineResponse.ok ? await freezeTimelineResponse.json() : null;
    const edgeDecayVisibilityData = edgeDecayVisibilityResponse.ok ? await edgeDecayVisibilityResponse.json() : null;
    const survivabilityTimelineData = survivabilityTimelineResponse.ok ? await survivabilityTimelineResponse.json() : null;
    const replayScenariosData = replayScenariosResponse.ok ? await replayScenariosResponse.json() : null;
    const riskEscalationData = riskEscalationResponse.ok ? await riskEscalationResponse.json() : null;
    const nextSafeActionFlowData = nextSafeActionFlowResponse.ok ? await nextSafeActionFlowResponse.json() : null;
    const operatorGuidanceData = operatorGuidanceResponse.ok ? await operatorGuidanceResponse.json() : null;
    const survivabilityGuidanceData = survivabilityGuidanceResponse.ok ? await survivabilityGuidanceResponse.json() : null;
    const confidenceGuidanceData = confidenceGuidanceResponse.ok ? await confidenceGuidanceResponse.json() : null;
    const riskReductionGuidanceData = riskReductionGuidanceResponse.ok ? await riskReductionGuidanceResponse.json() : null;
    const nextSafeActionGuidanceData = nextSafeActionGuidanceResponse.ok ? await nextSafeActionGuidanceResponse.json() : null;
    renderTradingLabNextActionData(await response.json(), paperBotCoreData, windowSystemData, paperRunnerData, orchestrationData, workstationData, phase28HandoffData, phase23NormalizationData, phase25LatencyData, paperTradingBotStatusData, operatorWorkbenchData, confidenceTimelineData, portfolioHeatData, macroOverlayData, chaosAlertsData, replayWorkbenchData, freezeTimelineData, edgeDecayVisibilityData, survivabilityTimelineData, replayScenariosData, riskEscalationData, nextSafeActionFlowData, operatorGuidanceData, survivabilityGuidanceData, confidenceGuidanceData, riskReductionGuidanceData, nextSafeActionGuidanceData);
  } catch {
    renderTradingLabNextActionData({
      title: "Trading Lab Workspace",
      badge: "MOCK ONLY",
      mode: "ACTIVE",
      paper_mode: "ACTIVE",
      live_execution_status: "BLOCKED",
      broker_status: "BLOCKED",
      summary: "Paper-only trading workflow using mock data. No broker or live execution path is active.",
      cards: [
        { title: "Signal Intake", status: "MOCK READY", meaning: "A sample signal can be reviewed without sending orders.", next_action: "Check mock signal fields." },
        { title: "Latency", status: "REVIEW", meaning: "Timing is tracked as a mock value only.", next_action: "Confirm timestamp labels are clear." },
        { title: "Regime", status: "PENDING REVIEW", meaning: "Regime means the current market condition tag.", next_action: "Keep tag paper-only." },
        { title: "Risk Gate", status: "BLOCKED", meaning: "The safety gate blocks live action.", next_action: "Do not weaken the lock." },
        { title: "Paper Result", status: "NOT EXECUTED", meaning: "No real or paper trade has been run from the dashboard.", next_action: "Use mock result only." },
        { title: "Scorecard", status: "WAITING", meaning: "Win/loss notes are not proven yet.", next_action: "Require enough mock samples." },
        { title: "Validator Status", status: "REVIEW", meaning: "Checks must pass before any future change package.", next_action: "Run local validators after edits." },
        { title: "Next Action", status: "START HERE", meaning: "Review one mock signal through the risk gate.", next_action: "Keep Live Execution: BLOCKED." }
      ],
      blocked_actions: [
        "No broker",
        "No OANDA",
        "No API keys",
        "No real orders",
        "No real webhooks",
        "No live execution"
      ]
    });
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
    const progress = createProgressBadge("Completion", project, "Not measured");
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
    card.append(title, progress, summary, sections, telemetry);
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
  noticeTitle.textContent = "Connector-locked apps";
  const noticeBody = document.createElement("span");
  noticeBody.textContent = "Launch and connector planning only. No credentials, OAuth, API calls, OneDrive access keys, social access keys, or persistence are enabled.";
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
  if (activeAssistantMode === "trading-lab") {
    renderTradingLabNextActionCard();
  } else if (activeDetailItemId !== "trading-bot") {
    hideTradingLabNextActionCard();
  }
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
    "Safety rules": "Local mock-only. Do not store secrets, credentials, API keys, broker keys, social access keys, OneDrive access keys, approvals, or execution state.",
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
  } catch {
    personalGalleryPanel.replaceChildren(
      createPersonalGalleryNotice(),
      createPersonalGalleryEmpty("Local gallery manifest not found. Add images to private-media/service-gallery and create gallery.local.json.")
    );
  }
}

function readCommandCenterState() {
  try {
    const parsed = JSON.parse(window.sessionStorage.getItem(dashboardWorkspaceStateKey) || "{}");
    if (!parsed || typeof parsed !== "object") return null;
    if (railDetailConfig[parsed.rail]) {
      const hasRailDetail = railDetailConfig[parsed.rail].items.some((item) => item.id === parsed.detail);
      if (!hasRailDetail) return null;
      return {
        rail: parsed.rail,
        workspace: parsed.rail,
        detail: parsed.detail
      };
    }
    if (!parsed.workspace) return null;
    const legacyTarget = resolveRailTarget(parsed.workspace, parsed.detail);
    const hasDetail = railDetailConfig[legacyTarget.rail].items.some((item) => item.id === legacyTarget.detail);
    if (!hasDetail) return null;
    return {
      rail: legacyTarget.rail,
      workspace: legacyTarget.rail,
      detail: legacyTarget.detail
    };
  } catch {
    return null;
  }
}

function saveCommandCenterState() {
  try {
    if (isWelcomeStartVisible()) {
      window.sessionStorage.removeItem(dashboardWorkspaceStateKey);
      return;
    }
    window.sessionStorage.setItem(dashboardWorkspaceStateKey, JSON.stringify({
      rail: activeWorkspaceId,
      workspace: activeWorkspaceId,
      detail: activeDetailItemId
    }));
  } catch {
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

async function loadJsonFixture(path, fallback) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      return { ...fallback, status: "UNKNOWN", source: path };
    }
    const data = await response.json();
    return { data, source: path };
  } catch {
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
  } catch {
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
  } catch {
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
      button.setAttribute("aria-label", `${label} Dock Player`);
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
      button.setAttribute("aria-label", `${label} Dock Player`);
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
  } catch {
    // YouTube state can be unavailable during player startup.
  }
}

function setYouTubeDockCollapsed(isCollapsed) {
  if (!youtubeRadioDock) return;
  youtubeRadioDock.classList.toggle("is-collapsed", isCollapsed);
  const expandButton = youtubeRadioDock.querySelector('[data-youtube-radio-control="expand"]');
  if (expandButton) {
    const label = isCollapsed ? "Expand Dock Player" : "Minimize Dock Player";
    const readableState = expandButton.querySelector("[data-youtube-radio-readable-state]");
    expandButton.classList.toggle("is-expanded", !isCollapsed);
    expandButton.setAttribute("aria-label", label);
    expandButton.setAttribute("title", isCollapsed ? "Expand" : "Minimize");
    if (readableState) readableState.textContent = isCollapsed ? "Expand" : "Minimize";
  }
}

function readSavedYouTubeDockCollapsed() {
  try {
    const value = window.localStorage.getItem(youtubeDockCollapsedKey);
    if (value === "true") return true;
    if (value === "false") return false;
    return false;
  } catch {
    return false;
  }
}

function saveYouTubeDockCollapsed(isCollapsed) {
  try {
    window.localStorage.setItem(youtubeDockCollapsedKey, String(isCollapsed));
  } catch {
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
  } catch {
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
  } catch {
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
  } catch {
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
  } catch {
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
  } catch {
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
  } catch {
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
        setYouTubeRadioState("Embed unavailable inside AI_OS.");
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

  if (action === "expand") {
    const isCollapsed = !youtubeRadioDock.classList.contains("is-collapsed");
    setYouTubeDockCollapsed(isCollapsed);
    saveYouTubeDockCollapsed(isCollapsed);
    saveYouTubeRadioState();
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
  } catch {
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
    } catch {
      // Use the current slider value when the YouTube player is not ready.
    }
  }
  return Math.max(0, Math.min(100, currentVolume + delta));
}

function runDashboardMusicShortcut(command, value) {
  if (command === "volume") {
    const volume = Math.max(0, Math.min(100, Number(value) || 0));
    handleYouTubeRadioVolume(volume);
    return;
  }
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
  } catch {
    return null;
  }
}

function saveDrawerClosed(isClosed) {
  try {
    window.sessionStorage.setItem(drawerStateKey, String(isClosed));
  } catch {
    // The drawer still works without persisted UI state.
  }
}

function readSavedPersonalRailClosed() {
  try {
    const value = window.sessionStorage.getItem(personalRailStateKey);
    if (value === "true") return true;
    if (value === "false") return false;
    return null;
  } catch {
    return null;
  }
}

function savePersonalRailClosed(isClosed) {
  try {
    window.sessionStorage.setItem(personalRailStateKey, String(isClosed));
  } catch {
    // The rail still works without persisted UI state.
  }
}

function readSavedDashboardTheme() {
  try {
    return window.localStorage.getItem(dashboardThemeKey) || "default";
  } catch {
    return "default";
  }
}

function saveDashboardTheme(themeName) {
  try {
    window.localStorage.setItem(dashboardThemeKey, themeName);
  } catch {
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
  syncMobileRailScrollLock();
}

function syncSidebarState() {
  const isMobile = mobileSidebarQuery.matches;
  const isOpen = document.body.classList.contains("sidebar-open");
  const isCollapsed = document.body.classList.contains("sidebar-collapsed");
  const expanded = isMobile ? isOpen : !isCollapsed;
  const workOpenerLabel = "Work";
  const workOpenerAria = expanded ? "Toggle Work" : "Open Work";
  sidebarToggle.setAttribute("aria-expanded", String(expanded));
  sidebarToggle.setAttribute("aria-label", expanded ? "Close Work" : "Open Work");
  sidebarToggle.textContent = expanded ? "Close Work" : "Work";
  drawerReopen.setAttribute("aria-expanded", String(expanded));
  drawerReopen.setAttribute("aria-label", workOpenerAria);
  const drawerReopenLabel = drawerReopen.querySelector("span");
  if (drawerReopenLabel) {
    drawerReopenLabel.textContent = workOpenerLabel;
  } else {
    drawerReopen.textContent = workOpenerLabel;
  }
}

function isMobileRailOpen() {
  return mobileSidebarQuery.matches && (
    document.body.classList.contains("sidebar-open") ||
    document.body.classList.contains("personal-rail-open")
  );
}

function getActiveMobileRail() {
  if (!mobileSidebarQuery.matches) return null;
  if (document.body.classList.contains("sidebar-open")) {
    return document.querySelector(".command-sidebar");
  }
  if (document.body.classList.contains("personal-rail-open")) {
    return document.querySelector(".personal-sidebar");
  }
  return null;
}

function getActiveMobileRailScrollTarget() {
  const activeRail = getActiveMobileRail();
  if (!activeRail) return null;
  const preferredList = activeRail.querySelector(".context-rail-list, .personal-rail-list");
  if (preferredList && preferredList.scrollHeight > preferredList.clientHeight) {
    return preferredList;
  }
  return activeRail;
}

function getMobileRailScrollableTarget(target) {
  const activeRail = getActiveMobileRail();
  if (!activeRail || !target) return null;
  const startElement = target.nodeType === Node.ELEMENT_NODE ? target : target.parentElement;
  let current = startElement;
  while (current && current !== document.body) {
    if (activeRail.contains(current)) {
      const style = window.getComputedStyle(current);
      const canScrollY = /(auto|scroll)/.test(style.overflowY) && current.scrollHeight > current.clientHeight;
      if (canScrollY) return current;
    }
    if (current === activeRail) break;
    current = current.parentElement;
  }
  return activeRail.scrollHeight > activeRail.clientHeight ? activeRail : null;
}

function isInsideActiveMobileRail(target) {
  const activeRail = getActiveMobileRail();
  if (!activeRail || !target) return false;
  return activeRail.contains(target);
}

function stopMobileRailScrollEvent(event) {
  event.stopPropagation();
  if (typeof event.stopImmediatePropagation === "function") {
    event.stopImmediatePropagation();
  }
}

function blockMobileRailScrollEvent(event) {
  event.preventDefault();
  stopMobileRailScrollEvent(event);
}

function _scrollActiveMobileRail(deltaY) {
  const scrollTarget = getActiveMobileRailScrollTarget();
  if (!scrollTarget || !Number.isFinite(deltaY)) return;
  scrollTarget.scrollTop += deltaY;
}

function isMobileRailScrollBleed(scrollTarget, deltaY) {
  if (!scrollTarget || !Number.isFinite(deltaY)) return true;
  if (scrollTarget.scrollHeight <= scrollTarget.clientHeight) return true;
  const scrollTop = scrollTarget.scrollTop;
  const maxScrollTop = scrollTarget.scrollHeight - scrollTarget.clientHeight;
  const atTop = scrollTop <= 0;
  const atBottom = scrollTop >= maxScrollTop - 1;
  return (atTop && deltaY < 0) || (atBottom && deltaY > 0);
}

function setMobileRailFixedBodyLock(isLocked) {
  if (isLocked && !mobileRailScrollLockActive) {
    mobileRailScrollLockY = window.scrollY || document.documentElement.scrollTop || 0;
    document.body.style.position = "fixed";
    document.body.style.top = `-${mobileRailScrollLockY}px`;
    document.body.style.left = "0";
    document.body.style.right = "0";
    document.body.style.width = "100%";
    mobileRailScrollLockActive = true;
    return;
  }

  if (!isLocked && mobileRailScrollLockActive) {
    document.body.style.position = "";
    document.body.style.top = "";
    document.body.style.left = "";
    document.body.style.right = "";
    document.body.style.width = "";
    window.scrollTo(0, mobileRailScrollLockY);
    mobileRailScrollLockY = 0;
    mobileRailScrollLockActive = false;
    mobileRailLastTouchY = null;
    mobileRailTouchStartX = null;
    mobileRailTouchStartY = null;
  }
}

function syncMobileRailScrollLock() {
  const shouldLock = isMobileRailOpen();
  document.documentElement.classList.toggle("mobile-rail-scroll-locked", shouldLock);
  document.body.classList.toggle("mobile-rail-scroll-locked", shouldLock);
  if (dashboardShell) {
    dashboardShell.classList.toggle("mobile-rail-scroll-locked", shouldLock);
  }
  if (commandMain) {
    commandMain.classList.toggle("mobile-rail-scroll-locked", shouldLock);
  }
  setMobileRailFixedBodyLock(shouldLock);
}

function focusMainWorkspace() {
  if (!commandMain) return;
  if (!commandMain.hasAttribute("tabindex")) {
    commandMain.setAttribute("tabindex", "-1");
  }
  commandMain.focus({ preventScroll: true });
}

function closeSidebar() {
  document.body.classList.remove("sidebar-open");
  if (!mobileSidebarQuery.matches) {
    document.body.classList.add("sidebar-collapsed");
  }
  saveDrawerClosed(true);
  syncSidebarState();
  syncMobileRailScrollLock();
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
  syncMobileRailScrollLock();
}

function closeMobileSidebar() {
  closeSidebar();
  if (mobileSidebarQuery.matches) {
    document.body.classList.remove("personal-rail-open");
    document.body.classList.add("personal-rail-collapsed");
    savePersonalRailClosed(true);
    syncPersonalRailState();
    syncMobileRailScrollLock();
    focusMainWorkspace();
  }
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
  syncMobileRailScrollLock();
}

function applySavedPersonalRailState() {
  const savedClosed = readSavedPersonalRailClosed();
  document.body.classList.remove("personal-rail-open");
  document.body.classList.toggle("personal-rail-collapsed", savedClosed === true || mobileSidebarQuery.matches);
  syncMobileRailScrollLock();
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
    const personalLabel = isInternalToggle ? "Close Personal" : "Personal";
    button.setAttribute("aria-label", isInternalToggle ? "Close Personal" : (expanded ? "Toggle Personal" : "Open Personal"));
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
  syncMobileRailScrollLock();
}

function closeActiveMobileRailAfterSelection() {
  if (!mobileSidebarQuery.matches) return;
  closeActiveMobileRail();
}

function closeActiveMobileRail() {
  if (!mobileSidebarQuery.matches) return;
  document.body.classList.remove("sidebar-open");
  document.body.classList.remove("personal-rail-open");
  document.body.classList.add("sidebar-collapsed");
  document.body.classList.add("personal-rail-collapsed");
  saveDrawerClosed(true);
  savePersonalRailClosed(true);
  syncSidebarState();
  syncPersonalRailState();
  syncMobileRailScrollLock();
  focusMainWorkspace();
}

function handleMobileRailOutsidePointer(event) {
  if (!isMobileRailOpen()) return;
  if (isInsideActiveMobileRail(event.target)) return;
  if (event.target?.closest?.(".drawer-reopen, .personal-rail-toggle, .rail-internal-toggle, .rail-toggle-button, .sidebar-toggle")) return;
  closeActiveMobileRail();
}

function handleMobileRailListSelection(event) {
  if (!mobileSidebarQuery.matches) return;
  const railList = event.currentTarget;
  const selectedButton = event.target?.closest?.("button");
  if (!selectedButton || !railList.contains(selectedButton)) return;
  if (selectedButton.matches(".rail-internal-toggle, .rail-toggle-button, .sidebar-toggle, .personal-rail-close")) return;
  window.setTimeout(closeActiveMobileRailAfterSelection, 0);
}

function containMobileRailTouch(event) {
  if (!isMobileRailOpen()) return;
  if (isInsideActiveMobileRail(event.target)) {
    const currentTouchX = event.touches?.[0]?.clientX;
    const currentTouchY = event.touches?.[0]?.clientY;
    const deltaY = typeof currentTouchY === "number" && typeof mobileRailLastTouchY === "number"
      ? mobileRailLastTouchY - currentTouchY
      : 0;
    const driftX = typeof currentTouchX === "number" && typeof mobileRailTouchStartX === "number"
      ? Math.abs(currentTouchX - mobileRailTouchStartX)
      : 0;
    const driftY = typeof currentTouchY === "number" && typeof mobileRailTouchStartY === "number"
      ? Math.abs(currentTouchY - mobileRailTouchStartY)
      : 0;

    if (driftX > 10 && driftX > driftY) {
      if (typeof currentTouchY === "number") {
        mobileRailLastTouchY = currentTouchY;
      }
      blockMobileRailScrollEvent(event);
      return;
    }

    const scrollTarget = getMobileRailScrollableTarget(event.target);
    if (isMobileRailScrollBleed(scrollTarget, deltaY)) {
      if (typeof currentTouchY === "number") {
        mobileRailLastTouchY = currentTouchY;
      }
      blockMobileRailScrollEvent(event);
      return;
    }

    if (typeof currentTouchY === "number") {
      mobileRailLastTouchY = currentTouchY;
    }
    stopMobileRailScrollEvent(event);
    return;
  }
  mobileRailLastTouchY = null;
  mobileRailTouchStartX = null;
  mobileRailTouchStartY = null;
  blockMobileRailScrollEvent(event);
}

function containMobileRailWheel(event) {
  if (!isMobileRailOpen()) return;
  if (isInsideActiveMobileRail(event.target)) {
    const scrollTarget = getMobileRailScrollableTarget(event.target);
    if (isMobileRailScrollBleed(scrollTarget, event.deltaY || 0)) {
      blockMobileRailScrollEvent(event);
      return;
    }
    stopMobileRailScrollEvent(event);
    return;
  }
  blockMobileRailScrollEvent(event);
}

function trackMobileRailTouchStart(event) {
  if (!isMobileRailOpen() || !isInsideActiveMobileRail(event.target)) {
    mobileRailLastTouchY = null;
    mobileRailTouchStartX = null;
    mobileRailTouchStartY = null;
    return;
  }
  const touchX = event.touches?.[0]?.clientX;
  const touchY = event.touches?.[0]?.clientY;
  mobileRailTouchStartX = typeof touchX === "number" ? touchX : null;
  mobileRailTouchStartY = typeof touchY === "number" ? touchY : null;
  mobileRailLastTouchY = typeof touchY === "number" ? touchY : null;
  stopMobileRailScrollEvent(event);
}
tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    hideWelcomeStart();
    clearFocusedStartView();
    const target = button.dataset.tab;
    setActiveTab(target);
  });
});

statusPanelButtons.forEach((button) => {
  button.addEventListener("click", () => {
    hideWelcomeStart();
    clearFocusedStartView();
    showStatusPanel(button.dataset.statusPanelButton);
  });
});

welcomeActionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    routeWelcomeAction(button.dataset.welcomeAction);
  });
});

actionButtons.forEach((item) => {
  item.addEventListener("click", () => {
    const action = item.dataset.action;
    if (action === "soft-refresh") {
      runSoftRefresh();
      return;
    }
    if (action === "toggle-personal-rail") {
      hideWelcomeStart();
      clearFocusedStartView();
      togglePersonalRail();
      return;
    }
    if (action === "home-start") {
      routeWelcomeAction("start-here");
      return;
    }
    if (item.dataset.tab) {
      actionButtons.forEach((target) => {
        if (target.dataset.tab) {
          target.classList.toggle("active", target === item);
        }
      });
      hideWelcomeStart();
      clearFocusedStartView();
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
  hideWelcomeStart();
  clearFocusedStartView();
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

document.addEventListener("pointerdown", handleMobileRailOutsidePointer, { capture: true });
document.addEventListener("touchstart", trackMobileRailTouchStart, { passive: false, capture: true });
document.addEventListener("touchmove", containMobileRailTouch, { passive: false, capture: true });
document.addEventListener("wheel", containMobileRailWheel, { passive: false, capture: true });
contextRailList?.addEventListener("click", handleMobileRailListSelection);
personalRailList?.addEventListener("click", handleMobileRailListSelection);

applyDashboardTheme(readSavedDashboardTheme());
renderRailSelection("build", "start-here");
showWelcomeStart();
youtubeRadioRestoreState = readSavedYouTubeRadioState();
setYouTubeDockCollapsed(youtubeRadioRestoreState?.collapsed ?? true);
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

window.setInterval(() => {
  if (activeWorkspaceId === "trading-bot" && !isWelcomeStartVisible()) {
    renderTradingLabNextActionCard();
  }
}, 15000);

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
  if (isMobileRailOpen()) return;
  const x = (event.clientX / window.innerWidth - 0.5).toFixed(3);
  const y = (event.clientY / window.innerHeight - 0.5).toFixed(3);
  document.documentElement.style.setProperty("--mx", x);
  document.documentElement.style.setProperty("--my", y);
});

window.addEventListener("scroll", () => {
  if (isMobileRailOpen()) return;
  const ratio = Math.min(window.scrollY / 700, 1).toFixed(3);
  document.documentElement.style.setProperty("--scroll", ratio);
}, { passive: true });

