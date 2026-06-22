import { useCallback, useMemo, useState } from "react";
import operatorStatusFixture from "../mock-data/aios-operator-status-v1.example.json";
import mockRuntimeVisibility from "../mock-data/aios-runtime-visibility-v1.example.json";
import { autonomyBridgeStatePayload } from "virtual:aios-autonomy-bridge-state";
import {
  RUNTIME_VISIBILITY_SOURCE_LABELS,
  mapRuntimeVisibilityDisplayModel
} from "./runtimeVisibilityAdapter";
import {
  fetchRuntimeVisibilityReadOnly,
  getRuntimeVisibilityClientConfig
} from "./runtimeVisibilityClient";
import AIOSLiveOperatorPanel from "./AIOSLiveOperatorPanel";
import "./App.css";

const CLASSIFICATION = Object.freeze({
  READ_ONLY: "READ_ONLY",
  REQUEST: "REQUEST",
  PROTECTED: "PROTECTED",
  FORBIDDEN: "FORBIDDEN"
});

const LIVE_TRADING_ALLOWED = false;
const MUTATION_ALLOWED = false;
const EXECUTION_ALLOWED = false;

const mockVisibilityDisplay = mapRuntimeVisibilityDisplayModel(mockRuntimeVisibility, {
  sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA
});

const autonomyBridgeState = autonomyBridgeStatePayload.data ?? {};

const safeButtons = [
  {
    id: "status",
    label: "Refresh Status",
    type: "READ_ONLY",
    panel: "status",
    summary: "Refreshes the existing read-only runtime visibility source."
  },
  {
    id: "next-safe-action",
    label: "Show Next Safe Action",
    type: "READ_ONLY",
    panel: "nextSafeAction",
    summary: "Displays the next safe action from current evidence."
  },
  {
    id: "countdown",
    label: "Show Countdown",
    type: "READ_ONLY",
    panel: "countdown",
    summary: "Shows Live Countdown progress without changing state."
  },
  {
    id: "trading-readiness",
    label: "Show Trading Readiness",
    type: "READ_ONLY",
    panel: "trading",
    summary: "Displays trading gates as paper-only and locked."
  },
  {
    id: "evidence",
    label: "Show Dashboard Evidence",
    type: "READ_ONLY",
    panel: "evidence",
    summary: "Shows source labels, freshness, and display-only evidence."
  },
  {
    id: "blockers",
    label: "Show Blockers",
    type: "READ_ONLY",
    panel: "blockers",
    summary: "Lists blocked actions and unsafe boundaries."
  },
  {
    id: "approval",
    label: "View Approval Required",
    type: "READ_ONLY",
    panel: "approval",
    summary: "Shows protected actions that require Human Owner approval."
  },
  {
    id: "kill-switch",
    label: "View Kill Switch State",
    type: "READ_ONLY",
    panel: "killSwitch",
    summary: "Displays kill switch visibility without exposing control authority."
  },
  {
    id: "risk-gate",
    label: "View Risk Gate State",
    type: "READ_ONLY",
    panel: "riskGate",
    summary: "Displays the risk gate as evidence-only until stronger proof is supplied."
  }
];

const requestButtons = [
  {
    id: "work-request",
    label: "Create Work Request",
    prompt: "Create a governed AIOS work request preview."
  },
  {
    id: "packet-draft",
    label: "Draft Packet",
    prompt: "Draft a non-executable packet preview for human review."
  }
];

const protectedActions = [
  {
    id: "arm-live-mode",
    label: "Arm Live Mode",
    state: "LOCKED",
    reason: "Live mode requires a separate approved boundary-change packet."
  },
  {
    id: "approve-apply",
    label: "Approve APPLY",
    state: "APPROVAL_REQUIRED",
    reason: "Approval remains Human Owner authority and is not mutated here."
  },
  {
    id: "broker-sandbox",
    label: "Trigger Broker Sandbox",
    state: "LOCKED",
    reason: "Broker sandbox action is not wired from the frontend."
  },
  {
    id: "start-runtime",
    label: "Start Runtime",
    state: "LOCKED",
    reason: "Runtime controls require backend policy and approval gates."
  },
  {
    id: "stop-runtime",
    label: "Stop Runtime",
    state: "LOCKED",
    reason: "Stop controls are displayed as protected, not executed."
  },
  {
    id: "execute-live-micro-trade",
    label: "Execute Live Micro-Trade",
    state: "LOCKED",
    reason: "Live trade execution remains blocked."
  }
];

