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
  EXIT: "exit",
  HISTORY: "history",
  READINESS: "readiness"
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
  history: "🧾",
  readiness: "🚦",
  detail: "🔎"
};

const SYSTEM_DETAIL_ITEMS = [
  {
    id: "dashboard",
    emoji: "📊",
    label: "DASHBOARD",
    value: "READY",
    tone: "good"
  },
  {
    id: "mode",
    emoji: "⚙️",
    label: "MODE",
    value: dashboardFixture.mode
  },
  {
    id: "data",
    emoji: "🧾",
    label: "DATA",
    value: dashboardFixture.source
  },
  {
    id: "broker",
    emoji: "🏦",
    label: "BROKER",
    value: dashboardFixture.bridges.brokerBridge
  },
  {
    id: "liveApis",
    emoji: "🔌",
    label: "LIVE APIS",
    value: "BLOCKED"
  }
];

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
  [VIEWS.EXIT]: "Exit",
  [VIEWS.HISTORY]: "Trading History",
  [VIEWS.READINESS]: "Execution Readiness"
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
  [VIEWS.EXIT]: ICONS.exit,
  [VIEWS.HISTORY]: ICONS.history,
  [VIEWS.READINESS]: ICONS.readiness
};

const FOREX_CHILD_VIEWS = new Set([
  VIEWS.WATCHLIST,
  VIEWS.DETAIL,
  VIEWS.POSITION,
  VIEWS.RISK,
  VIEWS.EXIT,
  VIEWS.HISTORY,
  VIEWS.READINESS
]);

const OPERATION_CONTRACTS = {
  watchlist: {
    cause: "Request latest available watchlist and opportunity snapshot from the AIOS read-model source.",
    effect: "Display ranked pairs, score, confidence, trend, source, freshness, and live-trading permission."
  },
  position: {
    cause: "Request broker/account position reconciliation read-model.",
    effect: "Display open position, units, entry price if available, realized P/L, unrealized P/L, freshness, and source."
  },
  risk: {
    cause: "Request risk governor and P/L truth read-model.",
    effect: "Display daily loss cap, max position size, realized P/L, unrealized P/L, risk status, and blocked/allowed state."
  },
  exit: {
    cause: "Request exit readiness and readiness-plan evaluation for any current open trade.",
    effect: "Display stop-loss, take-profit, trailing stop, max-time policy, auto-exit readiness, and block reason."
  },
  history: {
    cause: "Request sanitized closed-trade and execution-evidence read-model.",
    effect: "Display closed trades, realized P/L, exit reason, protection controls used, slippage, evidence status, source, and freshness."
  },
  readiness: {
    cause: "Request the live-capable execution readiness bridge projection.",
    effect: "Display live data, broker, signal, risk, exit, and history-writeback gates with LIVE_READY, blockers, and next safe action."
  }
};

function normalizeDataSourceType(value) {
  const text = String(value ?? "").toUpperCase();

  if (text.includes("FIXTURE") || text.includes("STALE") || text.includes("UNVERIFIED")) {
    return "fixture";
  }

  if (text.includes("PAPER") || text.includes("DEMO")) {
    return "paper";
  }

  if (text.includes("BROKER") && text.includes("EXECUTION")) {
    return "broker-live-execution";
  }

  if (text.includes("LIVE") || text.includes("BROKER")) {
    return "broker-live-read-only";
  }

  return "fixture";
}

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

function viewLabel(view) {
  return VIEW_LABELS[view] ?? "Dashboard";
}

