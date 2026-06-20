const DISPLAY_ONLY_STATUS = 'DISPLAY_ONLY';
const NO_RUNTIME_EVIDENCE = 'NO_RUNTIME_EVIDENCE';

const defaultReplayStatus = () => ({
  allowed: false,
  decision: 'blocked',
  blocked_reason: 'no_runtime_replay',
  blocked_reasons: [NO_RUNTIME_EVIDENCE],
  warnings: ['NO_RUNTIME_EVIDENCE'],
  paper_only: true,
  mode: 'PAPER_ONLY',
  session_id: null,
  event_count: 0,
  counts_by_event_type: {},
  total_candidates: 0,
  accepted_candidates: 0,
  rejected_candidates: 0,
  previews_created: 0,
  previews_rejected: 0,
  risk_accepted: 0,
  risk_rejected: 0,
  trades_opened: 0,
  trades_closed: 0,
  wins: 0,
  losses: 0,
  breakeven: 0,
  gross_profit: 0.0,
  gross_loss: 0.0,
  net_pnl: 0.0,
  profit_factor: null,
  balance_start: null,
  balance_end: null,
  balance_change: null,
  max_drawdown: 0.0,
  max_drawdown_pct: null,
  risk_usage: null,
  rejection_reasons: [],
  missing_evidence_warnings: [NO_RUNTIME_EVIDENCE],
  source_event_ids: [],
  replay_summary: {
    open_trade_ids: [],
    closed_trade_ids: []
  },
  safety: {
    paper_only: true,
    broker: false,
    live_trading: false,
    credentials: false,
    real_orders: false,
    network_access: false
  },
  next_safe_action: 'START_CANONICAL_SESSION_REPLAY'
});

const normalizeNumber = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return 0.0;
  }
  return Number(value.toFixed(4));
};

const toInt = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return 0;
  }
  return Math.max(0, Math.floor(value));
};

const normalizeReplay = (replay) => {
  if (!replay || typeof replay !== 'object') {
    return defaultReplayStatus();
  }
  const replaySummary = replay.replay_summary || {};
  const sourceEventIds = Array.isArray(replay.source_event_ids)
    ? replay.source_event_ids
    : [];

  return {
    allowed: Boolean(replay.allowed),
    decision: replay.decision || 'blocked',
    blocked_reason: replay.blocked_reason || 'none',
    blocked_reasons: Array.isArray(replay.blocked_reasons)
      ? replay.blocked_reasons
      : [],
    warnings: Array.isArray(replay.warnings) ? replay.warnings : [],
    paper_only: replay.paper_only !== false,
    mode: 'PAPER_ONLY',
    session_id: replay.session_id || null,
    event_count: toInt(replay.event_count),
    counts_by_event_type: replay.counts_by_event_type || {},
    total_candidates: toInt(replay.total_candidates),
    accepted_candidates: toInt(replay.accepted_candidates),
    rejected_candidates: toInt(replay.rejected_candidates),
    previews_created: toInt(replay.previews_created),
    previews_rejected: toInt(replay.previews_rejected),
    risk_accepted: toInt(replay.risk_accepted),
    risk_rejected: toInt(replay.risk_rejected),
    trades_opened: toInt(replay.trades_opened),
    trades_closed: toInt(replay.trades_closed),
    wins: toInt(replay.wins),
    losses: toInt(replay.losses),
    breakeven: toInt(replay.breakeven),
    gross_profit: normalizeNumber(replay.gross_profit),
    gross_loss: normalizeNumber(replay.gross_loss),
    net_pnl: normalizeNumber(replay.net_pnl),
    profit_factor: replay.profit_factor === null ? null : normalizeNumber(replay.profit_factor),
    balance_start: typeof replay.balance_start === 'number' ? replay.balance_start : null,
    balance_end: typeof replay.balance_end === 'number' ? replay.balance_end : null,
    balance_change: typeof replay.balance_change === 'number' ? replay.balance_change : null,
    max_drawdown: normalizeNumber(replay.max_drawdown),
    max_drawdown_pct: typeof replay.max_drawdown_pct === 'number' ? replay.max_drawdown_pct : null,
    risk_usage: replay.risk_usage || null,
    rejection_reasons: Array.isArray(replay.rejection_reasons) ? replay.rejection_reasons : [],
    missing_evidence_warnings: Array.isArray(replay.missing_evidence_warnings)
      ? replay.missing_evidence_warnings
      : [],
    source_event_ids: sourceEventIds,
    replay_summary: {
      open_trade_ids: Array.isArray(replaySummary.open_trade_ids)
        ? replaySummary.open_trade_ids
        : [],
      closed_trade_ids: Array.isArray(replaySummary.closed_trade_ids)
        ? replaySummary.closed_trade_ids
        : []
    },
    safety: replay.safety || {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    },
    next_safe_action: replay.next_safe_action || 'START_CANONICAL_SESSION_REPLAY',
    source: replay.source || 'session_replay_projection'
  };
};