const tradingReadiness = [
  { label: "Paper proof", state: "NEEDS_REVIEW" },
  { label: "Risk governor", state: "NEEDS_REVIEW" },
  { label: "Daily loss", state: "NEEDS_REVIEW" },
  { label: "Kill switch", state: "VISIBLE_LOCKED" },
  { label: "Broker sandbox/demo", state: "LOCKED" },
  { label: "Live arm", state: "LOCKED" },
  { label: "Human approval", state: "REQUIRED" },
  { label: "Live trade allowed", state: "FALSE" }
];

const forbiddenRequestPatterns = [
  /place\s+.*live\s+trade/i,
  /disable\s+.*risk/i,
  /disable\s+.*kill/i,
  /bypass\s+approval/i,
  /broker\s+key/i,
  /credential/i,
  /secret/i,
  /force\s+merge/i,
  /force\s+push/i,
  /shell/i,
  /raw\s+.*command/i,
  /execute\s+.*raw/i
];

const protectedRequestPatterns = [
  /arm\s+live/i,
  /live\s+mode/i,
  /live\s+micro/i,
  /approve/i,
  /\bapply\b/i,
  /broker\s+sandbox/i,
  /start\s+runtime/i,
  /stop\s+runtime/i,
  /worker\s+launch/i,
  /scheduler/i,
  /\bcommit\b/i,
  /\bpush\b/i,
  /\bmerge\b/i,
  /\bdeploy/i
];

const readOnlyRequestPatterns = [
  /\bshow\b/i,
  /\bview\b/i,
  /\binspect\b/i,
  /\bstatus\b/i,
  /readiness/i,
  /evidence/i,
  /blocker/i,
  /next\s+safe/i,
  /countdown/i,
  /kill\s+switch/i,
  /risk\s+gate/i
];

function asNumber(value, fallback = 0) {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) ? numberValue : fallback;
}

function formatTime(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  }).format(new Date(value));
}

function normalizeStatus(value) {
  const normalized = String(value ?? "UNKNOWN").toUpperCase();

  if (["READY", "PASS", "CLEAR", "GREEN", "HEALTHY"].includes(normalized)) {
    return "READY";
  }

  if (["BLOCKED", "FAIL", "CRITICAL", "DEGRADED"].includes(normalized)) {
    return "BLOCKED";
  }

  if (["STALE", "REVIEW", "NEEDS_APPROVAL", "APPROVAL_REQUIRED"].includes(normalized)) {
    return "NEEDS_REVIEW";
  }

  return normalized || "UNKNOWN";
}

function statusTone(value) {
  const normalized = String(value ?? "UNKNOWN").toUpperCase();

  if (normalized.includes("BLOCKED") || normalized.includes("FAIL") || normalized.includes("FALSE")) {
    return "danger";
  }

  if (
    normalized.includes("REVIEW") ||
    normalized.includes("REQUIRED") ||
    normalized.includes("LOCKED") ||
    normalized.includes("STALE") ||
    normalized.includes("UNKNOWN")
  ) {
    return "warn";
  }

  if (
    normalized.includes("READY") ||
    normalized.includes("PASS") ||
    normalized.includes("VISIBLE") ||
    normalized.includes("READ_ONLY")
  ) {
    return "good";
  }

  return "neutral";
}

function countBlockingSignals(runtimeVisibility) {
  const blockedPackets = asNumber(runtimeVisibility.executionLedger.blockedPacketCount);
  const poisonPackets = asNumber(runtimeVisibility.health.poisonPackets);
  const retryablePackets = asNumber(runtimeVisibility.health.retryablePackets);
  const alertCount = Array.isArray(runtimeVisibility.alerts) ? runtimeVisibility.alerts.length : 0;

  return blockedPackets + poisonPackets + retryablePackets + alertCount;
}

