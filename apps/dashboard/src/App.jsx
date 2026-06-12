import { useEffect, useMemo, useRef, useState } from "react";
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
import "./App.css";

const packetFilters = ["all", "dispatch", "wait_for_approval", "retry", "manual_review"];

const zoneDefinitions = [
  {
    id: "mars",
    label: "Mars Lab",
    eyebrow: "Build world",
    status: "REVIEW",
    planetClass: "mars",
    summary: "Codex lanes, PRs, workers, tests, packets, build status, and local dev tools.",
    objective: "Convert active dashboard work into validated, reviewable engineering packets.",
    signals: ["Codex lanes", "PR checks", "Worker evidence", "Build status"]
  },
  {
    id: "moon",
    label: "Moon Control",
    eyebrow: "Mission control",
    status: "NEEDS_APPROVAL",
    planetClass: "moon",
    summary: "AI_OS health, approvals, scheduler evidence, EdgeMark, and critical alerts.",
    objective: "Keep safety state visible before any runtime or protected action.",
    signals: ["AI_OS health", "Approvals", "Scheduler display", "EdgeMark"]
  },
  {
    id: "earth",
    label: "Earth Hub",
    eyebrow: "Workspace",
    status: "PAPER_SAFE",
    planetClass: "earth",
    summary: "Personal apps, contacts, notes, school/work/Microsoft, and user workspace.",
    objective: "Keep personal workspace calm, readable, and separate from privileged controls.",
    signals: ["Personal apps", "Notes", "School/work", "Contacts"]
  },
  {
    id: "galaxy",
    label: "Galaxy Intelligence",
    eyebrow: "Research map",
    status: "UNKNOWN",
    planetClass: "galaxy",
    summary: "AI agents, memory, research, automation map, strategy, and roadmap.",
    objective: "Map intelligence work without implying live AI calls or private prompt storage.",
    signals: ["Agents", "Memory", "Research", "Roadmap"]
  },
  {
    id: "vault",
    label: "Black Hole Vault",
    eyebrow: "Restricted",
    status: "BLOCKED",
    planetClass: "vault",
    summary: "Secrets boundary, broker/live block, restricted references, and emergency warnings.",
    objective: "Keep dangerous capabilities locked behind governance and human approval.",
    signals: ["No secrets", "Broker blocked", "Live blocked", "Restricted"]
  }
];

const advancedCategories = [
  "raw telemetry",
  "queues",
  "approvals",
  "scheduler",
  "runtime",
  "GitHub PR/checks",
  "workers",
  "debug JSON",
  "logs",
  "security state",
  "state freshness"
];

const mockVisibilityDisplay = mapRuntimeVisibilityDisplayModel(mockRuntimeVisibility, {
  sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA
});

const operatorStatusPanels = [
  operatorStatusFixture.registry_safety,
  operatorStatusFixture.telemetry_status,
  operatorStatusFixture.worker_status,
  operatorStatusFixture.pr_branch_status,
  operatorStatusFixture.next_safe_action
];

const autonomyBridgeState = autonomyBridgeStatePayload.data ?? {};
const autonomyBridgeCards = Array.isArray(autonomyBridgeState.dashboard_cards)
  ? autonomyBridgeState.dashboard_cards
  : [];
const autonomyBridgeSourceIsLive = autonomyBridgeStatePayload.sourceLabel === "LIVE";

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

function formatDuration(ms) {
  if (ms === undefined || ms === null) {
    return "UNKNOWN";
  }

  const absMs = Math.abs(ms);
  const minutes = Math.floor(absMs / 60000);
  const seconds = Math.floor((absMs % 60000) / 1000);
  const value = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

  return ms < 0 ? `${value} overdue` : value;
}

function statusTone(value) {
  const normalized = String(value).toLowerCase();

  if (
    ["critical", "blocked", "hard", "expired", "manual_review", "degraded"].includes(
      normalized
    )
  ) {
    return "danger";
  }

  if (
    [
      "warning",
      "soft",
      "stale",
      "retry",
      "wait_for_approval",
      "paused",
      "needs_approval",
      "review"
    ].includes(normalized)
  ) {
    return "warn";
  }

  if (
    ["active", "running", "dispatch", "none", "low", "fresh", "ready", "paper_safe"].includes(
      normalized
    )
  ) {
    return "good";
  }

  if (
    ["pass", "mock_data", "display_only", "not_connected", "not_evaluated", "model_preview"].includes(
      normalized
    )
  ) {
    return "good";
  }

  return "neutral";
}

function metricTone(value, tone) {
  return value === "UNKNOWN" ? "neutral" : tone;
}

function normalizeStatusValue(value) {
  const normalized = String(value ?? "UNKNOWN").toLowerCase();

  if (["blocked", "critical", "hard", "expired", "degraded"].includes(normalized)) {
    return "BLOCKED";
  }

  if (["needs_approval", "wait_for_approval", "warning", "warn", "review"].includes(normalized)) {
    return "NEEDS_APPROVAL";
  }

  if (["ready", "pass", "active", "fresh", "paper_safe"].includes(normalized)) {
    return "READY";
  }

  return "UNKNOWN";
}

