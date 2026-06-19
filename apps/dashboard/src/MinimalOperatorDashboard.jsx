import { useMemo, useState } from "react";
import dashboardFixture from "../mock-data/aios-minimal-operator-dashboard-v1.example.json";
import "./MinimalOperatorDashboard.css";

const VIEWS = {
  HOME: "home",
  FOREX: "forex",
  WATCHLIST: "watchlist",
  DETAIL: "detail",
  SYSTEM: "system",
  SAFETY: "safety",
  SETTINGS: "settings",
  POSITION: "position",
  RISK: "risk",
  EXIT: "exit"
};

const ICONS = {
  operator: "🎛️",
  forex: "🤖",
  system: "🖥️",
  safety: "🛡️",
  settings: "⚙️",
  watchlist: "🎯",
  position: "📍",
  risk: "📊",
  exit: "⏏️",
  detail: "🔎",
  price: "💱",
  chart: "📈",
  analytics: "🧠",
  decision: "⚖️",
  ready: "✅",
  blocked: "⛔",
  fixture: "🧪",
  locked: "🔒",
  readOnly: "👁️",
  hidden: "🕶️",
  killSwitch: "⏻"
};

const VIEW_LABELS = {
  [VIEWS.HOME]: "Operator",
  [VIEWS.FOREX]: "Forex Bot",
  [VIEWS.WATCHLIST]: "Watchlist",
  [VIEWS.DETAIL]: "Pair Detail",
  [VIEWS.SYSTEM]: "System",
  [VIEWS.SAFETY]: "Safety",
  [VIEWS.SETTINGS]: "Settings",
  [VIEWS.POSITION]: "Position",
  [VIEWS.RISK]: "Risk / P&L",
  [VIEWS.EXIT]: "Exit"
};

const VIEW_ICONS = {
  [VIEWS.HOME]: ICONS.operator,
  [VIEWS.FOREX]: ICONS.forex,
  [VIEWS.WATCHLIST]: ICONS.watchlist,
  [VIEWS.DETAIL]: ICONS.detail,
  [VIEWS.SYSTEM]: ICONS.system,
  [VIEWS.SAFETY]: ICONS.safety,
  [VIEWS.SETTINGS]: ICONS.settings,
  [VIEWS.POSITION]: ICONS.position,
  [VIEWS.RISK]: ICONS.risk,
  [VIEWS.EXIT]: ICONS.exit
};

const FOREX_CHILD_VIEWS = new Set([
  VIEWS.WATCHLIST,
  VIEWS.DETAIL,
  VIEWS.POSITION,
  VIEWS.RISK,
  VIEWS.EXIT
]);

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

function statusIcon(value) {
  const text = String(value ?? "").toUpperCase();

  if (text.includes("BLOCKED") || text.includes("MISSING") || text === "FALSE") {
    return ICONS.blocked;
  }

  if (text.includes("FIXTURE")) {
    return ICONS.fixture;
  }

  if (text.includes("LOCKED")) {
    return ICONS.locked;
  }

  if (text.includes("READ_ONLY")) {
    return ICONS.readOnly;
  }

  if (text.includes("READY") || text.includes("PRESENT")) {
    return ICONS.ready;
  }

  if (text.includes("HIDDEN") || text.includes("NO_SECRETS") || text.includes("NOT_DISPLAYED")) {
    return ICONS.hidden;
  }

  return null;
}

function viewLabel(view) {
  return VIEW_LABELS[view] ?? "Dashboard";
}

function viewIcon(view) {
  return VIEW_ICONS[view] ?? ICONS.operator;
}

function IconLabel({ icon, label, className = "" }) {
  return (
    <span className={["iconLabel", className].filter(Boolean).join(" ")}>
      <span aria-hidden="true" className="iconGlyph">
        {icon}
      </span>
      <span>{label}</span>
    </span>
  );
}

