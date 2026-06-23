import liveOperatorPanel from '../mock-data/aios-live-operator-panel-v1.example.json';
import operatorStatusFixture from '../mock-data/aios-operator-status-v1.example.json';
import mockRuntimeVisibility from '../mock-data/aios-runtime-visibility-v1.example.json';
import AiosSymbol from './AiosSymbol.jsx';
import AIOSLiveOperatorPanel from './AIOSLiveOperatorPanel.jsx';
import PreservedLegacyModules from './PreservedLegacyModules.jsx';
import './App.css';

const LIVE_TRADING_ALLOWED = false;
const MUTATION_ALLOWED = false;
const EXECUTION_ALLOWED = false;

const runtimeContract = mockRuntimeVisibility.frontend_contract ?? {};
const runtimeState = mockRuntimeVisibility.runtime ?? {};
const runtimeQueue = mockRuntimeVisibility.queue ?? {};
const accessSummary = operatorStatusFixture.registry_safety ?? {};
const telemetrySummary = operatorStatusFixture.telemetry_status ?? {};
const workerSummary = operatorStatusFixture.worker_status ?? {};
const nextSafeActionFixture = operatorStatusFixture.next_safe_action ?? {};
const blockedActions = Array.isArray(runtimeContract.blocked_actions) ? runtimeContract.blocked_actions : [];
const warnings = Array.isArray(mockRuntimeVisibility.warnings) ? mockRuntimeVisibility.warnings : [];

const PAIR_CODES = [
  'EUR/USD',
  'GBP/USD',
  'USD/JPY',
  'AUD/USD',
  'USD/CAD',
  'USD/CHF',
  'NZD/USD',
  'EUR/JPY',
  'GBP/JPY',
  'XAU/USD',
  'BTC/USD'
];

const PAIR_SYMBOLS = {
  'EUR/USD': 'pair-eur-usd',
  'GBP/JPY': 'pair-gbp-jpy',
  'XAU/USD': 'pair-xau-usd',
  'BTC/USD': 'pair-btc-usd'
};

const FOREX_CAPABILITY_STATES = [
  {
    label: 'Paper / research',
    value: 'DISPLAY / READINESS',
    status: 'REVIEW',
    detail: 'Allowed only when existing read-only evidence supports paper or readiness review.'
  },
  {
    label: 'Demo / broker proof',
    value: 'LOCKED / NEEDS EVIDENCE',
    status: 'LOCKED',
    detail: 'No broker proof is armed by this dashboard.'
  },
  {
    label: 'Live / real money',
    value: 'LOCKED',
    status: 'LOCKED',
    detail: 'Live forex trading is locked.'
  },
  {
    label: 'Broker execution',
    value: 'LOCKED',
    status: 'LOCKED',
    detail: 'Broker execution is locked unless governed exception evidence proves otherwise.'
  }
];

const FOREX_TRUTH_STATEMENTS = [
  'Live forex trading is locked.',
  'Broker execution is locked.',
  'Dashboard does not place orders.',
  'Credentials are not held by the dashboard.',
  'Next safe action comes from evidence.'
];

const TRADE_METADATA_DEFAULTS = {
  tradeNumber: 'AIOS-TRADE-PENDING',
  sessionId: 'SESSION-EVIDENCE-MISSING',
  cycleId: 'CYCLE-EVIDENCE-MISSING',
  candidateId: 'CANDIDATE-EVIDENCE-MISSING',
  setupId: 'SETUP-EVIDENCE-MISSING',
  strategyId: 'STRATEGY-EVIDENCE-MISSING',
  signalId: 'SIGNAL-EVIDENCE-MISSING',
  sequenceNumber: 'SEQ-PENDING',
  tradeTicketStatus: 'LOCKED',
  evidenceBundleId: 'EVIDENCE-BUNDLE-PENDING',
  replayId: 'REPLAY-NOT-STARTED',
  reconciliationStatus: 'NOT_STARTED',
  executionAuthority: 'DASHBOARD_DISPLAY_ONLY'
};

function upper(value, fallback = 'UNKNOWN') {
  if (value === null || value === undefined || value === '') {
    return fallback;
  }

  return String(value).toUpperCase();
}

function asBooleanText(value) {
  return value === true ? 'TRUE' : 'FALSE';
}

function formatMoney(value) {
  if (typeof value !== 'number') {
    return 'UNKNOWN';
  }

  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2
  }).format(value);
}

function formatInstrument(value) {
  return upper(value).replace('_', '/');
}

function safeValue(value, fallback = 'EVIDENCE MISSING') {
  if (value === null || value === undefined || value === '') {
    return fallback;
  }

  return String(value);
}

function statusTone(status) {
  const value = upper(status);

  if (value === 'CLEAR' || value === 'READY' || value === 'PASS' || value === 'DISPLAY_ONLY') {
    return 'good';
  }

  if (value === 'LOCKED' || value.includes('LOCKED') || value.includes('PROTECTED')) {
    return 'locked';
  }

  if (value === 'BLOCKED' || value.includes('BLOCK') || value.includes('FALSE') || value.includes('FAIL')) {
    return 'danger';
  }

  if (value === 'REVIEW' || value.includes('REVIEW') || value.includes('STALE') || value.includes('UNKNOWN')) {
    return 'warn';
  }

  return 'neutral';
}

function statusIcon(status) {
  const tone = statusTone(status);

  if (tone === 'good') {
    return 'status-clear';
  }

  if (tone === 'danger') {
    return 'status-blocked';
  }

  if (tone === 'locked') {
    return 'status-locked';
  }

  return 'status-review';
}

function StatusChip({ label, status = label, icon = false }) {
  return (
    <span className={`statusPill status-${statusTone(status)}`}>
      {icon ? <AiosSymbol name={statusIcon(status)} label={`${label} status`} size="xs" framed={false} /> : null}
      {label}
    </span>
  );
}

function SummaryTile({ label, value, status, detail, symbol }) {
  return (
    <article className="cockpitSummaryTile">
      <div className="tileHead">
        {symbol ? <AiosSymbol name={symbol} label={`${label} signal`} size="sm" /> : null}
        <div>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      </div>
      <StatusChip label={status} status={status} />
      {detail ? <p>{detail}</p> : null}
    </article>
  );
}

