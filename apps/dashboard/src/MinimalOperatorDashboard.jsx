import { useMemo, useState } from "react";
import dashboardFixture from "../mock-data/aios-minimal-operator-dashboard-v1.example.json";
import "./MinimalOperatorDashboard.css";

const VIEWS = {
  HOME: "home",
  FOREX: "forex",
  WATCHLIST: "watchlist",
  DETAIL: "detail"
};

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
      {!compact && !liveAllowed ? (
        <small>{source?.blockReason ?? "Data is blocked for live decisions."}</small>
      ) : null}
    </div>
  );
}

function Field({ label, value, tone, source = dataSourceForPair(), compact = false }) {
  return (
    <div className="field">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
      <DataLabel compact={compact} source={source} />
    </div>
  );
}

function ShellHeader({ view }) {
  return (
    <header className="dashboardHeader">
      <div>
        <p className="kicker">AIOS</p>
        <h1>{view === VIEWS.HOME ? "Operator" : "Forex Bot"}</h1>
      </div>
      <div className="headerBadges" aria-label="Dashboard safety labels">
        <StatusBadge value={dashboardFixture.mode} />
        <StatusBadge value={dashboardFixture.source} />
        <StatusBadge value={dashboardFixture.bridges.safeStatus} />
      </div>
    </header>
  );
}

function Breadcrumb({ view, selected, onNavigate }) {
  const crumbs = ["Home"];

  if (view !== VIEWS.HOME) {
    crumbs.push("Forex Bot");
  }

  if (view === VIEWS.WATCHLIST || view === VIEWS.DETAIL) {
    crumbs.push("Watchlist");
  }

  if (view === VIEWS.DETAIL) {
    crumbs.push(formatPair(selected.pair));
  }

  return (
    <nav className="breadcrumb" aria-label="Dashboard breadcrumb">
      {crumbs.map((crumb, index) => {
        const isLast = index === crumbs.length - 1;
        const target =
          crumb === "Home"
            ? VIEWS.HOME
            : crumb === "Forex Bot"
              ? VIEWS.FOREX
              : crumb === "Watchlist"
                ? VIEWS.WATCHLIST
                : VIEWS.DETAIL;

        return (
          <button
            aria-current={isLast ? "page" : undefined}
            className={isLast ? "activeCrumb" : ""}
            disabled={isLast}
            key={`${crumb}-${index}`}
            type="button"
            onClick={() => onNavigate(target)}
          >
            {crumb}
          </button>
        );
      })}
    </nav>
  );
}

function DoorCard({ title, detail, badge, onClick, actionLabel = "Open" }) {
  const content = (
    <>
      <span>{detail}</span>
      <strong>{title}</strong>
      {badge ? <StatusBadge value={badge} /> : null}
    </>
  );

  return (
    <article className={`doorCard ${onClick ? "interactiveDoorCard" : ""}`}>
      {content}
      {onClick ? (
        <button className="doorCardAction" type="button" onClick={onClick}>
          {actionLabel}
        </button>
      ) : null}
    </article>
  );
}

function HomeScreen({ onOpenForex }) {
  return (
    <section className="screen homeScreen" aria-label="Home">
      <div className="doorGrid">
        <DoorCard actionLabel="Open Forex Bot" detail="Open" title="Forex Bot" onClick={onOpenForex} />
        <DoorCard badge={dashboardFixture.mode} detail="System" title="Status" />
        <DoorCard badge={dashboardFixture.bridges.safeStatus} detail="Safety" title="Blocked" />
        <DoorCard badge={dashboardFixture.source} detail="Settings" title="Locked" />
      </div>
    </section>
  );
}

function ForexHub({ riskPl, exitReadiness, onBack, onOpenWatchlist }) {
  return (
    <section className="screen" aria-label="Forex Bot">
      <div className="screenTop">
        <button className="backButton" type="button" onClick={onBack}>
          Back
        </button>
        <h2>Forex Bot</h2>
      </div>

      <div className="hubGrid">
        <DoorCard actionLabel="Open Watchlist" detail="Open" title="Watchlist" onClick={onOpenWatchlist} />
        <DoorCard detail="Current Position" title={riskPl.currentPosition} />
        <DoorCard detail="Risk / P&L" title={riskPl.riskCap} />
        <DoorCard badge={exitReadiness.autoExitStatus} detail="Exit" title="Readiness" />
      </div>
    </section>
  );
}

