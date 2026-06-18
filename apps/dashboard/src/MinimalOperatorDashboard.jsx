import { useMemo, useState } from "react";
import dashboardFixture from "../mock-data/aios-minimal-operator-dashboard-v1.example.json";
import "./MinimalOperatorDashboard.css";

function statusTone(value) {
  const text = String(value ?? "").toUpperCase();

  if (text.includes("BLOCKED") || text.includes("MISSING") || text.includes("FALSE")) {
    return "danger";
  }

  if (
    text.includes("FIXTURE") ||
    text.includes("LOCKED") ||
    text.includes("REVIEW") ||
    text.includes("NEUTRAL")
  ) {
    return "warn";
  }

  if (
    text.includes("PRESENT") ||
    text.includes("BULLISH") ||
    text.includes("READY") ||
    text.includes("READ_ONLY")
  ) {
    return "good";
  }

  return "neutral";
}

function formatPair(pair) {
  return String(pair ?? "UNKNOWN").replace("_", "/");
}

function formatTime(value) {
  if (!value) {
    return "UNKNOWN";
  }

  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function chartPolyline(points) {
  if (!Array.isArray(points) || points.length === 0) {
    return "";
  }

  const width = 340;
  const height = 132;
  const pad = 14;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const spread = max - min || 1;

  return points
    .map((point, index) => {
      const x = pad + (index * (width - pad * 2)) / Math.max(points.length - 1, 1);
      const y = height - pad - ((point - min) / spread) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function StatusBadge({ value }) {
  return <span className={`statusBadge status-${statusTone(value)}`}>{value}</span>;
}

function Field({ label, value, tone }) {
  return (
    <div className="field">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
    </div>
  );
}

function Panel({ title, eyebrow, children, className = "" }) {
  return (
    <section className={`operatorPanel ${className}`.trim()}>
      <div className="panelHeading">
        {eyebrow ? <p>{eyebrow}</p> : null}
        <h2>{title}</h2>
      </div>
      {children}
    </section>
  );
}

function Watchlist({ pairs, selectedPair, onSelectPair }) {
  return (
    <Panel title="Watchlist" eyebrow="Ranked opportunities" className="watchlistPanel">
      <div className="tableShell" role="region" aria-label="Ranked fixture pair watchlist">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Pair</th>
              <th>Score</th>
              <th>Confidence</th>
              <th>Trend</th>
              <th>Supertrend</th>
              <th>Updated</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {pairs.map((pair) => {
              const selected = pair.pair === selectedPair;

              return (
                <tr className={selected ? "selectedRow" : ""} key={pair.pair}>
                  <td>{pair.rank}</td>
                  <td>
                    <strong>{formatPair(pair.pair)}</strong>
                    {selected ? <span className="selectedMark">Selected</span> : null}
                  </td>
                  <td>{pair.opportunityScore}</td>
                  <td>{pair.confidence}</td>
                  <td>{pair.trend}</td>
                  <td>
                    <StatusBadge value={pair.supertrend} />
                  </td>
                  <td>{formatTime(pair.lastUpdated)}</td>
                  <td>
                    <button
                      className="viewButton"
                      type="button"
                      onClick={() => onSelectPair(pair.pair)}
                    >
                      View Chart
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function SelectedPairPanel({ pair }) {
  const points = chartPolyline(pair.chart);

  return (
    <Panel title="Selected Pair / Chart Data" eyebrow="Fixture chart handoff">
      <div className="selectedPairHeader">
        <div>
          <span>Selected pair</span>
          <strong>{formatPair(pair.pair)}</strong>
        </div>
        <StatusBadge value="FIXTURE_NOT_LIVE" />
      </div>

      <div className="chartShell" aria-label={`${formatPair(pair.pair)} fixture chart`}>
        <svg viewBox="0 0 340 132" role="img" aria-label="Fixture price line">
          <polyline className="chartGridLine" points="14,104 326,104" />
          <polyline className="chartGridLine" points="14,66 326,66" />
          <polyline className="chartGridLine" points="14,28 326,28" />
          <polyline className="chartLine" points={points} />
          {pair.chart.map((point, index) => (
            <circle
              className="chartPoint"
              cx={14 + (index * 312) / Math.max(pair.chart.length - 1, 1)}
              cy={
                118 -
                ((point - Math.min(...pair.chart)) /
                  (Math.max(...pair.chart) - Math.min(...pair.chart) || 1)) *
                  104
              }
              key={`${pair.pair}-${point}-${index}`}
              r="3"
            />
          ))}
        </svg>
      </div>

      <div className="fieldGrid">
        <Field label="Fixture price" value={pair.fixturePrice} tone="neutral" />
        <Field label="Trend direction" value={pair.trend} />
        <Field label="Volatility" value={pair.volatility} />
        <Field label="Session" value={pair.session} tone="neutral" />
      </div>

      <div className="explanationBox">
        <span>AIOS explanation</span>
        <p>{pair.reason}</p>
      </div>
    </Panel>
  );
}

function RiskPlPanel({ riskPl }) {
  return (
    <Panel title="Risk / P&L" eyebrow="Sanitized fixture values">
      <div className="fieldGrid">
        <Field label="Realized P/L" value={riskPl.realizedPl} tone="neutral" />
        <Field label="Unrealized P/L" value={riskPl.unrealizedPl} tone="neutral" />
        <Field label="Risk cap" value={riskPl.riskCap} tone="warn" />
        <Field label="Position size" value={riskPl.positionSize} tone="warn" />
        <Field label="Current position" value={riskPl.currentPosition} tone="neutral" />
      </div>
    </Panel>
  );
}

function ExitReadinessPanel({ exitReadiness }) {
  return (
    <Panel title="Exit Readiness" eyebrow="Entry blocked without exit plan">
      <div className="readinessSummary">
        <span>Auto-exit status</span>
        <StatusBadge value={exitReadiness.autoExitStatus} />
      </div>
      <div className="controlList">
        {exitReadiness.controls.map((control) => (
          <div className="controlRow" key={control.label}>
            <span>{control.label}</span>
            <StatusBadge value={control.status} />
          </div>
        ))}
      </div>
      <div className="blockReason">
        <span>Block reason</span>
        <p>{exitReadiness.blockReason}</p>
      </div>
    </Panel>
  );
}

function BridgeSafetyPanel({ bridges }) {
  return (
    <Panel title="Bridges / Safety" eyebrow="Fail-closed summary">
      <div className="fieldGrid">
        <Field label="Secret bridge" value={bridges.secretBridge} />
        <Field label="Broker bridge" value={bridges.brokerBridge} />
        <Field label="Kill switch" value={bridges.killSwitch} />
        <Field label="Safe / blocked" value={bridges.safeStatus} />
        <Field label="SOS" value={bridges.sos} tone="neutral" />
      </div>
      <div className="nextAction">
        <span>Next action</span>
        <p>{bridges.nextAction}</p>
      </div>
    </Panel>
  );
}

function WorkflowPanel({ workflow }) {
  return (
    <Panel title="Operator Workflow" eyebrow="Read-only gate sequence">
      <ol className="workflowList">
        {workflow.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
    </Panel>
  );
}

export default function MinimalOperatorDashboard() {
  const pairs = useMemo(
    () =>
      [...dashboardFixture.watchlist].sort(
        (a, b) => b.opportunityScore - a.opportunityScore || b.confidence - a.confidence
      ),
    []
  );
  const [selectedPair, setSelectedPair] = useState(dashboardFixture.selectedPair);
  const selected = pairs.find((pair) => pair.pair === selectedPair) ?? pairs[0];

  return (
    <main className="minimalOperatorDashboard">
      <header className="dashboardHeader">
        <div>
          <p className="kicker">AIOS Minimal Operator Dashboard</p>
          <h1>Forex Control View</h1>
          <p>
            Read-only vertical slice for watchlist ranking, pair review, P/L visibility,
            exit readiness, and bridge safety.
          </p>
        </div>
        <div className="headerBadges" aria-label="Dashboard safety labels">
          <StatusBadge value={dashboardFixture.mode} />
          <StatusBadge value={dashboardFixture.source} />
          <StatusBadge value={dashboardFixture.bridges.safeStatus} />
        </div>
      </header>

      <section className="statusBand" aria-label="Current dashboard status">
        <Field label="Selected pair" value={formatPair(selected.pair)} tone="neutral" />
        <Field label="Opportunity score" value={selected.opportunityScore} tone="good" />
        <Field label="Confidence" value={selected.confidence} tone="good" />
        <Field label="Last update" value={formatTime(selected.lastUpdated)} tone="neutral" />
      </section>

      <div className="dashboardGrid">
        <Watchlist pairs={pairs} selectedPair={selected.pair} onSelectPair={setSelectedPair} />
        <SelectedPairPanel pair={selected} />
        <RiskPlPanel riskPl={dashboardFixture.riskPl} />
        <ExitReadinessPanel exitReadiness={dashboardFixture.exitReadiness} />
        <BridgeSafetyPanel bridges={dashboardFixture.bridges} />
        <WorkflowPanel workflow={dashboardFixture.workflow} />
      </div>
    </main>
  );
}
