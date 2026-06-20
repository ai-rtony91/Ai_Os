const { buildForexDashboardTruthStatus } = require('./forexDashboardTruthStatus');

const buildForexDemoConnectorProofClosure = (session_id = null, session_replay_payload = null) => {
  const replayProjection = buildForexDashboardTruthStatus({
    session_id,
    evidence: session_replay_payload
  });

  const noEvidence = replayProjection.paper_only && !session_replay_payload;
  return {
    proof_session_id: session_id || null,
    paper_only: true,
    mode: 'PAPER_ONLY',
    display_only: true,
    read_model: replayProjection,
    status: noEvidence ? 'NO_RUNTIME_EVIDENCE' : 'READ_MODEL_PROJECTED',
    label: noEvidence
      ? 'DISPLAY_ONLY_NO_RUNTIME_EVIDENCE'
      : 'DISPLAY_ONLY_TRUSTED_REPLAY',
    safety: {
      paper_only: true,
      broker: false,
      live_trading: false,
      credentials: false,
      real_orders: false,
      network_access: false
    },
    metadata: {
      provenance: 'proof_closure_display_only',
      source_of_truth: 'evidence_ledger_session_replay_projection'
    }
  };
};

module.exports = {
  buildForexDemoConnectorProofClosure
};