function viewIcon(view) {
  return VIEW_ICONS[view] ?? ICONS.operator;
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

function formatFreshness(source) {
  const timestamp = source?.timestamp ? formatTime(source.timestamp) : "UNKNOWN";
  const staleness = Number.isFinite(source?.stalenessSeconds)
    ? `${source.stalenessSeconds}s`
    : "UNKNOWN";

  return `${timestamp} / ${staleness}`;
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

function ReadinessRow({ label, value, tone }) {
  const displayValue = typeof value === "boolean" ? String(value) : value;

  return (
    <div className="field readinessField">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(displayValue)}`}>{displayValue}</strong>
    </div>
  );
}

function dataSourceForPair(pair) {
  const dataSource = dashboardFixture.dataSource ?? {};

  return {
    label:
      pair?.explanation?.dataSourceLabel ??
      dataSource.DISPLAY_LABEL ??
      dashboardFixture.source ??
      "UNVERIFIED",
    liveTradingAllowed:
      pair?.explanation?.liveTradingAllowedFromThisData ??
      dataSource.LIVE_TRADING_ALLOWED_FROM_THIS_DATA ??
      false,
    blockReason:
      pair?.explanation?.blockReason ??
      dataSource.BLOCK_REASON ??
      "Source permission is not approved for live trade decisions.",
    timestamp: pair?.lastUpdated ?? dataSource.DATA_TIMESTAMP_UTC ?? dashboardFixture.generatedAt,
    stalenessSeconds: dataSource.DATA_STALENESS_SECONDS
  };
}

function DataLabel({ source, compact = false }) {
  const liveAllowed = Boolean(source?.liveTradingAllowed);

  return (
    <div className={`dataLabel ${compact ? "compactLabel" : ""}`}>
      <StatusBadge value={source?.label ?? "UNVERIFIED"} />
      <span>{`Freshness: ${formatFreshness(source)}`}</span>
      <span>{`LIVE_TRADING_ALLOWED_FROM_THIS_DATA: ${String(liveAllowed)}`}</span>
      {!compact && !liveAllowed ? (
        <small>{source?.blockReason ?? "Data is blocked for live decisions."}</small>
      ) : null}
    </div>
  );
}

function buildLiveReadinessModel(pair) {
  const dataSource = dashboardFixture.dataSource ?? {};
  const bridges = dashboardFixture.bridges ?? {};
  const riskPl = dashboardFixture.riskPl ?? {};
  const exitReadiness = dashboardFixture.exitReadiness ?? {};
  const explanation = pair?.explanation ?? {};
  const sourceType = normalizeDataSourceType(
    explanation.dataSourceType ?? dataSource.DATA_SOURCE_TYPE ?? dashboardFixture.source
  );
  const liveSourceAllowed = Boolean(dataSource.LIVE_TRADING_ALLOWED_FROM_THIS_DATA);
  const selectedPair = formatPair(pair?.pair ?? dashboardFixture.selectedPair);
  const blockReasons = [
    "Real market data source is not approved for live trade decisions.",
    "Broker/account state has not been reconciled.",
    "Signal logic and expected edge evidence are not connected.",
    "Risk governor has not approved a live trade boundary.",
    "Pre-entry exit plan and auto-exit readiness are blocked.",
    "Trading history writeback is not available for real closed-trade evidence.",
    "Human Owner has not explicitly armed live execution."
  ];

  return {
    liveReady: false,
    actionMode: "READ_ONLY",
    liveButton: "NOT_PRESENT",
    nextSafeAction:
      "Connect permitted read-only data and broker reconciliation in a later packet, then run paper signal execution before any live arming gate.",
    blockReasons,
    sections: [
      {
        title: "Live data readiness",
        status: liveSourceAllowed ? "VALID" : "BLOCKED",
        rows: [
          { label: "Data source name", value: dataSource.DATA_SOURCE_NAME ?? "UNVERIFIED" },
          { label: "Source type", value: sourceType },
          {
            label: "Freshness timestamp",
            value: dataSource.DATA_TIMESTAMP_UTC ?? dashboardFixture.generatedAt ?? "UNKNOWN"
          },
          { label: "Stale/valid status", value: dataSource.MARKET_DATA_STATUS ?? "BLOCKED" },
          { label: "Live trading allowed from this source", value: liveSourceAllowed },
          {
            label: "Block reason",
            value:
              dataSource.BLOCK_REASON ??
              "Data source is not approved for live trade decisions."
          },
          { label: "No secrets printed", value: true, tone: "good" },
          { label: "No account IDs printed", value: true, tone: "good" }
        ]
      },
      {
        title: "Broker state readiness",
        status: "BLOCKED",
        rows: [
          { label: "Account reachable", value: false },
          { label: "Broker mode", value: "UNKNOWN" },
          { label: "Open positions reconciled", value: false },
          { label: "Pending orders reconciled", value: false },
          { label: "Daily P/L available", value: false },
          { label: "Margin/risk availability", value: false },
          {
            label: "Block reason",
            value: "Broker bridge is blocked and no sanitized account reconciliation is available."
          }
        ]
      },
      {
        title: "Signal readiness",
        status: "BLOCKED",
        rows: [
          { label: "Selected pair", value: selectedPair, tone: "neutral" },
          { label: "Strategy name", value: "UNCONNECTED" },
          { label: "Signal side", value: "NONE" },
          {
            label: "Confidence",
            value: pair?.confidence ? `${pair.confidence}% fixture confidence` : "UNVERIFIED"
          },
          { label: "Expected edge evidence path", value: "UNAVAILABLE" },
          { label: "Backtest/paper evidence required", value: true, tone: "warn" },
          {
            label: "Spread/slippage status",
            value: explanation.spreadSlippageStatus ?? "UNVERIFIED"
          },
          {
            label: "Block reason",
            value: "No approved live signal logic or expected-edge evidence is connected."
          }
        ]
      },
      {
        title: "Risk readiness",
        status: "BLOCKED",
        rows: [
          { label: "Max units", value: riskPl.positionSize ?? "NOT_APPROVED" },
          { label: "Max trade risk", value: riskPl.riskCap ?? "NOT_APPROVED" },
          { label: "Daily loss cap", value: riskPl.riskCap ?? "NOT_APPROVED" },
          { label: "One-position rule", value: "REQUIRED_NOT_ARMED" },
          { label: "No revenge-loop rule", value: "REQUIRED_NOT_ARMED" },
          { label: "No duplicate-entry rule", value: "REQUIRED_NOT_ARMED" },
          { label: "Kill switch required", value: bridges.killSwitch ?? "REQUIRED" },
          { label: "Risk governor approval", value: false },
          {
            label: "Block reason",
            value: "Risk governor has not approved a live trade boundary."
          }
        ]
      },
      {
        title: "Exit readiness",
        status: exitReadiness.autoExitStatus ?? "BLOCKED",
        rows: [
          { label: "Stop-loss before or with entry", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Take-profit policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Trailing-stop policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Max-time policy", value: "REQUIRED_NOT_LIVE_READY" },
          { label: "Auto-exit readiness", value: exitReadiness.autoExitStatus ?? "BLOCKED" },
          { label: "Manual close fallback", value: "REQUIRED" },
          {
            label: "Block reason",
            value:
              exitReadiness.blockReason ??
              "Exit readiness is not approved for live execution."
          }
        ]
      },
      {
        title: "Trading history writeback readiness",
        status: "BLOCKED",
        rows: [
          { label: "Opened trade evidence row", value: "REQUIRED" },
          { label: "Close realized P/L record", value: "REQUIRED" },
          {
            label: "Required row fields",
            value:
              "pair, side, units, entry time, exit time, duration, realized P/L, exit reason, slippage, source, freshness"
          },
          { label: "History writeback available", value: false },
          {
            label: "Block reason",
            value: "Live execution is blocked until sanitized trade-history writeback is available."
          }
        ]
      }
    ]
  };
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

function SystemDetailField({ label, value, tone }) {
  return (
    <div className="field systemDetailField">
      <span>{label}</span>
      <strong className={`tone-${tone ?? statusTone(value)}`}>{value}</strong>
    </div>
  );
}

function SystemDetailPanel({ item, source }) {
  const liveAllowed = Boolean(source?.liveTradingAllowed);
  const rows = [
    {
      label: item.label,
      value: item.value,
      tone: item.tone
    },
    {
      label: "SOURCE",
      value: source?.label ?? "UNVERIFIED"
    },
    {
      label: "FRESHNESS",
      value: formatFreshness(source),
      tone: "neutral"
    },
    {
      label: "LIVE_TRADING_ALLOWED_FROM_THIS_DATA",
      value: String(liveAllowed)
    }
  ];

  return (
    <section className="systemDetailPanel" aria-label={`${item.label} detail`}>
      <div className="fieldGrid systemDetailGrid">
        {rows.map((row) => (
          <SystemDetailField
            key={row.label}
            label={row.label}
            tone={row.tone}
            value={row.value}
          />
        ))}
      </div>
    </section>
  );
}

function CauseEffectPanel({ contract, source = dataSourceForPair() }) {
  return (
    <section className="panel causeEffectPanel" aria-label="Button cause and effect contract">
      <div className="causeEffectGrid">
        <div>
          <span>Cause</span>
          <p>{contract.cause}</p>
        </div>
        <div>
          <span>Effect</span>
          <p>{contract.effect}</p>
        </div>
      </div>
      <DataLabel source={source} />
    </section>
  );
}

function ShellHeader({ view }) {
  const label = viewLabel(view);

  return (
    <header className="dashboardHeader">
      <div>
        <h1 aria-label={label} className="pageIdentityGlyph" title={label}>
          <span aria-hidden="true">{viewIcon(view)}</span>
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
    crumbs.push({ label: formatPair(selected.pair), showLabel: true });
  } else if (view !== VIEWS.HOME && view !== VIEWS.FOREX && view !== VIEWS.WATCHLIST) {
    crumbs.push({ label: viewLabel(view), icon: viewIcon(view) });
  }

  const visibleCrumbs = view === VIEWS.DETAIL ? crumbs : crumbs.slice(0, -1);

  if (visibleCrumbs.length === 0) {
    return null;
  }

  return (
    <nav className="breadcrumb" aria-label="Dashboard breadcrumb">
      {visibleCrumbs.map((crumb, index) => {
        const isLast = index === visibleCrumbs.length - 1 && crumb.showLabel;
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
            {crumb.icon ? <span aria-hidden="true">{crumb.icon}</span> : null}
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
        <DoorCard
          icon={ICONS.history}
          title="Trading History"
          onClick={() => onNavigate(VIEWS.HISTORY)}
        />
        <DoorCard
          icon={ICONS.readiness}
          title="Execution Readiness"
          onClick={() => onNavigate(VIEWS.READINESS)}
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
      </div>

      <CauseEffectPanel contract={OPERATION_CONTRACTS.watchlist} source={dataSourceForPair()} />

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
        <BackButton onClick={onBack} />
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

function SimpleStatusPage({ title, backLabel, onBack, children }) {
  return (
    <section className="screen" aria-label={title}>
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <StatusBadge value={backLabel} />
      </div>
      <div className="simpleGrid">{children}</div>
    </section>
  );
}

function SystemPage({ onBack }) {
  const source = dataSourceForPair();
  const [selectedDetailId, setSelectedDetailId] = useState(SYSTEM_DETAIL_ITEMS[0].id);
  const selectedDetail =
    SYSTEM_DETAIL_ITEMS.find((item) => item.id === selectedDetailId) ?? SYSTEM_DETAIL_ITEMS[0];

  return (
    <section className="screen" aria-label="System">
      <div className="screenTop">
        <BackButton onClick={onBack} />
        <h2>System</h2>
        <StatusBadge value="READ_ONLY" />
      </div>

      <div className="systemEmojiGrid" aria-label="System status controls">
        {SYSTEM_DETAIL_ITEMS.map((item) => {
          const isActive = item.id === selectedDetail.id;

          return (
            <button
              aria-label={item.label}
              aria-pressed={isActive}
              className={`systemEmojiButton ${isActive ? "activeSystemEmojiButton" : ""}`}
              key={item.id}
              title={item.label}
              type="button"
              onClick={() => setSelectedDetailId(item.id)}
            >
              <span aria-hidden="true">{item.emoji}</span>
            </button>
          );
        })}
      </div>

      <SystemDetailPanel item={selectedDetail} source={source} />
    </section>
  );
}

function SafetyPage({ onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="BLOCKED" title="Safety" onBack={onBack}>
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
    <SimpleStatusPage backLabel="NO_SECRETS" title="Settings" onBack={onBack}>
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
    <SimpleStatusPage backLabel="READ_ONLY" title="Position" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.position} source={source} />
      <Field compact label="Position" source={source} value={riskPl.currentPosition} tone="neutral" />
      <Field compact label="Units" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Entry price" source={source} value="UNAVAILABLE" tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
    </SimpleStatusPage>
  );
}

function RiskPage({ riskPl, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel="FIXTURE_NOT_LIVE" title="Risk / P&L" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.risk} source={source} />
      <Field compact label="Daily loss cap" source={source} value={riskPl.riskCap} tone="warn" />
      <Field compact label="Max position size" source={source} value={riskPl.positionSize} tone="warn" />
      <Field compact label="Realized P/L" source={source} value={riskPl.realizedPl} tone="neutral" />
      <Field compact label="Unrealized P/L" source={source} value={riskPl.unrealizedPl} tone="neutral" />
      <Field compact label="Risk status" source={source} value="BLOCKED" tone="danger" />
      <Field compact label="Live trading allowed" source={source} value="false" />
    </SimpleStatusPage>
  );
}

function ExitPage({ exitReadiness, onBack }) {
  const source = dataSourceForPair();

  return (
    <SimpleStatusPage backLabel={exitReadiness.autoExitStatus} title="Exit" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.exit} source={source} />
      <section className="panel notePanel" aria-label="Exit page meaning">
        <div className="panelHeading">
          <p>Meaning</p>
          <h3>Readiness only</h3>
        </div>
        <p className="shortText">
          Exit evaluates whether a trade is protected and exit-ready. This page does not close trades.
        </p>
      </section>
      {exitReadiness.controls.map((control) => (
        <Field compact key={control.label} label={control.label} source={source} value={control.status} />
      ))}
      <Field compact label="Auto-exit" source={source} value={exitReadiness.autoExitStatus} />
      <section className="panel notePanel" aria-label="Exit block reason">
        <div className="panelHeading">
          <p>Block reason</p>
          <h3>{exitReadiness.autoExitStatus}</h3>
        </div>
        <p className="shortText">{exitReadiness.blockReason}</p>
        <DataLabel compact source={source} />
      </section>
    </SimpleStatusPage>
  );
}

function tradeValue(trade, keys, fallback = "UNAVAILABLE") {
  for (const key of keys) {
    if (trade?.[key] !== undefined && trade?.[key] !== null && trade?.[key] !== "") {
      return trade[key];
    }
  }

  return fallback;
}

function TradingHistoryPage({ onBack }) {
  const source = dataSourceForPair();
  const history = Array.isArray(dashboardFixture.tradingHistory)
    ? dashboardFixture.tradingHistory
    : [];
  const rows =
    history.length > 0
      ? history
      : [
          {
            pair: "UNAVAILABLE",
            evidenceStatus: "NO_REAL_HISTORY_AVAILABLE",
            sourceLabel: "FIXTURE_NOT_LIVE"
          }
        ];

  return (
    <SimpleStatusPage
      backLabel={history.length > 0 ? "READ_ONLY" : "NO_REAL_HISTORY_AVAILABLE"}
      title="Trading History"
      onBack={onBack}
    >
      <CauseEffectPanel contract={OPERATION_CONTRACTS.history} source={source} />
      {history.length === 0 ? (
        <section className="panel notePanel" aria-label="Trading history unavailable">
          <div className="panelHeading">
            <p>Trading History</p>
            <h3>NO_REAL_HISTORY_AVAILABLE</h3>
          </div>
          <p className="shortText">
            No sanitized real closed-trade history is available to this dashboard. Fixture/demo state is
            read-only and cannot prove live execution.
          </p>
          <DataLabel source={source} />
        </section>
      ) : null}
      <div className="historyList" role="list" aria-label="Closed trade history">
        {rows.map((trade, index) => (
          <section className="panel historyCard" key={`${trade.pair ?? "trade"}-${index}`} role="listitem">
            <div className="panelHeading">
              <p>Closed trade</p>
              <h3>{formatPair(tradeValue(trade, ["pair"], "UNKNOWN"))}</h3>
            </div>
            <div className="fieldGrid">
              <Field compact label="Pair" source={source} value={formatPair(tradeValue(trade, ["pair"]))} />
              <Field compact label="Side" source={source} value={tradeValue(trade, ["side"])} />
              <Field compact label="Units" source={source} value={tradeValue(trade, ["units"])} />
              <Field compact label="Entry time" source={source} value={tradeValue(trade, ["entryTime"])} />
              <Field compact label="Exit time" source={source} value={tradeValue(trade, ["exitTime"])} />
              <Field compact label="Duration" source={source} value={tradeValue(trade, ["duration"])} />
              <Field compact label="Realized P/L" source={source} value={tradeValue(trade, ["realizedPl", "realizedPL"])} />
              <Field compact label="Exit reason" source={source} value={tradeValue(trade, ["exitReason"])} />
              <Field compact label="Stop-loss used" source={source} value={tradeValue(trade, ["stopLossUsed"])} />
              <Field compact label="Take-profit used" source={source} value={tradeValue(trade, ["takeProfitUsed"])} />
              <Field compact label="Trailing used" source={source} value={tradeValue(trade, ["trailingStopUsed"])} />
              <Field compact label="Max-time used" source={source} value={tradeValue(trade, ["maxTimeUsed"])} />
              <Field compact label="Slippage" source={source} value={tradeValue(trade, ["slippage"])} />
              <Field compact label="Evidence status" source={source} value={tradeValue(trade, ["evidenceStatus"])} />
            </div>
          </section>
        ))}
      </div>
    </SimpleStatusPage>
  );
}

function ReadinessSection({ section, source }) {
  return (
    <section className="panel readinessPanel" aria-label={section.title}>
      <div className="panelHeading">
        <p>{section.title}</p>
        <h3>{section.status}</h3>
      </div>
      <div className="fieldGrid readinessGrid">
        {section.rows.map((row) => (
          <ReadinessRow
            key={`${section.title}-${row.label}`}
            label={row.label}
            tone={row.tone}
            value={row.value}
          />
        ))}
      </div>
      <DataLabel compact source={source} />
    </section>
  );
}

function ExecutionReadinessPage({ pair, onBack }) {
  const source = dataSourceForPair(pair);
  const readiness = buildLiveReadinessModel(pair);

  return (
    <SimpleStatusPage backLabel="LIVE_READY: false" title="Execution Readiness" onBack={onBack}>
      <CauseEffectPanel contract={OPERATION_CONTRACTS.readiness} source={source} />
      <section className="panel readinessSummaryPanel" aria-label="Overall execution readiness">
        <div className="panelHeading">
          <p>Overall status</p>
          <h3>{`LIVE_READY: ${String(readiness.liveReady)}`}</h3>
        </div>
        <div className="fieldGrid readinessGrid">
          <ReadinessRow label="Action mode" value={readiness.actionMode} tone="good" />
          <ReadinessRow label="Live BUY/SELL button" value={readiness.liveButton} tone="good" />
          <ReadinessRow label="Next safe action" value={readiness.nextSafeAction} tone="warn" />
        </div>
        <div className="blockedReasonList" aria-label="Blocked reasons">
          {readiness.blockReasons.map((reason) => (
            <div className="blockedReason" key={reason}>
              <span>Blocked</span>
              <p>{reason}</p>
            </div>
          ))}
        </div>
        <DataLabel source={source} />
      </section>
      <div className="readinessSectionList">
        {readiness.sections.map((section) => (
          <ReadinessSection key={section.title} section={section} source={source} />
        ))}
      </div>
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

      {view === VIEWS.HISTORY ? (
        <TradingHistoryPage onBack={() => setView(VIEWS.FOREX)} />
      ) : null}

      {view === VIEWS.READINESS ? (
        <ExecutionReadinessPage pair={selected} onBack={() => setView(VIEWS.FOREX)} />
      ) : null}
    </main>
  );
}