function DataRow({ label, value, status = 'REVIEW' }) {
  return (
    <div className="cockpitDataRow">
      <span>{label}</span>
      <strong>{value}</strong>
      <StatusChip label={status} status={status} />
    </div>
  );
}

function Section({ id, title, eyebrow, status, symbol, children }) {
  return (
    <section id={id} className="cockpitSection" aria-labelledby={`${id}-title`}>
      <div className="cockpitSectionHead">
        <div className="sectionTitleRow">
          {symbol ? <AiosSymbol name={symbol} label={`${title} icon`} size="sm" /> : null}
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h2 id={`${id}-title`}>{title}</h2>
          </div>
        </div>
        <StatusChip label={status} status={status} icon />
      </div>
      {children}
    </section>
  );
}

function LedgerMetric({ label, value, status = 'REVIEW', symbol }) {
  return (
    <div className="tradeLedgerMetric">
      <div className="tradeLedgerMetricTopline">
        {symbol ? <AiosSymbol name={symbol} label={`${label} icon`} size="xs" framed={false} /> : null}
        <span>{label}</span>
      </div>
      <strong>{value}</strong>
      <StatusChip label={status} status={status} />
    </div>
  );
}

function metadataValue(source, key, fallback = 'EVIDENCE MISSING') {
  if (!source || source[key] === null || source[key] === undefined || source[key] === '') {
    return fallback;
  }

  return String(source[key]);
}

function CommandCenter() {
  const runtimeIsStale = runtimeState.freshness === 'stale' || runtimeContract.stale_or_legacy === true;
  const runtimeStatus = runtimeIsStale ? 'REVIEW' : 'CLEAR';
  const accessStatus = accessSummary.status === 'PASS' ? 'CLEAR' : 'REVIEW';
  const brokerStatus = liveOperatorPanel.broker_call_performed ? 'REVIEW' : 'LOCKED';

  return (
    <Section id="command-center" eyebrow="Command Center" title="AIOS operating truth" status={runtimeStatus} symbol="aios-core">
      <div className="cockpitSummaryGrid">
        <SummaryTile
          label="AIOS online"
          value={runtimeIsStale ? 'STALE FIXTURE' : upper(runtimeState.status)}
          status={runtimeStatus}
          symbol="aios-core"
          detail="Runtime truth is fixture-backed until fresher read-only evidence is supplied."
        />
        <SummaryTile
          label="Site / access"
          value={accessSummary.status === 'PASS' ? 'PROTECTED DISPLAY' : 'NOT PROVEN'}
          status={accessStatus}
          symbol="site-access"
          detail="Registry fixture passes. Full SSO UX is not proved by this dashboard."
        />
        <SummaryTile
          label="Trading mode"
          value="PAPER / DISPLAY"
          status="LOCKED"
          symbol="trader-cockpit"
          detail="No live order authority exists in the frontend."
        />
        <SummaryTile
          label="Broker execution"
          value="NO BROKER CALL"
          status={brokerStatus}
          symbol="broker-bridge-locked"
          detail="Broker connector remains evidence-only and protected."
        />
      </div>
      <div className="nextActionBand">
        <span>Next safe action</span>
        <strong>{runtimeContract.next_safe_action ?? mockRuntimeVisibility.nextSafeAction}</strong>
      </div>
    </Section>
  );
}