function Metric({ label, value, tone = "neutral" }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StatusPill({ value }) {
  return <span className={`pill ${statusTone(value)}`}>{value}</span>;
}

function Section({ title, action, children }) {
  return (
    <section className="section">
      <div className="sectionHeader">
        <h2>{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}

function UnavailableMessage({ children }) {
  return <p className="nextAction">{children}</p>;
}

function buildCriticalAlerts(runtimeVisibility, approvalNeededCount, blockedCount) {
  const runtimeAlerts = Array.isArray(runtimeVisibility.alerts) ? runtimeVisibility.alerts : [];
  const criticalRuntimeAlerts = runtimeAlerts.filter((alert) =>
    ["critical", "blocked", "warning"].includes(String(alert.severity).toLowerCase())
  );

  const alerts = criticalRuntimeAlerts.slice(0, 2).map((alert) => ({
    label: alert.category ?? "runtime",
    status: alert.severity ?? "UNKNOWN",
    message: alert.message ?? "Runtime alert unavailable."
  }));

  if (approvalNeededCount !== "UNKNOWN" && Number(approvalNeededCount) > 0) {
    alerts.push({
      label: "approval",
      status: "NEEDS_APPROVAL",
      message: `${approvalNeededCount} item(s) need Anthony review before protected action.`
    });
  }

  if (blockedCount !== "UNKNOWN" && Number(blockedCount) > 0) {
    alerts.push({
      label: "blocked",
      status: "BLOCKED",
      message: `${blockedCount} blocked item(s) remain stopped.`
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      label: "evidence",
      status: "UNKNOWN",
      message: "No critical alert source is currently verified."
    });
  }

  return alerts.slice(0, 4);
}

function deriveAiosEdgeMark(runtimeVisibility, approvalNeededCount, blockedCount) {
  const reasons = [];
  let score = 78;

  if (runtimeVisibility.runtime.freshness === "stale") {
    score -= 12;
    reasons.push("stale runtime evidence penalty");
  }

  if (runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA) {
    score -= 10;
    reasons.push("fixture source lowers confidence");
  }

  if (Number(approvalNeededCount) > 0) {
    score -= 8;
    reasons.push("approval gate pending");
  }

  if (Number(blockedCount) > 0) {
    score -= 12;
    reasons.push("blocked items visible");
  }

  if (!runtimeVisibility.health.healthy) {
    score -= 8;
    reasons.push("automation health requires review");
  }

  reasons.push("live trading remains blocked");
  reasons.push("broker execution remains blocked");

  const safeScore = Math.max(0, Math.min(100, score));

  if (runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.UNKNOWN) {
    return {
      value: "UNKNOWN",
      label: "UNKNOWN UNTIL WIRED",
      band: "UNKNOWN",
      confidence: "LOW",
      reasons: ["source unavailable", "missing data is not success"]
    };
  }

  return {
    value: safeScore,
    label: "MODEL PREVIEW",
    band: safeScore >= 90 ? "READY" : safeScore >= 70 ? "REVIEW" : safeScore >= 40 ? "NEEDS_APPROVAL" : "BLOCKED",
    confidence: runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA ? "FIXTURE" : "READ_ONLY",
    reasons: reasons.slice(0, 5)
  };
}

function buildPlanetaryDashboardModel(runtimeVisibility) {
  const bridgeMetrics = autonomyBridgeCards[0]?.metrics ?? {};
  const winsCount = bridgeMetrics.wins ?? autonomyBridgeState.wins_count ?? "UNKNOWN";
  const blockedCount =
    bridgeMetrics.blocked ??
    autonomyBridgeState.blocked_count ??
    runtimeVisibility.executionLedger.blockedPacketCount;
  const approvalNeededCount =
    bridgeMetrics.approval_needed ??
    autonomyBridgeState.approval_needed_count ??
    runtimeVisibility.executionLedger.approvalCount;
  const nightSupervisorStatus =
    autonomyBridgeState.night_supervisor_status ??
    autonomyBridgeState.supervisor_status ??
    "UNKNOWN";
  const nextSafeAction =
    autonomyBridgeState.next_safe_action ??
    runtimeVisibility.nextSafeAction ??
    "Review evidence before protected action.";
  const globalStatus = normalizeStatusValue(
    Number(blockedCount) > 0
      ? "BLOCKED"
      : Number(approvalNeededCount) > 0
        ? "NEEDS_APPROVAL"
        : runtimeVisibility.runtime.status
  );

  return {
    winsCount,
    blockedCount,
    approvalNeededCount,
    nightSupervisorStatus,
    nextSafeAction,
    globalStatus,
    edgeMark: deriveAiosEdgeMark(runtimeVisibility, approvalNeededCount, blockedCount),
    criticalAlerts: buildCriticalAlerts(runtimeVisibility, approvalNeededCount, blockedCount),
    objective: "Turn AI_OS into a realistic planetary command system while keeping all protected actions gated.",
    mode: "paper-safe",
    sourceLabel: runtimeVisibility.sourceLabel,
    freshness: runtimeVisibility.runtime.freshness
  };
}

function useAiosInputNavigation(zoneIds, activeZoneId, setActiveZoneId, handlers) {
  useEffect(() => {
    function moveZone(delta) {
      const currentIndex = Math.max(zoneIds.indexOf(activeZoneId), 0);
      const nextIndex = (currentIndex + delta + zoneIds.length) % zoneIds.length;
      const nextZoneId = zoneIds[nextIndex];

      setActiveZoneId(nextZoneId);
      window.requestAnimationFrame(() => {
        document.querySelector(`[data-zone-id="${nextZoneId}"]`)?.focus();
      });
    }

    function handleKeyDown(event) {
      const key = event.key.toLowerCase();
      const target = event.target;
      const isTypingTarget =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement;

      if (event.key === "Escape") {
        if (handlers.closeTopLayer()) {
          event.preventDefault();
        }
        return;
      }

      if (isTypingTarget) {
        return;
      }

      if (["arrowright", "arrowdown", "d", "s"].includes(key)) {
        event.preventDefault();
        moveZone(1);
      }

      if (["arrowleft", "arrowup", "a", "w"].includes(key)) {
        event.preventDefault();
        moveZone(-1);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeZoneId, handlers, setActiveZoneId, zoneIds]);
}

function useGamepadPresence() {
  const [gamepadConnected, setGamepadConnected] = useState(false);

  useEffect(() => {
    function refreshGamepadState() {
      const pads = navigator.getGamepads?.() ?? [];
      setGamepadConnected(Array.from(pads).some(Boolean));
    }

    function handleConnected() {
      setGamepadConnected(true);
    }

    function handleDisconnected() {
      refreshGamepadState();
    }

    window.addEventListener("gamepadconnected", handleConnected);
    window.addEventListener("gamepaddisconnected", handleDisconnected);
    refreshGamepadState();

    return () => {
      window.removeEventListener("gamepadconnected", handleConnected);
      window.removeEventListener("gamepaddisconnected", handleDisconnected);
    };
  }, []);

  return gamepadConnected;
}

function AiosEdgeMarkPanel({ edgeMark }) {
  return (
    <section className="edgeMarkPanel" aria-labelledby="edgemark-title">
      <div>
        <p className="eyebrow">AIOS EdgeMark</p>
        <h2 id="edgemark-title">{edgeMark.label}</h2>
      </div>
      <div className="edgeScore">
        <strong>{edgeMark.value}</strong>
        <span>{edgeMark.band}</span>
      </div>
      <p className="edgeConfidence">Confidence: {edgeMark.confidence}</p>
      <ul>
        {edgeMark.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </section>
  );
}

function SafetyStatusStrip({ model }) {
  const safetyItems = [
    ["Live trading", "BLOCKED"],
    ["Broker", "BLOCKED"],
    ["Secrets", "SAFE"],
    ["Source", model.sourceLabel],
    ["Freshness", model.freshness]
  ];

  return (
    <section className="safetyStrip" aria-label="AI_OS safety state">
      {safetyItems.map(([label, value]) => (
        <div className="safetyItem" key={label}>
          <span>{label}</span>
          <StatusPill value={value} />
        </div>
      ))}
    </section>
  );
}

function CriticalAlertsPanel({ alerts }) {
  return (
    <section className="criticalAlerts" aria-labelledby="critical-alerts-title">
      <div className="panelTitleRow">
        <p className="eyebrow">Critical only</p>
        <h2 id="critical-alerts-title">Alerts</h2>
      </div>
      <div className="alertStack">
        {alerts.map((alert) => (
          <article className="alertCard" key={`${alert.label}-${alert.message}`}>
            <StatusPill value={alert.status} />
            <div>
              <strong>{alert.label}</strong>
              <p>{alert.message}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function PlanetZoneNode({ zone, isActive, isSelected, onFocus, onSelect }) {
  return (
    <button
      className={`planetNode ${zone.planetClass} ${isActive ? "active" : ""} ${
        isSelected ? "selected" : ""
      }`}
      data-zone-id={zone.id}
      type="button"
      onClick={() => onSelect(zone.id)}
      onFocus={() => onFocus(zone.id)}
      aria-pressed={isSelected}
    >
      <span className="planetVisual" aria-hidden="true">
        <span className="planetCore" />
      </span>
      <span className="zoneCopy">
        <span className="eyebrow">{zone.eyebrow}</span>
        <strong>{zone.label}</strong>
        <small>{zone.summary}</small>
        <span className="zoneStatus">
          <StatusPill value={zone.status} />
        </span>
      </span>
    </button>
  );
}

function PlanetaryScene({ zones, activeZoneId, selectedZoneId, onFocusZone, onSelectZone }) {
  return (
    <section className="planetaryScene" aria-label="Planetary zone navigation">
      <div className="starfield" aria-hidden="true" />
      <div className="orbitalPath pathOne" aria-hidden="true" />
      <div className="orbitalPath pathTwo" aria-hidden="true" />
      <div className="orbitalPath pathThree" aria-hidden="true" />
      <div className="zoneMap">
        {zones.map((zone) => (
          <PlanetZoneNode
            key={zone.id}
            zone={zone}
            isActive={activeZoneId === zone.id}
            isSelected={selectedZoneId === zone.id}
            onFocus={onFocusZone}
            onSelect={onSelectZone}
          />
        ))}
      </div>
    </section>
  );
}

function ZoneDetailPanel({ zone }) {
  return (
    <section className="zoneDetailPanel" aria-labelledby="zone-detail-title">
      <div className="panelTitleRow">
        <p className="eyebrow">Selected zone</p>
        <h2 id="zone-detail-title">{zone.label}</h2>
      </div>
      <p>{zone.objective}</p>
      <div className="signalGrid">
        {zone.signals.map((signal) => (
          <span key={signal}>{signal}</span>
        ))}
      </div>
    </section>
  );
}

function MissionObjectivePanel({ model }) {
  return (
    <section className="missionObjectivePanel" aria-labelledby="mission-objective-title">
      <div>
        <p className="eyebrow">Current objective</p>
        <h2 id="mission-objective-title">{model.objective}</h2>
      </div>
      <div className="nextActionBox">
        <span>Next allowed action</span>
        <strong>{model.nextSafeAction}</strong>
      </div>
    </section>
  );
}

function PaperLeaguePanel() {
  const categories = [
    "risk-adjusted return",
    "lowest drawdown",
    "consistency streak",
    "execution quality",
    "EdgeMark progression"
  ];

  return (
    <section className="paperLeaguePanel" aria-labelledby="paper-league-title">
      <div className="panelTitleRow">
        <p className="eyebrow">Paper League</p>
        <h2 id="paper-league-title">Simulated only</h2>
      </div>
      <p>
        Paper League is display-only in Phase 1. No real-money competition, broker action,
        live orders, or external leaderboard writes.
      </p>
      <div className="leagueCategories">
        {categories.map((category) => (
          <span key={category}>{category}</span>
        ))}
      </div>
    </section>
  );
}

function AstronautModeTile() {
  return (
    <section className="astronautTile" aria-labelledby="astronaut-title">
      <div className="helmetPreview" aria-hidden="true" />
      <div>
        <p className="eyebrow">Future immersive mode</p>
        <h2 id="astronaut-title">Astronaut Mode locked</h2>
        <p>Phase 1 does not implement movement, engine dependencies, or UE5 files.</p>
      </div>
      <StatusPill value="LOCKED" />
    </section>
  );
}

function InputHelpOverlay({ open, gamepadConnected, onClose }) {
  if (!open) {
    return null;
  }

  return (
    <div className="overlayBackdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="inputHelpOverlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="input-help-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="drawerTitle">
          <div>
            <p className="eyebrow">Controls</p>
            <h2 id="input-help-title">Command navigation</h2>
          </div>
          <button className="iconButton" type="button" onClick={onClose} aria-label="Close controls">
            X
          </button>
        </div>
        <div className="controlGrid">
          <div>
            <strong>Keyboard</strong>
            <p>Tab, arrows/WASD, Enter, Space, Escape.</p>
          </div>
          <div>
            <strong>Mouse</strong>
            <p>Hover and click zones. No destructive click actions.</p>
          </div>
          <div>
            <strong>Xbox</strong>
            <p>D-pad/left stick, A select, B back, X Advanced, Y search later.</p>
          </div>
        </div>
        <div className="controllerState">
          <StatusPill value={gamepadConnected ? "GAMEPAD_DETECTED" : "GAMEPAD_HELP_ONLY"} />
          <span>No controller action can commit, push, trade, approve, or mutate queues.</span>
        </div>
      </section>
    </div>
  );
}

function OperatorStatusPanel({ panel }) {
  const detailRows = [
    ["Source", panel.source],
    ["Branch", panel.branch],
    ["Base", panel.base],
    ["Merge", panel.merge_state],
    ["Collector", panel.collector_state],
    ["Latest event", panel.latest_event_at ? formatTime(panel.latest_event_at) : null],
    ["Active workers", panel.active_workers],
    ["Blocked workers", panel.blocked_workers],
    ["Action type", panel.action_type]
  ].filter(([, value]) => value !== undefined && value !== null && value !== "");

  return (
    <article className="operatorStatusCard">
      <div className="operatorStatusTop">
        <h3>{panel.label}</h3>
        <StatusPill value={panel.status} />
      </div>
      <p>{panel.summary}</p>
      {detailRows.length > 0 ? (
        <dl className="operatorStatusMeta">
          {detailRows.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      {panel.blocked_actions?.length ? (
        <ul className="blockedList">
          {panel.blocked_actions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      ) : null}
    </article>
  );
}

function AutonomyBridgeCard({ card }) {
  const metrics = card.metrics ?? {};

  return (
    <article className="autonomyBridgeCard">
      <div className="operatorStatusTop">
        <h3>{card.title ?? "Autonomy Bridge"}</h3>
        <StatusPill value={card.status ?? "UNKNOWN"} />
      </div>
      <p>{card.summary ?? autonomyBridgeState.plain_summary ?? "No bridge summary available."}</p>
      <div className="metricsGrid autonomyMetrics">
        <Metric label="Wins" value={metrics.wins ?? autonomyBridgeState.wins_count ?? "UNKNOWN"} />
        <Metric
          label="Blocked"
          value={metrics.blocked ?? autonomyBridgeState.blocked_count ?? "UNKNOWN"}
          tone={metricTone(metrics.blocked ?? autonomyBridgeState.blocked_count, "danger")}
        />
        <Metric
          label="Approval needed"
          value={metrics.approval_needed ?? autonomyBridgeState.approval_needed_count ?? "UNKNOWN"}
          tone={metricTone(
            metrics.approval_needed ?? autonomyBridgeState.approval_needed_count,
            "warn"
          )}
        />
        <Metric
          label="Worker notes"
          value={metrics.worker_notes ?? autonomyBridgeState.worker_notes_count ?? "UNKNOWN"}
        />
      </div>
      <p className="nextAction">{card.next_action ?? autonomyBridgeState.next_safe_action}</p>
    </article>
  );
}

function AdvancedDrawer({
  open,
  onClose,
  runtimeVisibility,
  filteredPackets,
  failedGroups,
  eventQuery,
  setEventQuery,
  packetFilter,
  setPacketFilter,
  isLocalApiReadOnly
}) {
  const healthTone = runtimeVisibility.health.healthy ? "good" : "danger";
  const ledgerAuthority = runtimeVisibility.ledgerAuthority ?? {};
  const workLedger = ledgerAuthority.workLedger ?? {};
  const nightSupervisorLedger = ledgerAuthority.nightSupervisorLedger ?? {};

  if (!open) {
    return null;
  }

  return (
    <div className="drawerBackdrop" role="presentation" onMouseDown={onClose}>
      <aside
        className="advancedDrawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="advanced-drawer-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="drawerTitle">
          <div>
            <p className="eyebrow">Operator advanced</p>
            <h2 id="advanced-drawer-title">Raw detail drawer</h2>
          </div>
          <button className="iconButton" type="button" onClick={onClose} aria-label="Close Advanced drawer">
            X
          </button>
        </div>

        <div className="advancedCategoryGrid" aria-label="Advanced categories">
          {advancedCategories.map((category) => (
            <span key={category}>{category}</span>
          ))}
        </div>

        <main className="runtimeGrid">
          <Section title="Runtime Status">
            <div className="metricsGrid">
              <Metric label="Runtime ID" value={runtimeVisibility.runtime.runtimeId} />
              <Metric
                label="Status"
                value={runtimeVisibility.runtime.status}
                tone={statusTone(runtimeVisibility.runtime.status)}
              />
              <Metric
                label="Freshness"
                value={runtimeVisibility.runtime.freshness}
                tone={statusTone(runtimeVisibility.runtime.freshness)}
              />
              <Metric label="Queue source" value={runtimeVisibility.runtime.queueSource} />
              <Metric label="Last tick" value={formatTime(runtimeVisibility.runtime.lastTickAt)} />
              <Metric label="Last event" value={formatTime(runtimeVisibility.telemetry.lastEventAt)} />
            </div>
          </Section>

          <Section title="Health Summary">
            <div className="metricsGrid">
              <Metric
                label="Runtime"
                value={runtimeVisibility.health.healthy ? "Healthy" : "Attention"}
                tone={healthTone}
              />
              <Metric label="Scheduler actions" value={runtimeVisibility.health.schedulerActions} />
              <Metric
                label="Expired workers"
                value={runtimeVisibility.health.expiredWorkers}
                tone={metricTone(runtimeVisibility.health.expiredWorkers, "danger")}
              />
              <Metric
                label="Poison packets"
                value={runtimeVisibility.health.poisonPackets}
                tone={metricTone(runtimeVisibility.health.poisonPackets, "danger")}
              />
              <Metric
                label="Retryable packets"
                value={runtimeVisibility.health.retryablePackets}
                tone={metricTone(runtimeVisibility.health.retryablePackets, "warn")}
              />
              <Metric
                label="Reclaimable"
                value={runtimeVisibility.health.reclaimablePackets}
                tone={metricTone(runtimeVisibility.health.reclaimablePackets, "warn")}
              />
            </div>
          </Section>

          <Section title="Queue Counters">
            <div className="queueStrip">
              {Object.entries(runtimeVisibility.queue).map(([key, value]) => (
                <Metric key={key} label={key.replaceAll("_", " ")} value={value} />
              ))}
            </div>
          </Section>

          <Section
            title="Active Packets"
            action={
              isLocalApiReadOnly ? null : (
                <div className="segmented">
                  {packetFilters.map((filter) => (
                    <button
                      key={filter}
                      className={filter === packetFilter ? "selected" : ""}
                      onClick={() => setPacketFilter(filter)}
                      type="button"
                    >
                      {filter.replaceAll("_", " ")}
                    </button>
                  ))}
                </div>
              )
            }
          >
            {isLocalApiReadOnly ? (
              <UnavailableMessage>
                Active packet state is not available from LOCAL_API_READ_ONLY.
              </UnavailableMessage>
            ) : (
              <div className="table">
                <div className="tableRow tableHead">
                  <span>Packet</span>
                  <span>Status</span>
                  <span>Risk</span>
                  <span>Last update</span>
                  <span>Reason</span>
                </div>
                {filteredPackets.map((packet) => (
                  <div className="tableRow" key={packet.packetId}>
                    <strong>{packet.packetId}</strong>
                    <StatusPill value={packet.action ?? packet.status} />
                    <span>{packet.risk ?? "UNKNOWN"}</span>
                    <span>{formatTime(packet.lastUpdatedAt)}</span>
                    <span>{packet.reason ?? packet.lastEventType ?? "No scheduler reason"}</span>
                  </div>
                ))}
              </div>
            )}
          </Section>

          <Section title="Failed Packets">
            {isLocalApiReadOnly ? (
              <UnavailableMessage>
                Failure grouping is not available from LOCAL_API_READ_ONLY.
              </UnavailableMessage>
            ) : (
              <>
                <div className="failureSplit">
                  <Metric label="Retryable" value={failedGroups.retryable.length} tone="warn" />
                  <Metric label="Manual review" value={failedGroups.poison.length} tone="danger" />
                </div>
                <div className="stackList">
                  {failedGroups.all.map((packet) => (
                    <article className="listItem" key={packet.packetId}>
                      <div>
                        <strong>{packet.packetId}</strong>
                        <p>{packet.reason}</p>
                      </div>
                      <div className="itemMeta">
                        <StatusPill value={packet.retryable ? "retryable" : "manual_review"} />
                        <span>{packet.failureCount} failures</span>
                        <span>{packet.source}</span>
                        <span>{formatTime(packet.lastFailedAt)}</span>
                      </div>
                    </article>
                  ))}
                </div>
              </>
            )}
          </Section>

          <Section title="Worker Leases">
            {isLocalApiReadOnly ? (
              <UnavailableMessage>
                Worker lease state is not exposed by LOCAL_API_READ_ONLY.
              </UnavailableMessage>
            ) : (
              <div className="workerGrid">
                {runtimeVisibility.workers.map((worker) => (
                  <article className="workerCard" key={worker.workerId}>
                    <div className="workerTop">
                      <strong>{worker.workerId}</strong>
                      <StatusPill value={worker.leaseState} />
                    </div>
                    <p>{worker.packetId ?? "No active packet"}</p>
                    <div className="workerMeta">
                      <span>Heartbeat {formatTime(worker.lastHeartbeatAt)}</span>
                      <span>Age {formatDuration(worker.heartbeatAgeMs)}</span>
                      <span>Lease {worker.leaseExpiresAt ? formatTime(worker.leaseExpiresAt) : "UNKNOWN"}</span>
                      <span>Expires in {formatDuration(worker.leaseExpiresInMs)}</span>
                      <span>{worker.reclaimablePacket ? "Packet reclaimable" : "Lease normal"}</span>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </Section>

          <Section title="Backpressure Alerts">
            <div className={`backpressure ${statusTone(runtimeVisibility.backpressure.level)}`}>
              <div>
                <strong>{runtimeVisibility.backpressure.reason}</strong>
                <p>Allowed concurrent packets: {runtimeVisibility.backpressure.allowedConcurrentPackets}</p>
              </div>
              <StatusPill value={runtimeVisibility.backpressure.level} />
            </div>
            <div className="pressureGrid">
              {isLocalApiReadOnly ? (
                <Metric label="Backpressure inputs" value="UNKNOWN" />
              ) : (
                Object.entries(runtimeVisibility.backpressure.pressureInputs).map(([key, value]) => (
                  <Metric key={key} label={key} value={value} />
                ))
              )}
            </div>
            <div className="alerts">
              {runtimeVisibility.alerts.map((alert) => (
                <div className="alert" key={`${alert.category}-${alert.message}`}>
                  <StatusPill value={alert.severity} />
                  <span>{alert.message}</span>
                </div>
              ))}
            </div>
          </Section>

          <Section
            title="Telemetry Log"
            action={
              <input
                className="search"
                value={eventQuery}
                onChange={(event) => setEventQuery(event.target.value)}
                placeholder="Filter telemetry"
                aria-label="Filter telemetry events"
              />
            }
          >
            <div className="ledgerSummary">
              <Metric label="Events" value={runtimeVisibility.telemetry.eventCount} />
              <Metric label="Invalid lines" value={runtimeVisibility.telemetry.invalidLineCount} />
              <Metric
                label="Work ledger"
                value={workLedger.status ?? "UNKNOWN"}
                tone={statusTone(workLedger.status ?? "UNKNOWN")}
              />
              <Metric label="Work events" value={workLedger.eventCount ?? "UNKNOWN"} />
              <Metric
                label="Night ledger"
                value={nightSupervisorLedger.status ?? "UNKNOWN"}
                tone={statusTone(nightSupervisorLedger.status ?? "UNKNOWN")}
              />
              <Metric label="Night events" value={nightSupervisorLedger.eventCount ?? "UNKNOWN"} />
            </div>
            <p className="nextAction">
              {ledgerAuthority.proofBoundary ?? "Ledger evidence is display-only."}
            </p>
            <div className="eventList">
              {runtimeVisibility.telemetry.recentEvents
                .filter((event) => {
                  const query = eventQuery.trim().toLowerCase();

                  if (!query) {
                    return true;
                  }

                  return [event.eventType, event.source, event.summary, event.packetId]
                    .filter(Boolean)
                    .some((value) => String(value).toLowerCase().includes(query));
                })
                .map((event) => (
                  <article className="eventItem" key={event.eventId}>
                    <div>
                      <strong>{event.eventType}</strong>
                      <p>{event.summary}</p>
                    </div>
                    <div className="itemMeta">
                      <span>{event.source}</span>
                      <span>{event.packetId ?? "No packet"}</span>
                      <span>{formatTime(event.ts)}</span>
                    </div>
                  </article>
                ))}
            </div>
          </Section>

          <Section title="Execution Ledger">
            {isLocalApiReadOnly ? (
              <UnavailableMessage>
                Execution ledger summary is not available from LOCAL_API_READ_ONLY.
              </UnavailableMessage>
            ) : (
              <div className="ledgerSummary">
                <Metric label="Packets" value={runtimeVisibility.executionLedger.packetCount} />
                <Metric label="Approvals" value={runtimeVisibility.executionLedger.approvalCount} />
                <Metric
                  label="Blocked"
                  value={runtimeVisibility.executionLedger.blockedPacketCount}
                  tone="warn"
                />
                <Metric
                  label="Applied"
                  value={runtimeVisibility.executionLedger.appliedPacketCount}
                  tone="good"
                />
              </div>
            )}
            <p className="nextAction">{runtimeVisibility.nextSafeAction}</p>
          </Section>

          <Section title="Operator Fixture">
            <div className="operatorStatusGrid">
              {operatorStatusPanels.map((panel) => (
                <OperatorStatusPanel key={panel.label} panel={panel} />
              ))}
            </div>
          </Section>

          <Section title="Autonomy Bridge">
            <div className="bridgeSourceRow">
              <StatusPill value={autonomyBridgeSourceIsLive ? "LIVE" : "sample"} />
              <StatusPill value={`source: ${autonomyBridgeStatePayload.sourcePath}`} />
              <StatusPill value={`schema: ${autonomyBridgeState.schema ?? "UNKNOWN"}`} />
            </div>
            {autonomyBridgeStatePayload.fallbackReason ? (
              <div className="warningStrip bridgeWarning">
                <span>Live bridge state unavailable; showing sample data.</span>
              </div>
            ) : null}
            <div className="autonomyBridgeGrid">
              {autonomyBridgeCards.length > 0 ? (
                autonomyBridgeCards.map((card) => (
                  <AutonomyBridgeCard key={card.title ?? "autonomy-bridge-card"} card={card} />
                ))
              ) : (
                <AutonomyBridgeCard card={{ title: "Night Supervisor Brief" }} />
              )}
            </div>
          </Section>
        </main>
      </aside>
    </div>
  );
}

function PlanetaryCommandShell({
  model,
  zones,
  activeZoneId,
  selectedZoneId,
  setActiveZoneId,
  setSelectedZoneId,
  openAdvanced,
  openInputHelp
}) {
  const selectedZone = zones.find((zone) => zone.id === selectedZoneId) ?? zones[0];

  return (
    <div className="commandShell">
      <header className="commandHeader">
        <div className="brandBlock">
          <p className="eyebrow">AI_OS planetary command</p>
          <h1>AIOS</h1>
          <p>Intelligent. Adaptive. Yours.</p>
        </div>
        <div className="commandHeaderStatus" aria-label="Global status">
          <StatusPill value={model.globalStatus} />
          <StatusPill value={model.mode} />
          <StatusPill value={model.edgeMark.label} />
          <button className="headerButton" type="button" onClick={openInputHelp}>
            Controls
          </button>
          <button className="headerButton primary" type="button" onClick={openAdvanced}>
            Advanced
          </button>
        </div>
      </header>

      <SafetyStatusStrip model={model} />

      <main className="planetaryLayout">
        <section className="commandIntro" aria-labelledby="command-intro-title">
          <p className="eyebrow">Realistic command system</p>
          <h2 id="command-intro-title">Cinematic planetary operations shell</h2>
          <p>
            AI_OS is displayed as a realistic, governance-bound command environment. The
            first screen keeps safety, status, objective, and next allowed action above raw
            telemetry.
          </p>
        </section>

        <AiosEdgeMarkPanel edgeMark={model.edgeMark} />
        <CriticalAlertsPanel alerts={model.criticalAlerts} />
        <MissionObjectivePanel model={model} />

        <PlanetaryScene
          zones={zones}
          activeZoneId={activeZoneId}
          selectedZoneId={selectedZoneId}
          onFocusZone={setActiveZoneId}
          onSelectZone={setSelectedZoneId}
        />

        <ZoneDetailPanel zone={selectedZone} />
        <PaperLeaguePanel />
        <AstronautModeTile />
      </main>
    </div>
  );
}

export default function App() {
  const [runtimeVisibility, setRuntimeVisibility] = useState(mockVisibilityDisplay);
  const [visibilityLoading, setVisibilityLoading] = useState(true);
  const [packetFilter, setPacketFilter] = useState("all");
  const [eventQuery, setEventQuery] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [inputHelpOpen, setInputHelpOpen] = useState(false);
  const [activeZoneId, setActiveZoneId] = useState(zoneDefinitions[0].id);
  const [selectedZoneId, setSelectedZoneId] = useState(zoneDefinitions[0].id);
  const handlersRef = useRef({
    closeTopLayer: () => false
  });
  const stableInputHandlers = useMemo(
    () => ({
      closeTopLayer: () => handlersRef.current.closeTopLayer()
    }),
    []
  );
  const gamepadConnected = useGamepadPresence();

  useEffect(() => {
    const config = getRuntimeVisibilityClientConfig();
    fetchRuntimeVisibilityReadOnly(config)
      .then((result) => {
        setRuntimeVisibility(
          mapRuntimeVisibilityDisplayModel(result.data, { sourceLabel: result.sourceLabel })
        );
      })
      .catch(() => {
        // API unavailable: retain mock data already in state.
      })
      .finally(() => setVisibilityLoading(false));
  }, []);

  useEffect(() => {
    handlersRef.current = {
      closeTopLayer: () => {
        if (inputHelpOpen) {
          setInputHelpOpen(false);
          return true;
        }

        if (advancedOpen) {
          setAdvancedOpen(false);
          return true;
        }

        if (selectedZoneId !== activeZoneId) {
          setSelectedZoneId(activeZoneId);
          return true;
        }

        return false;
      }
    };
  }, [activeZoneId, advancedOpen, inputHelpOpen, selectedZoneId]);

  useAiosInputNavigation(
    zoneDefinitions.map((zone) => zone.id),
    activeZoneId,
    setActiveZoneId,
    stableInputHandlers
  );

  const isLocalApiReadOnly =
    runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.LOCAL_API_READ_ONLY;

  const filteredPackets = useMemo(() => {
    if (packetFilter === "all") {
      return runtimeVisibility.activePackets;
    }

    return runtimeVisibility.activePackets.filter((packet) => packet.action === packetFilter);
  }, [packetFilter, runtimeVisibility.activePackets]);

  const failedGroups = runtimeVisibility.failedPackets;
  const model = useMemo(() => buildPlanetaryDashboardModel(runtimeVisibility), [runtimeVisibility]);

  return (
    <div className="runtimePage">
      {visibilityLoading ? (
        <div className="loadingStatus" role="status">
          <StatusPill value="loading" />
          <span>Checking read-only runtime visibility.</span>
        </div>
      ) : null}

      <PlanetaryCommandShell
        model={model}
        zones={zoneDefinitions}
        activeZoneId={activeZoneId}
        selectedZoneId={selectedZoneId}
        setActiveZoneId={setActiveZoneId}
        setSelectedZoneId={setSelectedZoneId}
        openAdvanced={() => setAdvancedOpen(true)}
        openInputHelp={() => setInputHelpOpen(true)}
      />

      <AdvancedDrawer
        open={advancedOpen}
        onClose={() => setAdvancedOpen(false)}
        runtimeVisibility={runtimeVisibility}
        filteredPackets={filteredPackets}
        failedGroups={failedGroups}
        eventQuery={eventQuery}
        setEventQuery={setEventQuery}
        packetFilter={packetFilter}
        setPacketFilter={setPacketFilter}
        isLocalApiReadOnly={isLocalApiReadOnly}
      />

      <InputHelpOverlay
        open={inputHelpOpen}
        gamepadConnected={gamepadConnected}
        onClose={() => setInputHelpOpen(false)}
      />
    </div>
  );
}