function buildPortalModel(runtimeVisibility) {
  const bridgeMetrics = autonomyBridgeState.dashboard_cards?.[0]?.metrics ?? {};
  const approvalNeededCount =
    bridgeMetrics.approval_needed ??
    autonomyBridgeState.approval_needed_count ??
    runtimeVisibility.executionLedger.approvalCount;
  const blockedCount =
    bridgeMetrics.blocked ??
    autonomyBridgeState.blocked_count ??
    countBlockingSignals(runtimeVisibility);
  const sourceIsMock = runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA;
  const sourceUnknown = runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.UNKNOWN;
  const staleEvidence = runtimeVisibility.runtime.freshness === "stale" || sourceIsMock || sourceUnknown;
  const systemStatus = normalizeStatus(
    staleEvidence ? "NEEDS_REVIEW" : Number(blockedCount) > 0 ? "BLOCKED" : runtimeVisibility.runtime.status
  );

  return {
    systemStatus,
    sourceLabel: runtimeVisibility.sourceLabel ?? "UNKNOWN",
    evidenceState: staleEvidence ? "NEEDS_REVIEW" : "DISPLAY_ONLY",
    freshness: runtimeVisibility.runtime.freshness ?? "UNKNOWN",
    generatedAt: runtimeVisibility.generatedAt ?? "UNKNOWN",
    currentMission: "Minimalist AIOS operator portal with display-only governance.",
    countdown: "20/22",
    lockedState: "LOCKED_READ_ONLY",
    nextSafeAction:
      autonomyBridgeState.next_safe_action ??
      runtimeVisibility.nextSafeAction ??
      "Review evidence before any protected action.",
    approvalNeededCount,
    blockedCount,
    runtimeStatus: runtimeVisibility.runtime.status ?? "UNKNOWN",
    queueSource: runtimeVisibility.runtime.queueSource ?? "UNKNOWN",
    lastTickAt: runtimeVisibility.runtime.lastTickAt ?? null,
    evidenceSourcePath:
      runtimeVisibility.ledgerAuthority?.workLedger?.path ??
      "apps/dashboard/mock-data/aios-runtime-visibility-v1.example.json",
    killSwitchState: "VISIBLE_LOCKED",
    riskGateState: "NEEDS_REVIEW",
    humanApprovalState: "REQUIRED"
  };
}

function classifyRequest(request) {
  const text = request.trim();

  if (!text) {
    return CLASSIFICATION.REQUEST;
  }

  if (forbiddenRequestPatterns.some((pattern) => pattern.test(text))) {
    return CLASSIFICATION.FORBIDDEN;
  }

  if (protectedRequestPatterns.some((pattern) => pattern.test(text))) {
    return CLASSIFICATION.PROTECTED;
  }

  if (readOnlyRequestPatterns.some((pattern) => pattern.test(text))) {
    return CLASSIFICATION.READ_ONLY;
  }

  return CLASSIFICATION.REQUEST;
}