function WatchlistScreen({ pairs, selectedPair, onBack, onViewPair }) {
  return (
    <section className="screen" aria-label="Watchlist">
      <div className="screenTop">
        <button className="backButton" type="button" onClick={onBack}>
          Back
        </button>
        <h2>Watchlist</h2>
      </div>

      <div className="watchlistList" role="list" aria-label="Ranked fixture pair watchlist">
        {pairs.map((pair) => {
          const selected = pair.pair === selectedPair;
          const source = dataSourceForPair(pair);

          return (
            <div className={`watchlistItem ${selected ? "selectedWatchlistItem" : ""}`} key={pair.pair}>
              <strong className="pairName">{formatPair(pair.pair)}</strong>
              <span className="scorePair">
                <span>Score</span>
                <strong>{pair.opportunityScore}</strong>
              </span>
              <span className="scorePair">
                <span>Confidence</span>
                <strong>{pair.confidence}</strong>
              </span>
              <StatusBadge value={pair.trend} />
              <DataLabel compact source={source} />
              <button
                className="viewButton"
                type="button"
                onClick={() => onViewPair(pair.pair)}
              >
                View
              </button>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function ChartPanel({ pair, source }) {
  const points = chartPolyline(pair.chart);

  return (
    <section className="panel chartPanel" aria-label={`${formatPair(pair.pair)} fixture chart`}>
      <div className="panelHeading">
        <p>Chart</p>
        <h3>{pair.fixturePrice}</h3>
      </div>
      <div className="chartShell">
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
      <DataLabel source={source} />
    </section>
  );
}

function AnalyticsPanel({ pair }) {
  const explanation = pair.explanation ?? {};

  return (
    <section className="panel" aria-label="Analytics">
      <div className="panelHeading">
        <p>Analytics</p>
        <h3>Opportunity</h3>
      </div>
      <p className="shortText">{explanation.rankingReason ?? pair.reason}</p>
      <div className="miniGrid">
        <StatusBadge value={pair.supertrend} />
        <StatusBadge value={explanation.spreadSlippageStatus ?? "UNVERIFIED_FIXTURE"} />
      </div>
    </section>
  );
}

function RiskPanel({ riskPl }) {
  const source = dataSourceForPair();

  return (
    <section className="panel" aria-label="Risk and P/L">
      <div className="panelHeading">
        <p>Risk</p>
        <h3>P/L</h3>
      </div>
      <div className="fieldGrid">
        <Field compact label="Realized" source={source} value={riskPl.realizedPl} tone="neutral" />
        <Field compact label="Unrealized" source={source} value={riskPl.unrealizedPl} tone="neutral" />
        <Field compact label="Cap" source={source} value={riskPl.riskCap} tone="warn" />
        <Field compact label="Position" source={source} value={riskPl.currentPosition} tone="neutral" />
      </div>
    </section>
  );
}

function ExitPanel({ exitReadiness }) {
  const source = dataSourceForPair();

  return (
    <section className="panel" aria-label="Exit readiness">
      <div className="panelHeading">
        <p>Exit</p>
        <h3>{exitReadiness.autoExitStatus}</h3>
      </div>
      <div className="controlList">
        {exitReadiness.controls.map((control) => (
          <div className="controlRow" key={control.label}>
            <span>{control.label}</span>
            <StatusBadge value={control.status} />
          </div>
        ))}
      </div>
      <DataLabel compact source={source} />
    </section>
  );
}

function DecisionPanel({ pair, bridges, exitReadiness }) {
  const source = dataSourceForPair(pair);
  const explanation = pair.explanation ?? {};

  return (
    <section className="panel decisionPanel" aria-label="Decision">
      <div className="panelHeading">
        <p>Decision</p>
        <h3>{explanation.safeDecision ?? bridges.safeStatus}</h3>
      </div>
      <p className="shortText">{explanation.nextSafeAction ?? bridges.nextAction}</p>
      <p className="shortText">{explanation.blockReason ?? exitReadiness.blockReason}</p>
      <DataLabel source={source} />
    </section>
  );
}

function PairDetail({ pair, riskPl, exitReadiness, bridges, onBack }) {
  const source = dataSourceForPair(pair);

  return (
    <section className="screen detailScreen" aria-label="Pair Detail">
      <div className="screenTop">
        <button className="backButton" type="button" onClick={onBack}>
          Back
        </button>
        <h2>{formatPair(pair.pair)}</h2>
        <StatusBadge value={bridges.safeStatus} />
      </div>

      <div className="detailGrid">
        <section className="panel pricePanel" aria-label="Price">
          <div className="panelHeading">
            <p>Price</p>
            <h3>{pair.fixturePrice}</h3>
          </div>
          <div className="miniGrid">
            <StatusBadge value={pair.trend} />
            <StatusBadge value={pair.session} />
          </div>
          <DataLabel source={source} />
        </section>
        <ChartPanel pair={pair} source={source} />
        <AnalyticsPanel pair={pair} />
        <RiskPanel riskPl={riskPl} />
        <ExitPanel exitReadiness={exitReadiness} />
        <DecisionPanel bridges={bridges} exitReadiness={exitReadiness} pair={pair} />
      </div>
    </section>
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
  const [view, setView] = useState(VIEWS.HOME);
  const [selectedPair, setSelectedPair] = useState(dashboardFixture.selectedPair);
  const selected = pairs.find((pair) => pair.pair === selectedPair) ?? pairs[0];

  function openPair(pair) {
    setSelectedPair(pair);
    setView(VIEWS.DETAIL);
  }

  return (
    <main className="minimalOperatorDashboard">
      <ShellHeader view={view} />
      <Breadcrumb selected={selected} view={view} onNavigate={setView} />

      {view === VIEWS.HOME ? <HomeScreen onOpenForex={() => setView(VIEWS.FOREX)} /> : null}

      {view === VIEWS.FOREX ? (
        <ForexHub
          exitReadiness={dashboardFixture.exitReadiness}
          riskPl={dashboardFixture.riskPl}
          onBack={() => setView(VIEWS.HOME)}
          onOpenWatchlist={() => setView(VIEWS.WATCHLIST)}
        />
      ) : null}

      {view === VIEWS.WATCHLIST ? (
        <WatchlistScreen
          pairs={pairs}
          selectedPair={selected.pair}
          onBack={() => setView(VIEWS.FOREX)}
          onViewPair={openPair}
        />
      ) : null}

      {view === VIEWS.DETAIL ? (
        <PairDetail
          bridges={dashboardFixture.bridges}
          exitReadiness={dashboardFixture.exitReadiness}
          pair={selected}
          riskPl={dashboardFixture.riskPl}
          onBack={() => setView(VIEWS.WATCHLIST)}
        />
      ) : null}
    </main>
  );
}
