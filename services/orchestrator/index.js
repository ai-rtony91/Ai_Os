const express = require('express');
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
