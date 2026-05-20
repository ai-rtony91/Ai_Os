import { useMemo, useState } from "react";
import mockRuntimeVisibility from "../mock-data/aios-runtime-visibility-v1.example.json";
import {
  RUNTIME_VISIBILITY_SOURCE_LABELS,
  mapRuntimeVisibilityDisplayModel
} from "./runtimeVisibilityAdapter";
import "./App.css";

const packetFilters = ["all", "dispatch", "wait_for_approval", "retry", "manual_review"];
const runtimeVisibility = mapRuntimeVisibilityDisplayModel(mockRuntimeVisibility, {
  sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA
});

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

  return "neutral";
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

export default function App() {
  const [packetFilter, setPacketFilter] = useState("all");
  const [eventQuery, setEventQuery] = useState("");

  const filteredPackets = useMemo(() => {
    if (packetFilter === "all") {
      return runtimeVisibility.activePackets;
    }

    return runtimeVisibility.activePackets.filter(
      (packet) => packet.action === packetFilter
    );
  }, [packetFilter]);

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
  }, [eventQuery]);

  const healthTone = runtimeVisibility.health.healthy ? "good" : "danger";
  const failedGroups = runtimeVisibility.failedPackets;

  return (
    <div className="runtimePage">
      <header className="runtimeHeader">
        <div>
          <p className="eyebrow">AI_OS runtime visibility</p>
          <h1>Runtime Operations</h1>
          <p className="summary">
            Local-first, paper-only execution visibility. Generated{" "}
            {formatTime(runtimeVisibility.generatedAt)}.
          </p>
        </div>
        <div className="headerStatus">
          <StatusPill value={runtimeVisibility.runtime.status} />
          <StatusPill value={`freshness: ${runtimeVisibility.runtime.freshness}`} />
          <StatusPill value={`backpressure: ${runtimeVisibility.backpressure.level}`} />
        </div>
      </header>

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
            <Metric label="Expired workers" value={runtimeVisibility.health.expiredWorkers} tone="danger" />
            <Metric label="Poison packets" value={runtimeVisibility.health.poisonPackets} tone="danger" />
            <Metric label="Retryable packets" value={runtimeVisibility.health.retryablePackets} tone="warn" />
            <Metric label="Reclaimable" value={runtimeVisibility.health.reclaimablePackets} tone="warn" />
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
          }
        >
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
        </Section>

        <Section title="Failed Packets">
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
        </Section>

        <Section title="Worker Leases">
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
            {Object.entries(runtimeVisibility.backpressure.pressureInputs).map(([key, value]) => (
              <Metric key={key} label={key} value={value} />
            ))}
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
          <div className="ledgerSummary">
            <Metric label="Packets" value={runtimeVisibility.executionLedger.packetCount} />
            <Metric label="Approvals" value={runtimeVisibility.executionLedger.approvalCount} />
            <Metric label="Blocked" value={runtimeVisibility.executionLedger.blockedPacketCount} tone="warn" />
            <Metric label="Applied" value={runtimeVisibility.executionLedger.appliedPacketCount} tone="good" />
          </div>
          <p className="nextAction">{runtimeVisibility.nextSafeAction}</p>
        </Section>
      </main>
    </div>
  );
}