function TradeMetadataMatrix() {
  const metadata = liveOperatorPanel.trade_metadata ?? {};
  const identity = metadata.trade_identity ?? {};
  const market = metadata.market_snapshot ?? {};
  const candidate = metadata.candidate_strategy ?? {};
  const risk = metadata.risk_sizing ?? {};
  const orderPreview = metadata.order_preview ?? {};
  const lifecycle = metadata.lifecycle ?? {};
  const balancePnl = metadata.balance_pnl ?? {};
  const evidenceReplay = metadata.evidence_replay ?? {};
  const units = liveOperatorPanel.units ?? liveOperatorPanel.micro_size ?? liveOperatorPanel.order_units;
  const evidencePath = metadataValue(evidenceReplay, 'evidence_path', runtimeContract.source_path ?? 'EVIDENCE MISSING');
  const blockerCount = Array.isArray(liveOperatorPanel.blockers)
    ? liveOperatorPanel.blockers.length
    : blockedActions.length;
  const balanceBefore = balancePnl.balance_before ?? liveOperatorPanel.balance;
  const balanceAfter = balancePnl.balance_after ?? liveOperatorPanel.balance;
  const runtimeFreshness = runtimeContract.freshness?.is_stale
    ? 'STALE FIXTURE'
    : safeValue(runtimeContract.freshness?.generated_at, 'UNKNOWN');
  const tradeNumber = metadataValue(identity, 'aios_trade_number', TRADE_METADATA_DEFAULTS.tradeNumber);
  const sessionId = metadataValue(identity, 'session_id', TRADE_METADATA_DEFAULTS.sessionId);
  const evidenceBundleId = metadataValue(identity, 'evidence_bundle_id', TRADE_METADATA_DEFAULTS.evidenceBundleId);
  const replayId = metadataValue(identity, 'replay_id', TRADE_METADATA_DEFAULTS.replayId);
  const executionAuthority = metadataValue(
    orderPreview,
    'execution_authority_state',
    runtimeContract.authority_state ?? TRADE_METADATA_DEFAULTS.executionAuthority
  );

  const priorityMetrics = [
    { label: 'AIOS Trade #', value: tradeNumber, status: 'REVIEW', symbol: 'trade-sequence' },
    { label: 'Session', value: sessionId, status: 'REVIEW', symbol: 'session-replay' },
    { label: 'Ticket', value: metadataValue(identity, 'trade_ticket_status', TRADE_METADATA_DEFAULTS.tradeTicketStatus), status: 'LOCKED', symbol: 'trade-ticket' },
    { label: 'Risk governor', value: metadataValue(risk, 'risk_governor_state', 'LIVE LOCKED'), status: 'LOCKED', symbol: 'risk-metadata' },
    { label: 'Evidence bundle', value: evidenceBundleId, status: 'REVIEW', symbol: 'evidence-ledger' },
    { label: 'Replay', value: replayId, status: 'REVIEW', symbol: 'session-replay' }
  ];

  const metadataGroups = [
    {
      title: 'Trade Identity',
      symbol: 'trade-ledger',
      status: 'REVIEW',
      rows: [
        { label: 'AIOS Trade #', value: tradeNumber, status: 'REVIEW' },
        { label: 'Session ID', value: sessionId, status: 'REVIEW' },
        { label: 'Cycle ID', value: metadataValue(identity, 'cycle_id', TRADE_METADATA_DEFAULTS.cycleId), status: 'REVIEW' },
        { label: 'Candidate ID', value: metadataValue(identity, 'candidate_id', TRADE_METADATA_DEFAULTS.candidateId), status: 'REVIEW' },
        { label: 'Setup ID', value: metadataValue(identity, 'setup_id', TRADE_METADATA_DEFAULTS.setupId), status: 'REVIEW' },
        { label: 'Strategy ID', value: metadataValue(identity, 'strategy_id', TRADE_METADATA_DEFAULTS.strategyId), status: 'REVIEW' },
        { label: 'Signal ID', value: metadataValue(identity, 'signal_id', TRADE_METADATA_DEFAULTS.signalId), status: 'REVIEW' },
        { label: 'Sequence number', value: metadataValue(identity, 'sequence_number', TRADE_METADATA_DEFAULTS.sequenceNumber), status: 'REVIEW' },
        { label: 'Trade ticket status', value: metadataValue(identity, 'trade_ticket_status', TRADE_METADATA_DEFAULTS.tradeTicketStatus), status: 'LOCKED' },
        { label: 'Evidence bundle ID', value: evidenceBundleId, status: 'REVIEW' },
        { label: 'Replay ID', value: replayId, status: 'REVIEW' }
      ]
    },
    {
      title: 'Market Snapshot',
      symbol: 'market-snapshot',
      status: 'REVIEW',
      rows: [
        { label: 'Instrument / pair', value: metadataValue(market, 'instrument_pair', formatInstrument(liveOperatorPanel.instrument)), status: 'REVIEW' },
        { label: 'Timeframe', value: metadataValue(market, 'timeframe', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Market session', value: metadataValue(market, 'market_session', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Snapshot timestamp', value: metadataValue(market, 'market_snapshot_timestamp', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Normalized market state', value: metadataValue(market, 'normalized_market_state', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Spread state', value: metadataValue(market, 'spread_state', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Volatility state', value: metadataValue(market, 'volatility_state', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Liquidity state', value: metadataValue(market, 'liquidity_state', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'News-risk state', value: metadataValue(market, 'news_risk_state', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Source freshness', value: metadataValue(market, 'source_freshness', liveOperatorPanel.evidence_freshness ?? runtimeFreshness), status: 'REVIEW' }
      ]
    },
    {
      title: 'Candidate / Strategy',
      symbol: 'bot-algo',
      status: 'REVIEW',
      rows: [
        { label: 'Selected candidate ID', value: metadataValue(candidate, 'selected_candidate_id', TRADE_METADATA_DEFAULTS.candidateId), status: 'REVIEW' },
        { label: 'Rejected candidate count', value: metadataValue(candidate, 'rejected_candidate_count', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Strategy name', value: metadataValue(candidate, 'strategy_name', 'SUPERTREND PAPER_ONLY'), status: 'REVIEW' },
        { label: 'Direction', value: metadataValue(candidate, 'direction', upper(liveOperatorPanel.side)), status: 'REVIEW' },
        { label: 'Entry basis', value: metadataValue(candidate, 'entry_basis', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Stop basis', value: metadataValue(candidate, 'stop_basis', liveOperatorPanel.stop_loss ?? 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Target basis', value: metadataValue(candidate, 'target_basis', liveOperatorPanel.take_profit ?? 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Expectancy status', value: metadataValue(candidate, 'expectancy_status', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Sample size', value: metadataValue(candidate, 'sample_size', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Profit factor', value: metadataValue(candidate, 'profit_factor', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Max drawdown', value: metadataValue(candidate, 'max_drawdown', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'In-sample / out-of-sample', value: metadataValue(candidate, 'sample_status', 'EVIDENCE MISSING'), status: 'REVIEW' }
      ]
    },
    {
      title: 'Risk / Sizing',
      symbol: 'risk-metadata',
      status: 'LOCKED',
      rows: [
        { label: 'Mode', value: metadataValue(risk, 'mode', 'PAPER / DEMO PROOF / LIVE LOCKED'), status: 'LOCKED' },
        { label: 'Units or micro-size', value: metadataValue(risk, 'units_or_micro_size', safeValue(units)), status: 'REVIEW' },
        { label: 'Position size', value: metadataValue(risk, 'position_size', safeValue(units)), status: 'REVIEW' },
        { label: 'Risk number', value: metadataValue(risk, 'risk_number', formatMoney(liveOperatorPanel.open_risk)), status: 'REVIEW' },
        { label: 'Planned R', value: metadataValue(risk, 'planned_r', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Realized R', value: metadataValue(risk, 'realized_r', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Max-loss gate', value: metadataValue(risk, 'max_loss_gate', upper(liveOperatorPanel.max_loss_gate)), status: 'CLEAR' },
        { label: 'Daily-stop gate', value: metadataValue(risk, 'daily_stop_gate', upper(liveOperatorPanel.daily_stop_gate)), status: 'CLEAR' },
        { label: 'Kill-switch state', value: metadataValue(risk, 'kill_switch_state', upper(liveOperatorPanel.kill_switch)), status: 'LOCKED' },
        { label: 'Risk governor state', value: metadataValue(risk, 'risk_governor_state', 'LIVE LOCKED'), status: 'LOCKED' }
      ]
    },
    {
      title: 'Order Preview',
      symbol: 'trade-ticket',
      status: 'LOCKED',
      rows: [
        { label: 'Order preview ID', value: metadataValue(orderPreview, 'order_preview_id', 'ORDER-PREVIEW-EVIDENCE-MISSING'), status: 'REVIEW' },
        { label: 'Order type', value: metadataValue(orderPreview, 'order_type', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Planned side', value: metadataValue(orderPreview, 'planned_side', upper(liveOperatorPanel.side)), status: 'REVIEW' },
        { label: 'Planned entry', value: metadataValue(orderPreview, 'planned_entry', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Planned stop loss', value: metadataValue(orderPreview, 'planned_stop_loss', liveOperatorPanel.stop_loss ?? 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Planned take profit', value: metadataValue(orderPreview, 'planned_take_profit', liveOperatorPanel.take_profit ?? 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Planned expiry', value: metadataValue(orderPreview, 'planned_expiry', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Spread/slippage treatment', value: metadataValue(orderPreview, 'spread_slippage_treatment', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Execution authority', value: executionAuthority, status: 'LOCKED' }
      ]
    },
    {
      title: 'Lifecycle',
      symbol: 'lifecycle-flow',
      status: 'LOCKED',
      rows: [
        { label: 'Preview state', value: metadataValue(lifecycle, 'preview_state', 'DISPLAY ONLY'), status: 'DISPLAY_ONLY' },
        { label: 'Paper fill state', value: metadataValue(lifecycle, 'paper_fill_state', 'NOT STARTED'), status: 'REVIEW' },
        { label: 'Demo proof state', value: metadataValue(lifecycle, 'demo_proof_state', 'LOCKED'), status: 'LOCKED' },
        { label: 'Live lock state', value: metadataValue(lifecycle, 'live_lock_state', 'LIVE LOCKED'), status: 'LOCKED' },
        { label: 'Reconciliation state', value: metadataValue(lifecycle, 'reconciliation_state', TRADE_METADATA_DEFAULTS.reconciliationStatus), status: 'REVIEW' },
        { label: 'Lifecycle transition count', value: metadataValue(lifecycle, 'lifecycle_transition_count', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Last lifecycle event', value: metadataValue(lifecycle, 'last_lifecycle_event', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Last lifecycle timestamp', value: metadataValue(lifecycle, 'last_lifecycle_timestamp', 'UNKNOWN'), status: 'REVIEW' }
      ]
    },
    {
      title: 'Balance / PnL',
      symbol: 'reconciliation',
      status: 'REVIEW',
      rows: [
        { label: 'Balance before', value: metadataValue(balancePnl, 'balance_before', formatMoney(balanceBefore)), status: 'REVIEW' },
        { label: 'Balance after', value: metadataValue(balancePnl, 'balance_after', formatMoney(balanceAfter)), status: 'REVIEW' },
        { label: 'Equity', value: metadataValue(balancePnl, 'equity', formatMoney(liveOperatorPanel.equity)), status: 'REVIEW' },
        { label: 'Open risk', value: metadataValue(balancePnl, 'open_risk', formatMoney(liveOperatorPanel.open_risk)), status: 'CLEAR' },
        { label: 'Open trades', value: metadataValue(balancePnl, 'open_trades', String(liveOperatorPanel.active_trades ?? 0)), status: 'CLEAR' },
        { label: 'Active trades', value: metadataValue(balancePnl, 'active_trades', String(liveOperatorPanel.active_trades ?? 0)), status: 'CLEAR' },
        { label: 'Result pips', value: metadataValue(balancePnl, 'result_pips', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Realized P/L', value: metadataValue(balancePnl, 'realized_pl', formatMoney(liveOperatorPanel.realized_pl)), status: 'REVIEW' },
        { label: 'Unrealized P/L', value: metadataValue(balancePnl, 'unrealized_pl', 'EVIDENCE MISSING'), status: 'REVIEW' },
        { label: 'Fees/spread/slippage', value: metadataValue(balancePnl, 'fees_spread_slippage', 'EVIDENCE MISSING'), status: 'REVIEW' }
      ]
    },
    {
      title: 'Evidence / Replay',
      symbol: 'evidence-ledger',
      status: 'DISPLAY_ONLY',
      rows: [
        { label: 'Evidence ledger summary', value: metadataValue(evidenceReplay, 'evidence_ledger_summary', 'Fixture-backed display evidence only'), status: 'DISPLAY_ONLY' },
        { label: 'Evidence path', value: evidencePath, status: 'REVIEW' },
        { label: 'Evidence freshness', value: metadataValue(evidenceReplay, 'evidence_freshness', liveOperatorPanel.evidence_freshness ?? runtimeFreshness), status: 'REVIEW' },
        { label: 'Source label', value: metadataValue(evidenceReplay, 'source_label', operatorStatusFixture.source_label ?? 'MOCK_DATA'), status: 'DISPLAY_ONLY' },
        { label: 'Generated timestamp', value: metadataValue(evidenceReplay, 'generated_timestamp', mockRuntimeVisibility.generatedAt ?? operatorStatusFixture.generated_at ?? 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Validator status', value: metadataValue(evidenceReplay, 'validator_status', 'UNKNOWN'), status: 'REVIEW' },
        { label: 'Session replay status', value: metadataValue(evidenceReplay, 'session_replay_status', 'NOT STARTED'), status: 'REVIEW' },
        { label: 'Safety boundary report status', value: metadataValue(evidenceReplay, 'safety_boundary_report_status', 'DISPLAY ONLY'), status: 'DISPLAY_ONLY' },
        { label: 'Blocker count', value: metadataValue(evidenceReplay, 'blocker_count', String(blockerCount)), status: blockerCount ? 'BLOCKED' : 'CLEAR' },
        { label: 'Next-action recommendation', value: metadataValue(evidenceReplay, 'next_action_recommendation', liveOperatorPanel.next_safe_action ?? runtimeContract.next_safe_action), status: 'REVIEW' }
      ]
    }
  ];

  return (
    <Section id="trade-metadata-matrix" eyebrow="Trade Metadata / Evidence Ledger" title="Sanitized trade metadata matrix" status="LOCKED" symbol="trade-ledger">
      <div className="tradeLedgerHero">
        <div className="tradeLedgerIdentity">
          <AiosSymbol name="trade-ticket" label="Sanitized trade ticket icon" size="md" />
          <div>
            <span>AIOS Trade #</span>
            <strong>{tradeNumber}</strong>
            <p>Internal sanitized identifier only. No broker account ID, broker order ID, credential, or execution authority is displayed.</p>
          </div>
        </div>
        <div className="tradeLedgerStatusRail" aria-label="Trade ledger execution boundary">
          <StatusChip label="DISPLAY_ONLY" status="DISPLAY_ONLY" icon />
          <StatusChip label="LIVE LOCKED" status="LOCKED" icon />
          <StatusChip label="BROKER LOCKED" status="LOCKED" icon />
        </div>
      </div>

      <div className="tradeLedgerGrid" aria-label="High-signal trade metadata fields">
        {priorityMetrics.map((metric) => (
          <LedgerMetric
            key={metric.label}
            label={metric.label}
            value={metric.value}
            status={metric.status}
            symbol={metric.symbol}
          />
        ))}
      </div>

      <details className="tradeMetadataDrawer">
        <summary>
          <span className="drawerSummaryLabel">
            <AiosSymbol name="evidence-ledger" label="Full metadata evidence ledger icon" size="sm" />
            Full metadata groups
          </span>
          <StatusChip label="DISPLAY_ONLY" status="DISPLAY_ONLY" />
        </summary>
        <div className="metadataGroupGrid">
          {metadataGroups.map((group) => (
            <article className="metadataGroupCard" key={group.title}>
              <header>
                <div className="sectionTitleRow">
                  <AiosSymbol name={group.symbol} label={`${group.title} icon`} size="sm" />
                  <h3>{group.title}</h3>
                </div>
                <StatusChip label={group.status} status={group.status} />
              </header>
              <div className="metadataRows">
                {group.rows.map((row) => (
                  <DataRow key={`${group.title}-${row.label}`} label={row.label} value={row.value} status={row.status} />
                ))}
              </div>
            </article>
          ))}
        </div>
      </details>
    </Section>
  );
}

function MoneyCockpitPanel() {
  const capitalFlow = liveOperatorPanel.capital_flow ?? mockRuntimeVisibility.capital_flow_projection ?? {};
  const accountAliases = Array.isArray(capitalFlow.account_aliases)
    ? capitalFlow.account_aliases
    : ['TRADING_FLOAT', 'RESERVE_ACCOUNT', 'PROFIT_VAULT', 'TAX_BUCKET', 'OPERATING_ACCOUNT', 'WITHDRAWAL_TARGET', 'RESUPPLY_SOURCE', 'COMPOUND_BUCKET'];
  const safetyStatements = Array.isArray(capitalFlow.safety_statements)
    ? capitalFlow.safety_statements
    : [
        'AIOS does not hold funds.',
        'AIOS does not move money from this dashboard.',
        'Account aliases only.',
        'Real transfers require future connector proof and human approval.',
        'Instant withdrawal/deposit depends on supported broker, bank, or payment rails.',
        'This panel is policy and simulation only.'
      ];
  const recommendations = Array.isArray(capitalFlow.recommendations) ? capitalFlow.recommendations : ['HOLD'];
  const requestPreviews = Array.isArray(capitalFlow.request_previews) ? capitalFlow.request_previews : [];
  const simulationLadder = Array.isArray(capitalFlow.simulation_ladder) ? capitalFlow.simulation_ladder : [];
  const visibleFields = Array.isArray(capitalFlow.default_visible_fields) ? capitalFlow.default_visible_fields : [];
  const collapsedFields = Array.isArray(capitalFlow.collapsed_fields) ? capitalFlow.collapsed_fields : [];
  const moneyCockpitStatus = metadataValue(capitalFlow, 'money_cockpit_status', 'MONEY_COCKPIT_DISPLAY_ONLY');
  const moneyLadderStatus = metadataValue(capitalFlow, 'money_ladder_status', 'MONEY_LADDER_100K_GOAL_SIMULATION_ONLY');
  const capitalFlowStatus = metadataValue(capitalFlow, 'capital_flow_status', 'CAPITAL_FLOW_DISPLAY_ONLY');
  const treasuryAutomationStatus = metadataValue(
    capitalFlow,
    'treasury_automation_status',
    'TREASURY_AUTOMATION_POLICY_ONLY'
  );
  const moneyRelevanceStatus = metadataValue(capitalFlow, 'money_relevance_status', 'MONEY_RELEVANT_VISIBLE');
  const rangeSimulationStatus = metadataValue(
    capitalFlow,
    'range_simulation_status',
    'RANGE_SIMULATION_READY_0_99_TO_100000'
  );
  const nextSafeCapitalAction = metadataValue(
    capitalFlow,
    'next_safe_capital_action',
    mockRuntimeVisibility.capital_flow_projection?.next_safe_action ?? 'Review display-only treasury policy simulation.'
  );

  const capitalMetrics = [
    { label: 'Trading float', value: metadataValue(capitalFlow, 'trading_float', formatMoney(liveOperatorPanel.balance)), status: 'DISPLAY_ONLY', symbol: 'money-cockpit' },
    { label: 'Reserve', value: metadataValue(capitalFlow, 'reserve_balance', 'UNKNOWN'), status: 'DISPLAY_ONLY', symbol: 'capital-flow' },
    { label: 'Profit vault', value: metadataValue(capitalFlow, 'profit_vault_balance', 'UNKNOWN'), status: 'DISPLAY_ONLY', symbol: 'funds-sweep' },
    { label: 'Tax bucket', value: metadataValue(capitalFlow, 'tax_bucket_balance', 'UNKNOWN'), status: 'DISPLAY_ONLY', symbol: 'balance-ladder' },
    { label: 'Daily P/L', value: metadataValue(capitalFlow, 'daily_pl', formatMoney(liveOperatorPanel.realized_pl)), status: 'REVIEW', symbol: 'risk-bankroll' },
    { label: 'Equity', value: metadataValue(capitalFlow, 'equity', formatMoney(liveOperatorPanel.equity)), status: 'DISPLAY_ONLY', symbol: 'capital-flow' },
    { label: 'Risk budget', value: metadataValue(capitalFlow, 'available_risk_budget', 'UNKNOWN'), status: 'REVIEW', symbol: 'risk-bankroll' },
    { label: 'Capital cap', value: metadataValue(capitalFlow, 'maximum_trading_float', 'UNKNOWN'), status: 'REVIEW', symbol: 'withdrawal-gate' },
    { label: 'Daily loss left', value: metadataValue(capitalFlow, 'daily_loss_left', 'UNKNOWN'), status: 'REVIEW', symbol: 'risk-bankroll' }
  ];

  const capitalRows = [
    { label: 'Sweep ready', value: metadataValue(capitalFlow, 'sweep_ready', '0.00'), status: 'REVIEW' },
    { label: 'Resupply need', value: metadataValue(capitalFlow, 'resupply_need', '0.00'), status: 'REVIEW' },
    { label: 'Compound progress', value: metadataValue(capitalFlow, 'compounding_progress', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Withdrawal gate', value: metadataValue(capitalFlow, 'withdrawal_status', 'WITHDRAWAL_BLOCKED_BY_APPROVAL'), status: 'LOCKED' },
    { label: 'Broker proof', value: metadataValue(capitalFlow, 'broker_proof_status', 'MISSING'), status: 'LOCKED' },
    { label: 'Connector proof', value: metadataValue(capitalFlow, 'connector_proof_status', 'FUTURE_CONNECTOR_PROOF_REQUIRED'), status: 'LOCKED' },
    { label: 'Approval gate', value: metadataValue(capitalFlow, 'approval_status', 'HUMAN_APPROVAL_REQUIRED'), status: 'LOCKED' },
    { label: 'Risk freeze', value: metadataValue(capitalFlow, 'risk_freeze_status', 'CLEAR'), status: 'CLEAR' },
    { label: 'Capital Flow status', value: capitalFlowStatus, status: 'DISPLAY_ONLY' },
    { label: 'Money relevance', value: moneyRelevanceStatus, status: 'DISPLAY_ONLY' }
  ];

  const thresholdRows = [
    { label: 'Minimum float floor', value: metadataValue(capitalFlow, 'minimum_trading_float', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Maximum float cap', value: metadataValue(capitalFlow, 'maximum_trading_float', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Sweep threshold', value: metadataValue(capitalFlow, 'sweep_threshold', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Resupply threshold', value: metadataValue(capitalFlow, 'resupply_threshold', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Compounding threshold', value: metadataValue(capitalFlow, 'compounding_threshold', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Compounding target', value: metadataValue(capitalFlow, 'compounding_target', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Max withdrawal/event', value: metadataValue(capitalFlow, 'max_withdrawal_per_event', 'UNKNOWN'), status: 'LOCKED' },
    { label: 'Max deposit/event', value: metadataValue(capitalFlow, 'max_deposit_per_event', 'UNKNOWN'), status: 'LOCKED' },
    { label: 'Cooldown minutes', value: metadataValue(capitalFlow, 'cooldown_minutes', 'UNKNOWN'), status: 'REVIEW' },
    { label: 'Maintenance window', value: metadataValue(capitalFlow, 'maintenance_window', 'NOT_ACTIVE'), status: 'REVIEW' },
    { label: 'Last capital action', value: metadataValue(capitalFlow, 'last_capital_action', 'NONE'), status: 'DISPLAY_ONLY' }
  ];

  return (
    <Section id="money-cockpit" eyebrow="Money Cockpit / Treasury" title="Capital flow simulator" status="DISPLAY_ONLY" symbol="money-cockpit">
      <div className="capitalFlowHero">
        <div className="tradeLedgerIdentity">
          <AiosSymbol name="money-cockpit" label="Money cockpit icon" size="md" />
          <div>
            <span>Money cockpit status</span>
            <strong>{moneyCockpitStatus}</strong>
            <p>Bank-style balance visibility, policy simulation, and draft money actions only. 100000 is a goal ladder ceiling, not guaranteed growth.</p>
          </div>
        </div>
        <div className="tradeLedgerStatusRail" aria-label="Capital flow execution boundary">
          <StatusChip label="DISPLAY_ONLY" status="DISPLAY_ONLY" icon />
          <StatusChip label="NO MONEY MOVEMENT" status="LOCKED" icon />
          <StatusChip label="100K GOAL NOT GUARANTEED" status="REVIEW" icon />
          <StatusChip label="HUMAN APPROVAL REQUIRED" status="LOCKED" icon />
        </div>
      </div>

      <div className="capitalFlowTruthList" aria-label="Capital flow safety doctrine">
        {safetyStatements.map((statement) => (
          <span key={statement}>{statement}</span>
        ))}
      </div>

      <div className="tradeLedgerGrid capitalFlowMetricGrid" aria-label="High-signal capital policy fields">
        {capitalMetrics.map((metric) => (
          <LedgerMetric
            key={metric.label}
            label={metric.label}
            value={metric.value}
            status={metric.status}
            symbol={metric.symbol}
          />
        ))}
      </div>

      <div className="cockpitDataGrid capitalFlowStatusGrid" aria-label="Capital request gate statuses">
        {capitalRows.map((row) => (
          <DataRow key={row.label} label={row.label} value={row.value} status={row.status} />
        ))}
      </div>

      <div className="nextActionBand">
        <span>Next safe capital action</span>
        <strong>{nextSafeCapitalAction}</strong>
      </div>

      <details className="tradeMetadataDrawer capitalFlowDrawer">
        <summary>
          <span className="drawerSummaryLabel">
            <AiosSymbol name="balance-ladder" label="Money cockpit drawer icon" size="sm" />
            100K goal ladder, aliases, requests, and gates
          </span>
          <StatusChip label={rangeSimulationStatus} status="DISPLAY_ONLY" />
        </summary>
        <div className="metadataGroupGrid capitalFlowDrawerGrid">
          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="balance-ladder" label="Balance ladder icon" size="sm" />
                <h3>0.99 to 100000 Goal Ladder</h3>
              </div>
              <StatusChip label={moneyLadderStatus} status="DISPLAY_ONLY" />
            </header>
            <div className="capitalFlowScenarioGrid">
              {simulationLadder.map((scenario) => (
                <div className="capitalFlowScenario" key={metadataValue(scenario, 'balance', 'BALANCE')}>
                  <span>{metadataValue(scenario, 'capital_tier', metadataValue(scenario, 'balance_tier', 'UNKNOWN'))}</span>
                  <strong>{metadataValue(scenario, 'balance', 'UNKNOWN')}</strong>
                  {scenario.risk_cap ? <small>{metadataValue(scenario, 'risk_cap')} risk cap</small> : null}
                  <p>{metadataValue(scenario, 'next_money_action', 'Review money policy.')}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="capital-flow" label="Account alias icon" size="sm" />
                <h3>Account Aliases</h3>
              </div>
              <StatusChip label="ALIASES ONLY" status="DISPLAY_ONLY" />
            </header>
            <div className="capitalFlowAliasGrid">
              {accountAliases.map((alias) => (
                <span key={alias}>{alias}</span>
              ))}
            </div>
          </article>

          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="funds-sweep" label="Capital recommendation icon" size="sm" />
                <h3>Recommendations</h3>
              </div>
              <StatusChip label={treasuryAutomationStatus} status="LOCKED" />
            </header>
            <div className="capitalFlowRecommendationList">
              {recommendations.map((recommendation) => (
                <span key={recommendation}>{recommendation}</span>
              ))}
            </div>
          </article>

          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="compound-target" label="Capital threshold icon" size="sm" />
                <h3>Policy Thresholds</h3>
              </div>
              <StatusChip label="DISPLAY_ONLY" status="DISPLAY_ONLY" />
            </header>
            <div className="metadataRows">
              {thresholdRows.map((row) => (
                <DataRow key={row.label} label={row.label} value={row.value} status={row.status} />
              ))}
            </div>
          </article>

          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="withdrawal-gate" label="Draft request preview icon" size="sm" />
                <h3>Request Previews</h3>
              </div>
              <StatusChip label="NO TRANSFER" status="LOCKED" />
            </header>
            <div className="capitalFlowRequestList">
              {requestPreviews.length ? (
                requestPreviews.map((request) => (
                  <div className="capitalFlowRequest" key={metadataValue(request, 'request_id', 'REQUEST-DRAFT')}>
                    <span>{metadataValue(request, 'request_type', 'DRAFT')}</span>
                    <strong>{metadataValue(request, 'amount', 'UNKNOWN')}</strong>
                    <p>{metadataValue(request, 'source_alias', 'SOURCE_ALIAS')} to {metadataValue(request, 'destination_alias', 'DESTINATION_ALIAS')}</p>
                    <StatusChip label={metadataValue(request, 'status', 'DRAFT_ONLY')} status="LOCKED" />
                  </div>
                ))
              ) : (
                <p className="capitalFlowEmpty">No transfer request preview drafted.</p>
              )}
            </div>
          </article>

          <article className="metadataGroupCard">
            <header>
              <div className="sectionTitleRow">
                <AiosSymbol name="risk-bankroll" label="Money relevance icon" size="sm" />
                <h3>Money Relevance Rule</h3>
              </div>
              <StatusChip label={moneyRelevanceStatus} status="DISPLAY_ONLY" />
            </header>
            <div className="capitalFlowRecommendationList">
              {visibleFields.slice(0, 8).map((field) => (
                <span key={field}>{field}</span>
              ))}
              {collapsedFields.slice(0, 7).map((field) => (
                <span key={field}>{field}: COLLAPSED</span>
              ))}
            </div>
          </article>
        </div>
      </details>
    </Section>
  );
}

function TraderCockpit() {
  return (
    <Section id="trader-cockpit" eyebrow="Trader Cockpit" title="Pair and risk state" status="LOCKED" symbol="trader-cockpit">
      <div className="traderGrid">
        <div className="selectedPair">
          <div className="selectedPairHead">
            <AiosSymbol name="pair-eur-usd" label="Selected EUR/USD pair icon" size="wide" />
            <span>Selected pair</span>
          </div>
          <strong>{formatInstrument(liveOperatorPanel.instrument)}</strong>
          <p>Direction candidate: {upper(liveOperatorPanel.side)} from fixture evidence only.</p>
        </div>
        <div className="riskStack">
          <DataRow label="Kill switch" value={upper(liveOperatorPanel.kill_switch)} status="LOCKED" />
          <DataRow label="Daily stop" value={upper(liveOperatorPanel.daily_stop_gate)} status="CLEAR" />
          <DataRow label="Open risk" value={formatMoney(liveOperatorPanel.open_risk)} status="CLEAR" />
          <DataRow label="Active trades" value={String(liveOperatorPanel.active_trades ?? 0)} status="CLEAR" />
          <DataRow label="Realized P/L" value={formatMoney(liveOperatorPanel.realized_pl)} status="REVIEW" />
        </div>
      </div>
      <div className="pairCodeRail" aria-label="Watchlist pair codes and research-only market badges">
        {PAIR_CODES.map((pair) => (
          <span className={PAIR_SYMBOLS[pair] ? 'pairCodeChip pairCodeChip-symbol' : 'pairCodeChip'} key={pair}>
            {PAIR_SYMBOLS[pair] ? (
              <AiosSymbol name={PAIR_SYMBOLS[pair]} label={`${pair} research badge`} size="wide" framed={false} />
            ) : null}
            {pair}
          </span>
        ))}
      </div>
    </Section>
  );
}

function ForexCapabilityTruth() {
  return (
    <Section id="forex-capability-truth" eyebrow="Forex Capability Truth" title="What can trade now" status="LOCKED" symbol="risk-shield">
      <div className="capabilityAnswer">
        <span>Can AIOS trade forex live right now?</span>
        <strong>NO — LIVE FOREX LOCKED.</strong>
      </div>
      <div className="capabilityGrid">
        {FOREX_CAPABILITY_STATES.map((item) => (
          <article className="capabilityCard" key={item.label}>
            <div>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
            <StatusChip label={item.status} status={item.status} />
            <p>{item.detail}</p>
          </article>
        ))}
      </div>
      <div className="truthStatementList" aria-label="Forex execution truth">
        {FOREX_TRUTH_STATEMENTS.map((statement) => (
          <span key={statement}>{statement}</span>
        ))}
      </div>
    </Section>
  );
}

function BotAlgoState() {
  const blockers = blockedActions.length;
  const queuePressure = Number(runtimeQueue.waitingForApproval ?? 0) + Number(runtimeQueue.retryable ?? 0);

  return (
    <Section id="bot-algo-state" eyebrow="Bot / Algo State" title="Strategy boundary" status="REVIEW" symbol="bot-algo">
      <div className="cockpitDataGrid">
        <DataRow label="Strategy" value="SUPERTREND PAPER_ONLY" status="REVIEW" />
        <DataRow label="Signal feed" value="NO DATA" status="REVIEW" />
        <DataRow label="Automation state" value={upper(runtimeState.status)} status="REVIEW" />
        <DataRow label="Evidence freshness" value={upper(runtimeState.freshness)} status="REVIEW" />
        <DataRow label="Blockers" value={String(blockers)} status={blockers ? 'BLOCKED' : 'CLEAR'} />
        <DataRow label="Queue pressure" value={String(queuePressure)} status={queuePressure ? 'REVIEW' : 'CLEAR'} />
      </div>
    </Section>
  );
}

function SiteAccessState() {
  return (
    <Section id="site-access-state" eyebrow="Site / Access State" title="Security display" status="REVIEW" symbol="site-access">
      <div className="cockpitDataGrid">
        <DataRow label="Registry safety" value={upper(accessSummary.status)} status={accessSummary.status === 'PASS' ? 'CLEAR' : 'REVIEW'} />
        <DataRow label="Telemetry" value={upper(telemetrySummary.status)} status="REVIEW" />
        <DataRow label="Worker status" value={upper(workerSummary.status)} status="REVIEW" />
        <DataRow label="Login UX" value="NOT PROVEN" status="REVIEW" />
        <DataRow label="SSO provider" value="CONTRACT ONLY" status="REVIEW" />
        <DataRow label="Secret handling" value="NO TOKENS READ" status="CLEAR" />
      </div>
    </Section>
  );
}

function ProofSafetyDrawer() {
  return (
    <details className="cockpitDrawer proofDrawer">
      <summary>
        <span className="drawerSummaryLabel">
          <AiosSymbol name="proof-evidence" label="Proof evidence icon" size="sm" />
          Proof / Safety Drawer
        </span>
        <StatusChip label="LOCKED" status="LOCKED" />
      </summary>

      <div className="drawerGrid">
        <article>
          <h3>Safety constants</h3>
          <DataRow label="Execution allowed" value={asBooleanText(EXECUTION_ALLOWED)} status="LOCKED" />
          <DataRow label="Mutation allowed" value={asBooleanText(MUTATION_ALLOWED)} status="LOCKED" />
          <DataRow label="Live trading allowed" value={asBooleanText(LIVE_TRADING_ALLOWED)} status="LOCKED" />
          <DataRow label="Approval required" value={asBooleanText(runtimeContract.approval_required)} status="REVIEW" />
        </article>

        <article>
          <h3>Evidence sources</h3>
          <DataRow label="Runtime source" value={runtimeContract.source_path ?? 'UNKNOWN'} status="REVIEW" />
          <DataRow label="Operator source" value={operatorStatusFixture.provenance?.source_path ?? 'UNKNOWN'} status="REVIEW" />
          <DataRow label="Generated" value={mockRuntimeVisibility.generatedAt ?? 'UNKNOWN'} status="REVIEW" />
          <DataRow label="Next action source" value={upper(nextSafeActionFixture.source)} status="REVIEW" />
        </article>
      </div>

      <div className="blockedActionList">
        <h3>Blocked actions</h3>
        <ul>
          {blockedActions.map((action) => (
            <li key={action}>{action}</li>
          ))}
        </ul>
      </div>

      {warnings.length ? (
        <div className="blockedActionList">
          <h3>Warnings</h3>
          <ul>
            {warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <details className="liveBridgeDrawer">
        <summary>
          <span>Final live bridge evidence</span>
          <StatusChip label="REVIEW" status="REVIEW" />
        </summary>
        <AIOSLiveOperatorPanel />
      </details>
    </details>
  );
}

function UtilityDock() {
  return (
    <details className="cockpitDrawer utilityDock">
      <summary>
        <span className="drawerSummaryLabel">
          <AiosSymbol name="music-utility" label="Music utility icon" size="sm" />
          Utilities / Music Dock
        </span>
        <StatusChip label="SECONDARY" status="DISPLAY_ONLY" />
      </summary>
      <PreservedLegacyModules focus="all" />
    </details>
  );
}

export default function MinimalOperatorDashboard() {
  return (
    <div className="runtimePage">
      <main className="operatorPortal traderCockpitShell">
        <header className="cockpitTopbar">
          <div className="cockpitTitleBlock">
            <AiosSymbol name="aios-core" label="AIOS core cockpit icon" size="lg" />
            <div>
              <p className="eyebrow">AIOS dashboard</p>
              <h1>Trader Cockpit</h1>
              <p className="headerSummary">
                Display-only operator truth for AIOS, access, trading boundary, broker lock, bot state,
                and next safe action.
              </p>
            </div>
          </div>
          <div className="cockpitTopbarChips" aria-label="Dashboard safety state">
            <StatusChip label="DISPLAY_ONLY" status="DISPLAY_ONLY" icon />
            <StatusChip label="LOCKED" status="LOCKED" icon />
            <StatusChip label="NO BROKER" status="BLOCKED" icon />
          </div>
        </header>

        <nav className="cockpitNav" aria-label="Cockpit sections">
          <a href="#command-center">Command</a>
          <a href="#trader-cockpit">Trader</a>
          <a href="#trade-metadata-matrix">Ledger</a>
          <a href="#money-cockpit">Money</a>
          <a href="#forex-capability-truth">Capability</a>
          <a href="#bot-algo-state">Bot</a>
          <a href="#site-access-state">Access</a>
          <a href="#proof-safety">Proof</a>
        </nav>

        <div className="cockpitGrid">
          <CommandCenter />
          <TraderCockpit />
          <TradeMetadataMatrix />
          <MoneyCockpitPanel />
          <ForexCapabilityTruth />
          <BotAlgoState />
          <SiteAccessState />
        </div>

        <section id="proof-safety" className="cockpitSecondaryRail" aria-label="Proof, safety, and utilities">
          <ProofSafetyDrawer />
          <UtilityDock />
        </section>
      </main>
    </div>
  );
}