function previewForRequest(request, classification, model, timestamp) {
  const trimmed = request.trim();
  const base = trimmed || "No request text supplied.";

  if (classification === CLASSIFICATION.FORBIDDEN) {
    return {
      request: base,
      classification,
      interpretation: "This request overlaps a forbidden dashboard control boundary.",
      blockedActions: [
        "frontend_execution",
        "broker_or_secret_action",
        "approval_bypass",
        "raw_command_execution"
      ],
      approvalRequired: true,
      nextSafeAction: "Stop and reframe the request as read-only inspection or a governed work request.",
      timestamp
    };
  }

  if (classification === CLASSIFICATION.PROTECTED) {
    return {
      request: base,
      classification,
      interpretation: "This request describes a protected action. The dashboard can display the gate only.",
      blockedActions: [
        "direct_apply",
        "runtime_mutation",
        "approval_mutation",
        "broker_or_live_trading_action"
      ],
      approvalRequired: true,
      nextSafeAction: "Create a scoped packet and obtain Human Owner approval before any action.",
      timestamp
    };
  }

  if (classification === CLASSIFICATION.READ_ONLY) {
    return {
      request: base,
      classification,
      interpretation: "This request can be handled as read-only dashboard inspection.",
      blockedActions: ["execution", "mutation", "protected_action"],
      approvalRequired: false,
      nextSafeAction: model.nextSafeAction,
      timestamp
    };
  }

  return {
    request: base,
    classification,
    interpretation: "This request becomes a local intent preview only.",
    blockedActions: ["execution", "mutation", "approval_mutation", "worker_launch"],
    approvalRequired: true,
    nextSafeAction: "Review the preview, then create an approved work packet if action is needed.",
    timestamp
  };
}