function BackButton({ onClick }) {
  return (
    <button aria-label="Back" className="backButton iconOnlyButton" title="Back" type="button" onClick={onClick}>
      <span aria-hidden="true">←</span>
    </button>
  );
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
  const icon = statusIcon(value);

  return (
    <span className={`statusBadge status-${statusTone(value)}`}>
      {icon ? (
        <span aria-hidden="true" className="statusBadgeIcon">
          {icon}
        </span>
      ) : null}
      <span>{value}</span>
    </span>
  );
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
        <h1>
          <IconLabel icon={viewIcon(view)} label={viewLabel(view)} />
        </h1>
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
  const crumbs = [{ label: "Home", icon: ICONS.operator }];

  if (view === VIEWS.FOREX || FOREX_CHILD_VIEWS.has(view)) {
    crumbs.push({ label: "Forex Bot", icon: ICONS.forex });
  }

  if (view === VIEWS.WATCHLIST || view === VIEWS.DETAIL) {
    crumbs.push({ label: "Watchlist", icon: ICONS.watchlist });
  }

  if (view === VIEWS.DETAIL) {
    crumbs.push({ label: formatPair(selected.pair), icon: ICONS.detail, showLabel: true });
  } else if (view !== VIEWS.HOME && view !== VIEWS.FOREX && view !== VIEWS.WATCHLIST) {
    crumbs.push({ label: viewLabel(view), icon: viewIcon(view) });
  }

  return (
    <nav className="breadcrumb" aria-label="Dashboard breadcrumb">
      {crumbs.map((crumb, index) => {
        const isLast = index === crumbs.length - 1;
        const target =
          crumb.label === "Home"
            ? VIEWS.HOME
            : crumb.label === "Forex Bot"
              ? VIEWS.FOREX
              : crumb.label === "Watchlist"
                ? VIEWS.WATCHLIST
                : view;

        return (
          <button
            aria-current={isLast ? "page" : undefined}
            aria-label={crumb.label}
            className={isLast ? "activeCrumb" : ""}
            disabled={isLast}
            key={`${crumb.label}-${index}`}
            title={crumb.label}
            type="button"
            onClick={() => onNavigate(target)}
          >
            <span aria-hidden="true">{crumb.icon}</span>
            {crumb.showLabel ? <span>{crumb.label}</span> : null}
          </button>
        );
      })}
    </nav>
  );
}

function DoorCard({ title, icon, onClick, disabled = false }) {
  const content = (
    <span aria-hidden="true" className="doorCardIconOnly">
      {icon}
    </span>
  );

  if (onClick && !disabled) {
    return (
      <button
        aria-label={title}
        className="doorCard interactiveDoorCard"
        title={title}
        type="button"
        onClick={onClick}
      >
        {content}
      </button>
    );
  }

  return (
    <div
      aria-label={title}
      className={`doorCard ${disabled ? "disabledDoorCard" : ""}`}
      title={title}
    >
      {content}
    </div>
  );
}

function PairViewButton({ pair, onViewPair }) {
  const label = `View ${formatPair(pair)} details`;

  return (
    <button
      aria-label={label}
      className="viewButton iconOnlyButton"
      title={label}
      type="button"
      onClick={() => onViewPair(pair)}
    >
      <span aria-hidden="true">{ICONS.detail}</span>
    </button>
  );
}

function HomeScreen({ onNavigate }) {
  return (
    <section className="screen homeScreen" aria-label="Home">
      <div className="doorGrid">
        <DoorCard icon={ICONS.forex} title="Forex Bot" onClick={() => onNavigate(VIEWS.FOREX)} />
        <DoorCard icon={ICONS.system} title="System" onClick={() => onNavigate(VIEWS.SYSTEM)} />
        <DoorCard
          icon={ICONS.safety}
          title="Safety"
          onClick={() => onNavigate(VIEWS.SAFETY)}
        />
        <DoorCard
          icon={ICONS.settings}
          title="Settings"
          onClick={() => onNavigate(VIEWS.SETTINGS)}
        />
      </div>
    </section>
  );
}

function ForexHub({ onBack, onNavigate }) {
  return (
    <section className="screen" aria-label="Forex Bot">
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>
          <IconLabel icon={ICONS.forex} label="Forex Bot" />
        </h2>
      </div>

      <div className="hubGrid">
        <DoorCard icon={ICONS.watchlist} title="Watchlist" onClick={() => onNavigate(VIEWS.WATCHLIST)} />
        <DoorCard icon={ICONS.position} title="Position" onClick={() => onNavigate(VIEWS.POSITION)} />
        <DoorCard icon={ICONS.risk} title="Risk / P&L" onClick={() => onNavigate(VIEWS.RISK)} />
        <DoorCard
          icon={ICONS.exit}
          title="Exit"
          onClick={() => onNavigate(VIEWS.EXIT)}
        />
      </div>
    </section>
  );
}

