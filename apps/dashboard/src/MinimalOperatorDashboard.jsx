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

function dataSourceForPair(pair) {
  return {
    label:
      pair?.explanation?.dataSourceLabel ??
      dashboardFixture.dataSource?.DISPLAY_LABEL ??
      dashboardFixture.source ??
      "UNVERIFIED",
    liveTradingAllowed:
      pair?.explanation?.liveTradingAllowedFromThisData ??
      dashboardFixture.dataSource?.LIVE_TRADING_ALLOWED_FROM_THIS_DATA ??
      false,
    blockReason:
      pair?.explanation?.blockReason ??
      dashboardFixture.dataSource?.BLOCK_REASON ??
      "Source permission is not approved for live trade decisions."
  };
}

function DataLabel({ source, compact = false }) {
  const liveAllowed = Boolean(source?.liveTradingAllowed);

  return (
    <div className={`dataLabel ${compact ? "compactLabel" : ""}`}>
      <StatusBadge value={source?.label ?? "UNVERIFIED"} />
      <span>{`LIVE_TRADING_ALLOWED_FROM_THIS_DATA: ${String(liveAllowed)}`}</span>
      {!liveAllowed ? <small>{source?.blockReason ?? "Data is blocked for live decisions."}</small> : null}
    </div>
  );
}

function LabeledValue({ value, source, strong = false }) {
  const ValueTag = strong ? "strong" : "span";

  return (
    <div className="labeledValue">
      <ValueTag>{value}</ValueTag>
      <DataLabel compact source={source} />
    </div>
  );
}

function Field({ label, value, tone, source = dataSourceForPair() }) {
  return (
    <div className="field">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
      <DataLabel compact source={source} />
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
              <th>Price</th>
              <th>Score</th>
              <th>Confidence</th>
              <th>Trend</th>
              <th>Supertrend</th>
              <th>Volatility</th>
              <th>Session</th>
              <th>Updated</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {pairs.map((pair) => {
              const selected = pair.pair === selectedPair;
              const source = dataSourceForPair(pair);

              return (
                <tr className={selected ? "selectedRow" : ""} key={pair.pair}>
                  <td>{pair.rank}</td>
                  <td>
                    <LabeledValue source={source} strong value={formatPair(pair.pair)} />
                    {selected ? <span className="selectedMark">Selected</span> : null}
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.fixturePrice} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.opportunityScore} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.confidence} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.trend} />
                  </td>
                  <td>
                    <StatusBadge value={pair.supertrend} />
                    <DataLabel compact source={source} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.volatility} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={pair.session} />
                  </td>
                  <td>
                    <LabeledValue source={source} value={formatTime(pair.lastUpdated)} />
                  </td>
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
  const source = dataSourceForPair(pair);

  return (
    <Panel title="Selected Pair / Chart Data" eyebrow="Fixture chart handoff">
      <div className="selectedPairHeader">
        <div>
          <span>Selected pair</span>
          <strong>{formatPair(pair.pair)}</strong>
          <DataLabel source={source} />
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
        <DataLabel source={source} />
      </div>

      <div className="fieldGrid">
        <Field label="Fixture price" source={source} value={pair.fixturePrice} tone="neutral" />
        <Field label="Trend direction" source={source} value={pair.trend} />
        <Field label="Volatility" source={source} value={pair.volatility} />
        <Field label="Session" source={source} value={pair.session} tone="neutral" />
      </div>

      <div className="explanationBox">
        <span>AIOS explanation</span>
        <p>{pair.reason}</p>
      </div>
    </Panel>
  );
}

