const express = require('express');
const path = require('path');
const { execFileSync } = require('child_process');
const {
  buildForexDashboardTruthStatus
} = require('./forexDashboardTruthStatus');
const {
  buildForexDemoConnectorProofClosure
} = require('./forexDemoConnectorProofClosure');

const router = express.Router();

const noopReplay = () => ({
  allowed: false,
  decision: 'blocked',
  blocked_reason: 'missing_or_invalid_session_replay',
  blocked_reasons: ['NO_RUNTIME_EVIDENCE'],
  warnings: ['NO_RUNTIME_EVIDENCE'],
  paper_only: true,
  mode: 'PAPER_ONLY',
  session_id: null,
  evidence_path: 'relative:in-memory',
  source: 'forex_dashboard_truth_status',
  safety: {
    paper_only: true,
    broker: false,
    live_trading: false,
    credentials: false,
    real_orders: false,
    network_access: false
  },
  next_safe_action: 'START_RUNTIME_SESSION_AND_REPLAY'
});

function buildMoneyStripUnavailableReadModel(blockReason) {
  return {
    status: 'BLOCKED',
    source_label: 'OANDA_READ_ONLY_DISABLED_OR_MISCONFIGURED',
    mode: 'READ_ONLY',
    stale_status: 'BLOCKED',
    broker: 'OANDA',
    freshness_utc: new Date().toISOString(),
    blocked_reason: blockReason,
    live_order_allowed: false,
    order_placement_allowed: false,
    execution_allowed: false,
    balance: 'BLOCKED',
    nav: 'BLOCKED',
    equity: 'BLOCKED',
    currency: 'BLOCKED',
    margin_available: 'BLOCKED',
    margin_used: 'BLOCKED',
    margin_used_percent: 'BLOCKED',
    withdrawal_limit: 'BLOCKED',
    realized_pl: 'BLOCKED',
    unrealized_pl: 'BLOCKED',
    open_trade_count: 0,
    open_position_count: 0,
    pending_order_count: 0,
    selected_pair: 'UNKNOWN',
    bid: 'BLOCKED',
    ask: 'BLOCKED',
    spread: 'BLOCKED',
    source: 'services/orchestrator',
    safety: {
      read_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      account_id: false,
      network_access: false,
      no_write: true
    },
  };
}

function isMoneyStripReadOnlyEnabled() {
  return (
    process.env.AIOS_FOREX_READONLY_LIVE_ENABLE === '1' &&
    (process.env.AIOS_FOREX_BROKER || '').toLowerCase() === 'oanda'
  );
}

function getMoneyStripViaPython() {
  const pythonCommand = process.env.PYTHON || 'python';
  const output = execFileSync(
    pythonCommand,
    [
      '-c',
      'import json, os, sys; '
        + 'sys.path.insert(0, os.path.join(os.getcwd(), "src")); '
        + 'from forex_delivery.read_only_live_data_bridge import build_read_only_live_data_bridge_read_model; '
        + 'print(json.dumps(build_read_only_live_data_bridge_read_model()))'
    ],
    {
      encoding: 'utf8',
      cwd: path.resolve(__dirname, '..', '..'),
      timeout: 4500,
      windowsHide: true
    }
  );

  const lines = String(output).split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const jsonText = lines.at(-1) || '{}';
  const model = JSON.parse(jsonText);
  const moneyStrip = model && model.money_strip ? model.money_strip : null;
  if (!moneyStrip) {
    return {
      ...buildMoneyStripUnavailableReadModel('Python model missing money_strip.'),
      source_label: 'OANDA_READ_ONLY_INCOMPLETE',
      blocked_reason: 'Python bridge returned model without money strip.',
      model_available: false,
    };
  }
  return {
    ...moneyStrip,
    model_available: true,
    source: 'services/orchestrator-python-bridge',
    money_read_model: moneyStrip,
    safety: {
      read_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      account_id: false,
      network_access: false,
      no_write: true
    }
  };
}

router.get('/health', (_req, res) => {
  res.json({
    allowed: true,
    decision: 'allowed',
    paper_only: true,
    mode: 'PAPER_ONLY',
    service: 'forex-dashboard-truth-status',
    safety: {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    }
  });
});

router.get('/api/forex/session-status', (req, res) => {
  const sessionId = req.query.sessionId || req.query.session_id || null;
  const evidence = req.body && req.body.evidence ? req.body.evidence : null;
  const status = buildForexDashboardTruthStatus({
    session_id: sessionId,
    evidence
  });

  res.json(status);
});

router.get('/api/forex/replay-status', (req, res) => {
  const sessionId = req.query.sessionId || req.query.session_id || null;
  const replayStatus = noopReplay();
  const proofClosure = buildForexDemoConnectorProofClosure(sessionId, replayStatus);
  res.json({
    allowed: true,
    decision: 'allowed',
    blocked_reason: 'none',
    blocked_reasons: [],
    warnings: [],
    paper_only: true,
    mode: 'PAPER_ONLY',
    session_id: sessionId,
    source: 'proof_closure_only',
    replay_status: replayStatus,
    proof_closure: proofClosure,
    next_safe_action: 'USE_SESSION_STATUS_ENDPOINT',
    safety: {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    }
  });
});

router.get('/api/forex/oanda/money-strip', (req, res) => {
  if (!isMoneyStripReadOnlyEnabled()) {
    res.json(
      buildMoneyStripUnavailableReadModel(
        'Set AIOS_FOREX_READONLY_LIVE_ENABLE=1 and AIOS_FOREX_BROKER=oanda to enable read-only bridge.'
      )
    );
    return;
  }

  if (!process.env.OANDA_API_TOKEN || !process.env.OANDA_ACCOUNT_ID) {
    res.json(
      buildMoneyStripUnavailableReadModel(
        'OANDA_API_TOKEN and OANDA_ACCOUNT_ID runtime presence required. Values are never exposed by this endpoint.'
      )
    );
    return;
  }

  try {
    const moneyStripReadModel = getMoneyStripViaPython();
    res.json(moneyStripReadModel);
  } catch (error) {
    res.json(
      buildMoneyStripUnavailableReadModel(
        `READ_ONLY_BRIDGE_BLOCKED:${error.name || 'Error'}`
      )
    );
  }
});

router.get('/forex/status', (req, res) => {
  const sessionId = req.query.sessionId || req.query.session_id || null;
  const proofClosure = buildForexDemoConnectorProofClosure(sessionId, null);
  res.json({
    status: 'display_only',
    source: 'legacy_route_mapped_to_projection',
    allowed: true,
    decision: 'allowed',
    blocked_reason: 'none',
    blocked_reasons: [],
    warnings: ['LEGACY_ROUTE_MAPPED_TO_DISPLAY_ONLY'],
    paper_only: true,
    mode: 'PAPER_ONLY',
    session_id: sessionId,
    proof_closure: proofClosure,
    next_safe_action: 'USE_SESSION_STATUS_ENDPOINT',
    safety: {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    }
  });
});

module.exports = router;
module.exports.router = router;