function Metric({ label, value, tone = "neutral" }) {
  return (
    <div className={`metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StatusPill({ value }) {
  return <span className={`statusPill status-${statusTone(value)}`}>{value}</span>;
}

function Panel({ title, eyebrow, children, className = "" }) {
  return (
    <section className={`panel ${className}`.trim()}>
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function StatusHeader({ model, refreshStatus, loading }) {
  return (
    <header className="portalHeader">
      <div>
        <p className="eyebrow">AIOS operator portal</p>
        <h1>AIOS</h1>
        <p className="headerSummary">
          Minimal control surface. Display state, request intent, preserve governance.
        </p>
      </div>
      <div className="headerActions" aria-label="AIOS status">
        <StatusPill value={model.systemStatus} />
        <StatusPill value={model.lockedState} />
        <StatusPill value={model.evidenceState} />
        <button className="button button-readonly" type="button" onClick={refreshStatus}>
          {loading ? "Checking..." : "Refresh Status"}
        </button>
      </div>
    </header>
  );
}

function RequestComposer({
  requestText,
  setRequestText,
  submitRequest,
  createRequestPreview
}) {
  return (
    <Panel title="What do you want AIOS to do?" eyebrow="Command input" className="requestPanel">
      <form className="requestForm" onSubmit={submitRequest}>
        <label className="requestLabel" htmlFor="operator-request">
          Anthony request
        </label>
        <textarea
          id="operator-request"
          value={requestText}
          onChange={(event) => setRequestText(event.target.value)}
          placeholder="Ask for status, evidence, blockers, readiness, or a governed work request."
          rows={5}
        />
        <div className="requestActions">
          <button className="button button-primary" type="submit">
            Submit Request
          </button>
          {requestButtons.map((button) => (
            <button
              className="button button-request"
              key={button.id}
              type="button"
              onClick={() => createRequestPreview(button.prompt)}
            >
              {button.label}
            </button>
          ))}
        </div>
      </form>
      <p className="guardrailText">
        Request submission creates a local preview only. It does not execute commands or mutate AIOS state.
      </p>
    </Panel>
  );
}

function SafeActionButtons({ buttons, selectedPanel, selectPanel, refreshStatus }) {
  return (
    <Panel title="Safe buttons" eyebrow="Read-only actions" className="buttonsPanel">
      <div className="buttonGrid">
        {buttons.map((button) => (
          <button
            className={`button button-readonly ${selectedPanel === button.panel ? "selected" : ""}`}
            key={button.id}
            type="button"
            onClick={button.id === "status" ? refreshStatus : () => selectPanel(button.panel)}
          >
            <span>{button.label}</span>
            <small>{button.type}</small>
          </button>
        ))}
      </div>
    </Panel>
  );
}

function OutputPanel({ selectedOutput, selectedPanel, lastIntentPreview, model }) {
  const fallbackOutput = {
    title: "Portal ready",
    summary: "Submit a request or choose a read-only button to inspect AIOS state.",
    details: [
      `Selected panel: ${selectedPanel}`,
      `Next safe action: ${model.nextSafeAction}`,
      "Execution allowed: false",
      "Mutation allowed: false"
    ]
  };
  const output = selectedOutput ?? fallbackOutput;

  return (
    <Panel title="AIOS response" eyebrow="Output panel" className="outputPanel">
      <div className="outputBox">
        <h3>{output.title}</h3>
        <p>{output.summary}</p>
        <ul>
          {output.details.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      </div>
      {lastIntentPreview ? (
        <div className="previewBox">
          <div className="panelTopline">
            <h3>Latest intent preview</h3>
            <StatusPill value={lastIntentPreview.classification} />
          </div>
          <dl className="previewGrid">
            <div>
              <dt>Request</dt>
              <dd>{lastIntentPreview.request}</dd>
            </div>
            <div>
              <dt>Interpretation</dt>
              <dd>{lastIntentPreview.interpretation}</dd>
            </div>
            <div>
              <dt>Approval required</dt>
              <dd>{String(lastIntentPreview.approvalRequired)}</dd>
            </div>
            <div>
              <dt>Timestamp</dt>
              <dd>{lastIntentPreview.timestamp}</dd>
            </div>
          </dl>
          <p className="nextSafeAction">{lastIntentPreview.nextSafeAction}</p>
        </div>
      ) : null}
    </Panel>
  );
}

function BlockerPanel({ model, lastIntentPreview }) {
  const blockers = [
    "live_trading_allowed=false",
    "broker_allowed=false",
    "approval_mutation_allowed=false",
    "worker_launch_allowed=false",
    "scheduler_allowed=false",
    "execution_allowed=false",
    "mutation_allowed=false",
    ...(lastIntentPreview?.blockedActions ?? [])
  ];

  return (
    <Panel title="Blockers" eyebrow="Fail-closed state">
      <div className="metricRow">
        <Metric label="Blocked count" value={model.blockedCount ?? "UNKNOWN"} tone="warn" />
        <Metric label="Evidence state" value={model.evidenceState} tone={statusTone(model.evidenceState)} />
      </div>
      <ul className="blockedList">
        {[...new Set(blockers)].map((blocker) => (
          <li key={blocker}>{blocker}</li>
        ))}
      </ul>
    </Panel>
  );
}

function ApprovalPanel() {
  return (
    <Panel title="Approval required" eyebrow="Protected gates">
      <div className="protectedList">
        {protectedActions.map((action) => (
          <article className="protectedAction" key={action.id}>
            <div>
              <h3>{action.label}</h3>
              <p>{action.reason}</p>
            </div>
            <button className="button button-locked" type="button" disabled>
              {action.state}
            </button>
          </article>
        ))}
      </div>
    </Panel>
  );
}

function TradingReadinessStrip() {
  return (
    <section className="readinessStrip" aria-label="Trading readiness">
      {tradingReadiness.map((item) => (
        <div className="readinessItem" key={item.label}>
          <span>{item.label}</span>
          <strong className={`stateText state-${statusTone(item.state)}`}>{item.state}</strong>
        </div>
      ))}
    </section>
  );
}

function EvidencePanel({ runtimeVisibility, model }) {
  const operatorPanels = [
    operatorStatusFixture.registry_safety,
    operatorStatusFixture.telemetry_status,
    operatorStatusFixture.worker_status,
    operatorStatusFixture.next_safe_action
  ].filter(Boolean);

  return (
    <Panel title="Dashboard evidence" eyebrow="Display-only sources" className="evidencePanel">
      <div className="evidenceGrid">
        <Metric label="Source" value={model.sourceLabel} tone={statusTone(model.sourceLabel)} />
        <Metric label="Freshness" value={model.freshness} tone={statusTone(model.freshness)} />
        <Metric label="Runtime" value={model.runtimeStatus} tone={statusTone(model.runtimeStatus)} />
        <Metric label="Last tick" value={formatTime(model.lastTickAt)} />
      </div>
      <dl className="evidenceDetails">
        <div>
          <dt>Schema</dt>
          <dd>{runtimeVisibility.schema ?? "UNKNOWN"}</dd>
        </div>
        <div>
          <dt>Generated</dt>
          <dd>{model.generatedAt}</dd>
        </div>
        <div>
          <dt>Queue source</dt>
          <dd>{model.queueSource}</dd>
        </div>
        <div>
          <dt>Evidence path</dt>
          <dd>{model.evidenceSourcePath}</dd>
        </div>
      </dl>
      <div className="operatorEvidenceList">
        {operatorPanels.map((panel) => (
          <article key={panel.label}>
            <span>{panel.label}</span>
            <strong>{panel.status}</strong>
            <p>{panel.summary}</p>
          </article>
        ))}
      </div>
    </Panel>
  );
}

function MissionCards({ model }) {
  return (
    <section className="missionGrid" aria-label="Mission status">
      <Panel title="Current mission" eyebrow="Mission card">
        <p>{model.currentMission}</p>
      </Panel>
      <Panel title="Countdown" eyebrow="Live countdown">
        <div className="largeValue">{model.countdown}</div>
        <p>Minimalist dashboard APPLY in progress. Live boundary remains locked.</p>
      </Panel>
      <Panel title="Locked / armed" eyebrow="Authority state">
        <div className="largeValue small">{model.lockedState}</div>
        <p>Frontend has no execution, mutation, broker, scheduler, or approval authority.</p>
      </Panel>
      <Panel title="Next safe action" eyebrow="Operator guidance">
        <p className="nextSafeAction">{model.nextSafeAction}</p>
      </Panel>
    </section>
  );
}

function SafetyStatePanel({ model }) {
  return (
    <Panel title="Safety state" eyebrow="Read-only guarantees">
      <div className="safetyGrid">
        <Metric label="Execution" value={String(EXECUTION_ALLOWED)} tone="danger" />
        <Metric label="Mutation" value={String(MUTATION_ALLOWED)} tone="danger" />
        <Metric label="Live trading" value={String(LIVE_TRADING_ALLOWED)} tone="danger" />
        <Metric label="Kill switch" value={model.killSwitchState} tone="warn" />
        <Metric label="Risk gate" value={model.riskGateState} tone="warn" />
        <Metric label="Human approval" value={model.humanApprovalState} tone="warn" />
      </div>
    </Panel>
  );
}

export default function App() {
  const [runtimeVisibility, setRuntimeVisibility] = useState(mockVisibilityDisplay);
  const [visibilityLoading, setVisibilityLoading] = useState(false);
  const [requestText, setRequestText] = useState("");
  const [selectedOutput, setSelectedOutput] = useState(null);
  const [lastIntentPreview, setLastIntentPreview] = useState(null);
  const [selectedPanel, setSelectedPanel] = useState("status");

  const model = useMemo(() => buildPortalModel(runtimeVisibility), [runtimeVisibility]);

  const refreshRuntimeVisibility = useCallback(() => {
    setVisibilityLoading(true);
    const config = getRuntimeVisibilityClientConfig();

    return fetchRuntimeVisibilityReadOnly(config)
      .then((result) => {
        setRuntimeVisibility(
          mapRuntimeVisibilityDisplayModel(result.data, { sourceLabel: result.sourceLabel })
        );
      })
      .catch(() => {
        setSelectedOutput({
          title: "Runtime visibility fallback",
          summary: "Local API read-only source is unavailable. Fixture evidence remains displayed.",
          details: [
            "Source: MOCK_DATA",
            "Evidence state: NEEDS_REVIEW",
            "No mutation was attempted."
          ]
        });
      })
      .finally(() => setVisibilityLoading(false));
  }, []);

  function outputForPanel(panel) {
    const panelOutputs = {
      status: {
        title: "Status",
        summary: "AIOS status is displayed from read-only runtime visibility evidence.",
        details: [
          `System status: ${model.systemStatus}`,
          `Runtime status: ${model.runtimeStatus}`,
          `Evidence state: ${model.evidenceState}`
        ]
      },
      nextSafeAction: {
        title: "Next safe action",
        summary: model.nextSafeAction,
        details: ["Review evidence first.", "Protected actions require separate approval."]
      },
      countdown: {
        title: "Countdown",
        summary: "Live Countdown 20/22 dashboard APPLY.",
        details: ["Goal: minimalist operator portal.", "Live boundary: locked."]
      },
      trading: {
        title: "Trading readiness",
        summary: "Trading readiness is visible only. Live trading remains false.",
        details: tradingReadiness.map((item) => `${item.label}: ${item.state}`)
      },
      evidence: {
        title: "Dashboard evidence",
        summary: "Evidence is sourced from fixture/API read models.",
        details: [
          `Source label: ${model.sourceLabel}`,
          `Generated: ${model.generatedAt}`,
          `Evidence path: ${model.evidenceSourcePath}`
        ]
      },
      blockers: {
        title: "Blockers",
        summary: "Protected actions are blocked by default.",
        details: [
          "execution_allowed=false",
          "mutation_allowed=false",
          "live_trading_allowed=false",
          "approval_mutation_allowed=false"
        ]
      },
      approval: {
        title: "Approval required",
        summary: "Human Owner approval is required before protected actions.",
        details: protectedActions.map((action) => `${action.label}: ${action.state}`)
      },
      killSwitch: {
        title: "Kill switch state",
        summary: "Kill switch state is visible but not controllable from this dashboard.",
        details: ["State: VISIBLE_LOCKED", "Direct frontend control: false"]
      },
      riskGate: {
        title: "Risk gate state",
        summary: "Risk gate is displayed as NEEDS_REVIEW until stronger evidence is supplied.",
        details: ["Risk gate: NEEDS_REVIEW", "Bad orders remain blocked by policy."]
      }
    };

    return panelOutputs[panel] ?? panelOutputs.status;
  }

  function selectPanel(panel) {
    setSelectedPanel(panel);
    setSelectedOutput(outputForPanel(panel));
  }

  function createPreviewFromText(text) {
    const classification = classifyRequest(text);
    const preview = previewForRequest(text, classification, model, new Date().toISOString());
    setLastIntentPreview(preview);
    setSelectedOutput({
      title: "Intent preview",
      summary: preview.interpretation,
      details: [
        `Classification: ${preview.classification}`,
        `Approval required: ${preview.approvalRequired}`,
        `Next safe action: ${preview.nextSafeAction}`
      ]
    });
    setSelectedPanel("intentPreview");
  }

  function submitRequest(event) {
    event.preventDefault();
    createPreviewFromText(requestText);
  }

  function createRequestPreview(prompt) {
    setRequestText(prompt);
    createPreviewFromText(prompt);
  }

  return (
    <div className="runtimePage">
      <main className="operatorPortal">
        <StatusHeader
          loading={visibilityLoading}
          model={model}
          refreshStatus={refreshRuntimeVisibility}
        />

        <MissionCards model={model} />
        <TradingReadinessStrip />
        <AIOSLiveOperatorPanel />

        <div className="portalGrid">
          <div className="primaryColumn">
            <RequestComposer
              createRequestPreview={createRequestPreview}
              requestText={requestText}
              setRequestText={setRequestText}
              submitRequest={submitRequest}
            />
            <OutputPanel
              lastIntentPreview={lastIntentPreview}
              model={model}
              selectedOutput={selectedOutput}
              selectedPanel={selectedPanel}
            />
          </div>

          <aside className="sideColumn" aria-label="Read-only control surface">
            <SafeActionButtons
              buttons={safeButtons}
              refreshStatus={refreshRuntimeVisibility}
              selectedPanel={selectedPanel}
              selectPanel={selectPanel}
            />
            <SafetyStatePanel model={model} />
          </aside>
        </div>

        <div className="reviewGrid">
          <BlockerPanel lastIntentPreview={lastIntentPreview} model={model} />
          <ApprovalPanel />
          <EvidencePanel model={model} runtimeVisibility={runtimeVisibility} />
        </div>
      </main>
    </div>
  );
}