function FactorList({ title, items, tone = "neutral" }) {
  return (
    <div className={`factorList factor-${tone}`}>
      <h3>{title}</h3>
      <ul>
        {(items ?? ["UNKNOWN"]).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function OpportunityExplanationPanel({ pair, riskPl, exitReadiness, bridges }) {
  const explanation = pair.explanation ?? {};
  const source = dataSourceForPair(pair);
  const dataSourceLabel = source.label;
  const liveTradingAllowed = Boolean(source.liveTradingAllowed);

  return (
    <Panel title="Opportunity Explanation" eyebrow="AIOS selected-pair reasoning" className="opportunityPanel">
      <div className="explanationHeader">
        <div>
          <span>Selected pair</span>
          <strong>{formatPair(pair.pair)}</strong>
          <DataLabel source={source} />
        </div>
        <div className="headerBadges">
          <StatusBadge value={dataSourceLabel} />
          <StatusBadge value={liveTradingAllowed ? "LIVE_DATA_ALLOWED" : "LIVE_DATA_BLOCKED"} />
        </div>
      </div>

      <div className="fieldGrid compact">
        <Field label="Opportunity score" source={source} value={pair.opportunityScore} tone="good" />
        <Field label="Confidence score" source={source} value={pair.confidence} tone="good" />
        <Field label="Supertrend" source={source} value={pair.supertrend ?? "UNKNOWN"} />
        <Field label="Volatility" source={source} value={pair.volatility ?? "UNKNOWN"} />
        <Field label="Session" source={source} value={pair.session ?? "UNKNOWN"} tone="neutral" />
        <Field
          label="Spread / slippage"
          source={source}
          value={explanation.spreadSlippageStatus ?? "UNVERIFIED_FIXTURE"}
        />
        <Field label="P/L readiness" source={source} value={explanation.plReadiness ?? "BLOCKED_FIXTURE"} />
        <Field label="Exit readiness" source={source} value={explanation.exitReadiness ?? exitReadiness.autoExitStatus} />
      </div>

      <div className="rankReason">
        <span>Why AIOS ranked this pair</span>
        <p>{explanation.rankingReason ?? pair.reason}</p>
      </div>

      <div className="factorGrid">
        <FactorList title="Bullish factors" items={explanation.bullishFactors} tone="good" />
        <FactorList title="Bearish / risk factors" items={explanation.riskFactors} tone="danger" />
      </div>

      <div className="decisionGrid">
        <Field label="Safe / blocked decision" source={source} value={explanation.safeDecision ?? bridges.safeStatus} />
        <Field label="Current position" source={source} value={riskPl.currentPosition} tone="neutral" />
      </div>

      <div className="blockReason">
        <span>Block reason</span>
        <p>{explanation.blockReason ?? exitReadiness.blockReason}</p>
      </div>

      <div className="nextAction">
        <span>Next safe action</span>
        <p>{explanation.nextSafeAction ?? bridges.nextAction}</p>
      </div>
    </Panel>
  );
}

function RiskPlPanel({ riskPl }) {
  const source = dataSourceForPair();

  return (
    <Panel title="Risk / P&L" eyebrow="Sanitized fixture values">
      <div className="fieldGrid">
        <Field label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
        <Field label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
        <Field label="Risk cap" source={source} value={riskPl.riskCap} tone="warn" />
        <Field label="Position size" source={source} value={riskPl.positionSize} tone="warn" />
        <Field label="Current position" source={source} value={riskPl.currentPosition} tone="neutral" />
      </div>
    </Panel>
  );
}

function ExitReadinessPanel({ exitReadiness }) {
  const source = dataSourceForPair();

  return (
    <Panel title="Exit Readiness" eyebrow="Entry blocked without exit plan">
      <div className="readinessSummary">
        <span>Auto-exit status</span>
        <div className="labeledValue">
          <StatusBadge value={exitReadiness.autoExitStatus} />
          <DataLabel compact source={source} />
        </div>
      </div>
      <div className="controlList">
        {exitReadiness.controls.map((control) => (
          <div className="controlRow" key={control.label}>
            <span>{control.label}</span>
            <div className="labeledValue">
              <StatusBadge value={control.status} />
              <DataLabel compact source={source} />
            </div>
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
  const source = dataSourceForPair();

  return (
    <Panel title="Bridges / Safety" eyebrow="Fail-closed summary">
      <div className="fieldGrid">
        <Field label="Secret bridge" source={source} value={bridges.secretBridge} />
        <Field label="Broker bridge" source={source} value={bridges.brokerBridge} />
        <Field label="Kill switch" source={source} value={bridges.killSwitch} />
        <Field label="Safe / blocked" source={source} value={bridges.safeStatus} />
        <Field label="SOS" source={source} value={bridges.sos} tone="neutral" />
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
  const selectedSource = dataSourceForPair(selected);

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
        <Field label="Selected pair" source={selectedSource} value={formatPair(selected.pair)} tone="neutral" />
        <Field label="Opportunity score" source={selectedSource} value={selected.opportunityScore} tone="good" />
        <Field label="Confidence" source={selectedSource} value={selected.confidence} tone="good" />
        <Field label="Last update" source={selectedSource} value={formatTime(selected.lastUpdated)} tone="neutral" />
      </section>

      <div className="dashboardGrid">
        <section className="primaryWorkArea" aria-label="Pair selection and explanation">
          <Watchlist pairs={pairs} selectedPair={selected.pair} onSelectPair={setSelectedPair} />
          <div className="analysisStack">
            <SelectedPairPanel pair={selected} />
            <OpportunityExplanationPanel
              bridges={dashboardFixture.bridges}
              exitReadiness={dashboardFixture.exitReadiness}
              pair={selected}
              riskPl={dashboardFixture.riskPl}
            />
          </div>
        </section>

        <section className="safetyWorkArea" aria-label="Risk, exit, and bridge safety">
          <RiskPlPanel riskPl={dashboardFixture.riskPl} />
          <ExitReadinessPanel exitReadiness={dashboardFixture.exitReadiness} />
          <BridgeSafetyPanel bridges={dashboardFixture.bridges} />
        </section>

        <div className="workflowCompact">
          <WorkflowPanel workflow={dashboardFixture.workflow} />
        </div>
      </div>
    </main>
  );
}