function WatchlistScreen({ pairs, selectedPair, onBack, onViewPair }) {
  return (
    <section className="screen" aria-label="Watchlist">
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>
          <IconLabel icon={ICONS.watchlist} label="Watchlist" />
        </h2>
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
              <PairViewButton pair={pair.pair} onViewPair={onViewPair} />
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
        <p>
          <IconLabel icon={ICONS.chart} label="Chart" />
        </p>
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
        <p>
          <IconLabel icon={ICONS.analytics} label="Analytics" />
        </p>
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
        <p>
          <IconLabel icon={ICONS.risk} label="Risk" />
        </p>
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
        <p>
          <IconLabel icon={ICONS.exit} label="Exit" />
        </p>
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
        <p>
          <IconLabel icon={ICONS.decision} label="Decision" />
        </p>
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
        <BackButton onClick={onBack} />
        <h2>
          <IconLabel icon={ICONS.detail} label={formatPair(pair.pair)} />
        </h2>
        <StatusBadge value={bridges.safeStatus} />
      </div>

      <div className="detailGrid">
        <section className="panel pricePanel" aria-label="Price">
          <div className="panelHeading">
            <p>
              <IconLabel icon={ICONS.price} label="Price" />
            </p>
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

function SimpleStatusPage({ title, icon, backLabel, onBack, children }) {
  return (
    <section className="screen" aria-label={title}>
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>
          <IconLabel icon={icon} label={title} />
        </h2>
        <StatusBadge value={backLabel} />
      </div>
      <div className="simpleGrid">{children}</div>
    </section>
  );
}

function SystemPage({ onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.system} backLabel="READ_ONLY" title="System" onBack={onBack}>
      <Field compact label="Dashboard" source={source} value="READY" tone="good" />
      <Field compact label="Mode" source={source} value={dashboardFixture.mode} />
      <Field compact label="Data" source={source} value={dashboardFixture.source} />
      <Field compact label="Broker" source={source} value={dashboardFixture.bridges.brokerBridge} />
      <Field compact label="Live APIs" source={source} value="BLOCKED" />
    </SimpleStatusPage>
  );
}

function SafetyPage({ onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.safety} backLabel="BLOCKED" title="Safety" onBack={onBack}>
      <Field compact label="Live trading" source={source} value="BLOCKED" />
      <Field compact label="Source labels" source={source} value="REQUIRED" tone="warn" />
      <Field compact label="Secrets" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Kill switch" source={source} value="REQUIRED" tone="warn" />
      <Field compact label="Broker/API action" source={source} value="BLOCKED" />
    </SimpleStatusPage>
  );
}

function SettingsPage({ bridges, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.settings} backLabel="NO_SECRETS" title="Settings" onBack={onBack}>
      <Field compact label="Secret bridge" source={source} value={bridges.secretBridge} />
      <Field compact label="Broker bridge" source={source} value={bridges.brokerBridge} />
      <Field compact label="API keys" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Tokens" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Account IDs" source={source} value="HIDDEN" tone="good" />
      <Field compact label="Secret values" source={source} value="NOT_DISPLAYED" tone="good" />
    </SimpleStatusPage>
  );
}

function PositionPage({ riskPl, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.position} backLabel="READ_ONLY" title="Position" onBack={onBack}>
      <Field compact label="Position" source={source} value={riskPl.currentPosition} tone="neutral" />
      <Field compact label="Units" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
    </SimpleStatusPage>
  );
}

function RiskPage({ riskPl, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.risk} backLabel="FIXTURE_NOT_LIVE" title="Risk / P&L" onBack={onBack}>
      <Field compact label="Risk cap" source={source} value={riskPl.riskCap} tone="warn" />
      <Field compact label="Position size" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
      <Field compact label="Live trading allowed" source={source} value="false" />
    </SimpleStatusPage>
  );
}

function ExitPage({ exitReadiness, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage icon={ICONS.exit} backLabel={exitReadiness.autoExitStatus} title="Exit" onBack={onBack}>
      {exitReadiness.controls.map((control) => (
        <Field compact key={control.label} label={control.label} source={source} value={control.status} />
      ))}
      <Field compact label="Auto-exit" source={source} value={exitReadiness.autoExitStatus} />
      <section className="panel notePanel" aria-label="Exit block reason">
        <div className="panelHeading">
          <p>
            <IconLabel icon={ICONS.blocked} label="Block reason" />
          </p>
          <h3>{exitReadiness.autoExitStatus}</h3>
        </div>
        <p className="shortText">{exitReadiness.blockReason}</p>
        <DataLabel compact source={source} />
      </section>
    </SimpleStatusPage>
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

      {view === VIEWS.HOME ? <HomeScreen onNavigate={setView} /> : null}

      {view === VIEWS.FOREX ? (
        <ForexHub
          onBack={() => setView(VIEWS.HOME)}
          onNavigate={setView}
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

      {view === VIEWS.SYSTEM ? <SystemPage onBack={() => setView(VIEWS.HOME)} /> : null}

      {view === VIEWS.SAFETY ? <SafetyPage onBack={() => setView(VIEWS.HOME)} /> : null}

      {view === VIEWS.SETTINGS ? (
        <SettingsPage bridges={dashboardFixture.bridges} onBack={() => setView(VIEWS.HOME)} />
      ) : null}

      {view === VIEWS.POSITION ? (
        <PositionPage riskPl={dashboardFixture.riskPl} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.RISK ? (
        <RiskPage riskPl={dashboardFixture.riskPl} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.EXIT ? (
        <ExitPage exitReadiness={dashboardFixture.exitReadiness} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}
    </main>
  );
}
