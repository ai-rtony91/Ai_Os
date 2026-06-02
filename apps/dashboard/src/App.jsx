import { useEffect, useMemo, useState } from "react";
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
const playlistDockItems = [
  {
    title: "Telemetry chat import",
    status: "placeholder",
    summary: "Future local intake for telemetry chat references. No private links fetched."
  },
  {
    title: "Parallax web app ideas",
    status: "placeholder",
    summary: "Future idea lane for visual app concepts. Planning only."
  },
  {
    title: "Music playlist references",
    status: "placeholder",
    summary: "Use the existing Music Companion. No external project import is connected."
  }
];

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
    ["warning", "soft", "stale", "retry", "wait_for_approval", "paused"].includes(
      normalized
    )
  ) {
    return "warn";
  }

  if (["active", "running", "dispatch", "none", "low", "fresh"].includes(normalized)) {
    return "good";
  }

  if (["pass", "mock_data", "display_only", "not_connected", "not_evaluated"].includes(normalized)) {
    return "good";
  }

  return "neutral";
}

function metricTone(value, tone) {
  return value === "UNKNOWN" ? "neutral" : tone;
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

function MissionCard({ label, value, summary, tone = "neutral" }) {
  return (
    <article className={`missionCard ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{summary}</p>
    </article>
  );
}

function WorkerRoomCard({ label, status, summary, meta }) {
  return (
    <article className="workerRoomCard">
      <div className="operatorStatusTop">
        <h3>{label}</h3>
        <StatusPill value={status} />
      </div>
      <p>{summary}</p>
      <span>{meta}</span>
    </article>
  );
}

function PlaylistDock() {
  return (
    <section className="playlistDock" aria-labelledby="playlist-dock-title">
      <div className="operatorStatusIntro">
        <div>
          <p className="eyebrow">Companion dock</p>
          <h2 id="playlist-dock-title">Playlist Dock Intake</h2>
          <p>
            Placeholder-only intake for future references. This panel does not fetch
            private ChatGPT projects or connect external APIs.
          </p>
        </div>
        <a className="dockLink" href="/AIOS_MUSIC_COMPANION.html" target="_blank" rel="noreferrer">
          Open Music Companion
        </a>
      </div>
      <div className="playlistDockGrid">
        {playlistDockItems.map((item) => (
          <article className="dockItem" key={item.title}>
            <div className="operatorStatusTop">
              <h3>{item.title}</h3>
              <StatusPill value={item.status} />
            </div>
            <p>{item.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function UnavailableMessage({ children }) {
  return <p className="nextAction">{children}</p>;
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
          value={
            metrics.approval_needed ??
            autonomyBridgeState.approval_needed_count ??
            "UNKNOWN"
          }
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

export default function App() {
  const [runtimeVisibility, setRuntimeVisibility] = useState(mockVisibilityDisplay);
  const [visibilityLoading, setVisibilityLoading] = useState(true);
  const [packetFilter, setPacketFilter] = useState("all");
  const [eventQuery, setEventQuery] = useState("");

  useEffect(() => {
    const config = getRuntimeVisibilityClientConfig();
    fetchRuntimeVisibilityReadOnly(config)
      .then((result) => {
        setRuntimeVisibility(
          mapRuntimeVisibilityDisplayModel(result.data, { sourceLabel: result.sourceLabel })
        );
      })
      .catch(() => {
        // API unavailable: retain mock data already in state
      })
      .finally(() => setVisibilityLoading(false));
  }, []);

  const isLocalApiReadOnly =
    runtimeVisibility.sourceLabel === RUNTIME_VISIBILITY_SOURCE_LABELS.LOCAL_API_READ_ONLY;

  const filteredPackets = useMemo(() => {
    if (packetFilter === "all") {
      return runtimeVisibility.activePackets;
    }

    return runtimeVisibility.activePackets.filter(
      (packet) => packet.action === packetFilter
    );
  }, [packetFilter, runtimeVisibility.activePackets]);

  const filteredEvents = useMemo(() => {
    const query = eventQuery.trim().toLowerCase();

    if (!query) {
      return runtimeVisibility.telemetry.recentEvents;
    }

    return runtimeVisibility.telemetry.recentEvents.filter((event) =>
      [event.eventType, event.source, event.summary, event.packetId]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query))
    );
  }, [eventQuery, runtimeVisibility.telemetry.recentEvents]);

  const healthTone = runtimeVisibility.health.healthy ? "good" : "danger";
  const failedGroups = runtimeVisibility.failedPackets;
  const bridgeMetrics = autonomyBridgeCards[0]?.metrics ?? {};
  const winsCount = bridgeMetrics.wins ?? autonomyBridgeState.wins_count ?? "UNKNOWN";
  const blockedCount = bridgeMetrics.blocked ?? autonomyBridgeState.blocked_count ?? runtimeVisibility.executionLedger.blockedPacketCount;
  const approvalNeededCount =
    bridgeMetrics.approval_needed ??
    autonomyBridgeState.approval_needed_count ??
    runtimeVisibility.executionLedger.approvalCount;
  const passedCount = winsCount;
  const nightSupervisorStatus =
    autonomyBridgeState.night_supervisor_status ??
    autonomyBridgeState.supervisor_status ??
    "UNKNOWN";
  const nextSafeAction =
    autonomyBridgeState.next_safe_action ??
    runtimeVisibility.nextSafeAction ??
    "Review evidence before protected action.";
  const workerRooms = [
    {
      label: "Codex",
      status: runtimeVisibility.workers.length > 0 ? "tracked" : "evidence",
      summary: "Scoped engineering worker activity is shown as evidence only.",
      meta: `${runtimeVisibility.workers.length} runtime worker lease record(s)`
    },
    {
      label: "Claude",
      status: "review",
      summary: "Inspector and review lanes remain outside dashboard execution authority.",
      meta: `${autonomyBridgeState.worker_notes_count ?? "UNKNOWN"} worker note(s)`
    },
    {
      label: "Relay",
      status: approvalNeededCount === 0 ? "clear" : "needs_approval",
      summary: "Relay evidence is summarized for review, not approval automation.",
      meta: `${approvalNeededCount} approval-needed item(s)`
    },
    {
      label: "Night Supervisor",
      status: nightSupervisorStatus,
      summary: autonomyBridgeState.plain_summary ?? "Night Supervisor evidence unavailable.",
      meta: autonomyBridgeState.morning_digest_path ?? "No digest path available"
    }
  ];

  return (
    <div className="runtimePage">
      <header className="runtimeHeader">
        <div>
          <p className="eyebrow">AI_OS 24-hour operations</p>
          <h1>Operations Display</h1>
          <p className="summary">
            Read-only evidence view for worker activity, approvals, savepoints, and next safe action. Generated{" "}
            {formatTime(runtimeVisibility.generatedAt)}.
          </p>
        </div>
        <div className="headerStatus">
          <StatusPill value={runtimeVisibility.runtime.status} />
          <StatusPill value={`source: ${runtimeVisibility.sourceLabel}`} />
          <StatusPill value={`freshness: ${runtimeVisibility.runtime.freshness}`} />
          <StatusPill value={`backpressure: ${runtimeVisibility.backpressure.level}`} />
          {visibilityLoading && <StatusPill value="loading…" />}
        </div>
      </header>

      <section className="operationsHero" aria-labelledby="operations-summary-title">
        <div className="operatorStatusIntro">
          <div>
            <p className="eyebrow">Simple user mode</p>
            <h2 id="operations-summary-title">24-Hour Mission Summary</h2>
            <p>{autonomyBridgeState.plain_summary ?? "Runtime evidence is available for review."}</p>
          </div>
          <StatusPill value={nightSupervisorStatus} />
        </div>
        <div className="missionCardGrid">
          <MissionCard
            label="Worker activity"
            value={winsCount}
            summary="Completed or useful worker outputs seen in the latest evidence."
            tone="good"
          />
          <MissionCard
            label="Passed"
            value={passedCount}
            summary="Validated or completed evidence items, shown read-only."
            tone="good"
          />
          <MissionCard
            label="Blocked"
            value={blockedCount}
            summary="Items that must remain stopped until reviewed."
            tone={metricTone(blockedCount, "danger")}
          />
          <MissionCard
            label="Approvals waiting"
            value={approvalNeededCount}
            summary="Human-owner review required before protected actions."
            tone={metricTone(approvalNeededCount, "warn")}
          />
          <MissionCard
            label="Night Supervisor"
            value={nightSupervisorStatus}
            summary="Overnight supervision status from current evidence."
            tone={statusTone(nightSupervisorStatus)}
          />
          <MissionCard
            label="T9 savepoint"
            value="2026-06-02"
            summary="Checkpoint and resume evidence exist for the latest night run."
            tone="good"
          />
          <MissionCard
            label="Next safe action"
            value="review"
            summary={nextSafeAction}
            tone="warn"
          />
        </div>
      </section>

      <section className="workerRooms" aria-labelledby="worker-rooms-title">
        <div className="operatorStatusIntro">
          <div>
            <p className="eyebrow">Worker rooms</p>
            <h2 id="worker-rooms-title">Room Status</h2>
            <p>Readable worker state for review only. No launch, pause, approval, or mutation controls.</p>
          </div>
        </div>
        <div className="workerRoomGrid">
          {workerRooms.map((room) => (
            <WorkerRoomCard key={room.label} {...room} />
          ))}
        </div>
      </section>

      <section className="operatorStatusSlice" aria-labelledby="operator-status-title">
        <div className="operatorStatusIntro">
          <div>
            <p className="eyebrow">Operator status</p>
            <h2 id="operator-status-title">Display-Only Fixture</h2>
            <p>
              {operatorStatusFixture.provenance.classification}.{" "}
              {operatorStatusFixture.provenance.authority}.
            </p>
          </div>
          <div className="headerStatus">
            <StatusPill value={operatorStatusFixture.mode} />
            <StatusPill value={`source: ${operatorStatusFixture.source_label}`} />
            <StatusPill value={`schema: ${operatorStatusFixture.schema}`} />
          </div>
        </div>
        <div className="operatorStatusGrid">
          {operatorStatusPanels.map((panel) => (
            <OperatorStatusPanel key={panel.label} panel={panel} />
          ))}
        </div>
        <div className="warningStrip operatorWarnings">
          {operatorStatusFixture.warnings.map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      </section>

      <section className="autonomyBridgeSlice" aria-labelledby="autonomy-bridge-title">
        <div className="operatorStatusIntro">
          <div>
            <p className="eyebrow">Autonomy bridge</p>
            <h2 id="autonomy-bridge-title">Night Supervisor State</h2>
            <p>
              {autonomyBridgeState.plain_summary ??
                "Autonomy bridge state is unavailable."}
            </p>
          </div>
          <div className="headerStatus">
            <StatusPill value={autonomyBridgeSourceIsLive ? "LIVE" : "sample"} />
            <StatusPill value={`source: ${autonomyBridgeStatePayload.sourcePath}`} />
            <StatusPill value={`schema: ${autonomyBridgeState.schema ?? "UNKNOWN"}`} />
          </div>
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
      </section>

      <PlaylistDock />

      <details className="advancedTelemetry">
        <summary>
          <span>Advanced telemetry drill-down</span>
          <small>Runtime details, packet tables, worker leases, backpressure, and raw telemetry</small>
        </summary>
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
              <p>
                Allowed concurrent packets:{" "}
                {runtimeVisibility.backpressure.allowedConcurrentPackets}
              </p>
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
          </div>
          <div className="eventList">
            {filteredEvents.map((event) => (
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
              <Metric label="Blocked" value={runtimeVisibility.executionLedger.blockedPacketCount} tone="warn" />
              <Metric label="Applied" value={runtimeVisibility.executionLedger.appliedPacketCount} tone="good" />
            </div>
          )}
          <p className="nextAction">{runtimeVisibility.nextSafeAction}</p>
        </Section>
        </main>
      </details>
    </div>
  );
}