const buildForexDashboardTruthStatus = ({ session_id = null, evidence = null } = {}) => {
  const replay = normalizeReplay(evidence);
  const hasEvidence = evidence && Object.prototype.hasOwnProperty.call(evidence, 'session_id');

  const noRuntimeEvidence = !hasEvidence || replay.allowed === false;
  const displayState = noRuntimeEvidence ? NO_RUNTIME_EVIDENCE : DISPLAY_ONLY_STATUS;

  return {
    allowed: replay.allowed,
    decision: replay.decision,
    blocked_reason: replay.blocked_reason || 'none',
    blocked_reasons: replay.blocked_reasons || [],
    warnings: replay.warnings || [],
    paper_only: true,
    mode: 'PAPER_ONLY',
    session_id,
    display_state: displayState,
    source: 'automation.forex_engine.session_replay',
    safety: {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    },
    freshness: {
      label: noRuntimeEvidence ? 'NO_RUNTIME_EVIDENCE' : 'HAS_REPLAY_DATA',
      status: noRuntimeEvidence ? NO_RUNTIME_EVIDENCE : 'TRUSTED_REPLAY'
    },
    session_replay_status: replay,
    evidence_ledger_status: {
      status: noRuntimeEvidence ? NO_RUNTIME_EVIDENCE : 'RECEIVED',
      reason: noRuntimeEvidence ? NO_RUNTIME_EVIDENCE : 'evidence_present'
    },
    candidates: {
      total: replay.total_candidates,
      accepted: replay.accepted_candidates,
      rejected: replay.rejected_candidates
    },
    previews: {
      created: replay.previews_created,
      rejected: replay.previews_rejected
    },
    risk: {
      accepted: replay.risk_accepted,
      rejected: replay.risk_rejected
    },
    open_trades: replay.trades_opened,
    closed_trades: replay.trades_closed,
    pnl: {
      gross_profit: replay.gross_profit,
      gross_loss: replay.gross_loss,
      net_pnl: replay.net_pnl,
      profit_factor: replay.profit_factor
    },
    balance: {
      start: replay.balance_start,
      end: replay.balance_end,
      change: replay.balance_change
    },
    drawdown: {
      max_drawdown: replay.max_drawdown,
      max_drawdown_pct: replay.max_drawdown_pct
    },
    risk_usage: replay.risk_usage,
    missing_evidence_warnings: replay.missing_evidence_warnings || [NO_RUNTIME_EVIDENCE],
    blocked_reasons: replay.blocked_reasons || [],
    next_safe_action: replay.next_safe_action || 'START_CANONICAL_SESSION_REPLAY'
  };
};

module.exports = {
  DISPLAY_ONLY_STATUS,
  NO_RUNTIME_EVIDENCE,
  buildForexDashboardTruthStatus
};
