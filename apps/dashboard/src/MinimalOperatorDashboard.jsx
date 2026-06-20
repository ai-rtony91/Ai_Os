import React, { useEffect, useState } from 'react';
import './App.css';

const initialTruthState = {
  allowed: false,
  decision: 'blocked',
  blocked_reason: 'not_loaded',
  blocked_reasons: ['DASHBOARD_NOT_LOADED'],
  warnings: ['DISPLAY_ONLY_NO_RUNTIME_EVIDENCE'],
  paper_only: true,
  mode: 'PAPER_ONLY',
  session_id: null,
  display_state: 'NO_RUNTIME_EVIDENCE',
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
    label: 'NO_RUNTIME_EVIDENCE',
    status: 'NO_RUNTIME_EVIDENCE'
  },
  session_replay_status: null,
  evidence_ledger_status: {
    status: 'NO_RUNTIME_EVIDENCE',
    reason: 'dashboard_started_without_session_projection'
  },
  candidates: {
    total: 0,
    accepted: 0,
    rejected: 0
  },
  previews: {
    created: 0,
    rejected: 0
  },
  risk: {
    accepted: 0,
    rejected: 0
  },
  open_trades: 0,
  closed_trades: 0,
  pnl: {
    gross_profit: 0,
    gross_loss: 0,
    net_pnl: 0,
    profit_factor: null
  },
  balance: {
    start: null,
    end: null,
    change: null
  },
  drawdown: {
    max_drawdown: 0,
    max_drawdown_pct: null
  },
  risk_usage: null,
  missing_evidence_warnings: ['DISPLAY_ONLY_NO_RUNTIME_EVIDENCE'],
  blocked_reasons: ['DISPLAY_ONLY_NO_RUNTIME_EVIDENCE'],
  next_safe_action: 'POLL_SESSION_STATUS_WHEN_REPLAY_EXISTS'
};

const MetricBlock = ({ title, children }) => (
  <div style={{
    border: '1px solid #d0d7de',
    borderRadius: 6,
    padding: '0.75rem',
    marginBottom: '0.75rem',
    backgroundColor: '#f6f8fa'
  }}>
    <h4 style={{ marginTop: 0 }}>{title}</h4>
    {children}
  </div>
);

const Row = ({ label, value }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
    <span>{label}</span>
    <span style={{ fontFamily: 'monospace' }}>{value}</span>
  </div>
);

const MinimalOperatorDashboard = () => {
  const [state, setState] = useState(initialTruthState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTruth = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch('/api/forex/session-status', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
          throw new Error(`Session status HTTP ${response.status}`);
        }
        const payload = await response.json();
        setState({
          ...initialTruthState,
          ...payload,
          safety: payload.safety || initialTruthState.safety
        });
      } catch (fetchError) {
        setError(fetchError.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    fetchTruth();
  }, []);

  return (
    <div style={{ padding: '1rem' }}>
      <h1>Forex Dashboard Truth</h1>
      <p style={{ color: '#444', marginBottom: '1rem' }}>
        DISPLAY_ONLY. This view reflects server-side paper/session/evidence projection only.
      </p>
      {error && (
        <p style={{ color: '#b00020' }}>{`Error: ${error}`}</p>
      )}
      <MetricBlock title="Display Safety">
        <Row label="Mode" value={state.mode} />
        <Row label="Source" value={state.source} />
        <Row label="Display State" value={state.display_state} />
        <Row label="Session Id" value={state.session_id || 'N/A'} />
        <Row label="Freshness" value={state.freshness?.status || 'NO_RUNTIME_EVIDENCE'} />
        <Row label="Safety" value={JSON.stringify(state.safety)} />
      </MetricBlock>

      <MetricBlock title="Session Replay Status">
        <Row label="Session Replay Allowed" value={String(state.session_replay_status?.allowed)} />
        <Row label="Replay Decision" value={state.session_replay_status?.decision || 'blocked'} />
        <Row label="Replay Blocked Reason" value={state.session_replay_status?.blocked_reason || 'none'} />
        <Row label="Event Count" value={state.session_replay_status?.event_count ?? 0} />
        <Row label="Source" value={state.session_replay_status?.source || 'N/A'} />
      </MetricBlock>

      <MetricBlock title="Evidence Ledger">
        <Row label="Ledger Status" value={state.evidence_ledger_status?.status || 'NO_RUNTIME_EVIDENCE'} />
        <Row label="Ledger Reason" value={state.evidence_ledger_status?.reason || 'NO_RUNTIME_EVIDENCE'} />
      </MetricBlock>

      <MetricBlock title="Candidates">
        <Row label="Total Candidates" value={state.candidates?.total || 0} />
        <Row label="Accepted Candidates" value={state.candidates?.accepted || 0} />
        <Row label="Rejected Candidates" value={state.candidates?.rejected || 0} />
      </MetricBlock>

      <MetricBlock title="Previews / Risk">
        <Row label="Previews Created" value={state.previews?.created || 0} />
        <Row label="Previews Rejected" value={state.previews?.rejected || 0} />
        <Row label="Risk Accepted" value={state.risk?.accepted || 0} />
        <Row label="Risk Rejected" value={state.risk?.rejected || 0} />
      </MetricBlock>

      <MetricBlock title="Trades">
        <Row label="Open Trades" value={state.open_trades || 0} />
        <Row label="Closed Trades" value={state.closed_trades || 0} />
        <Row label="Wins" value={state.pnl?.wins || 0} />
        <Row label="Losses" value={state.pnl?.losses || 0} />
      </MetricBlock>

      <MetricBlock title="P/L and Balance">
        <Row label="Gross Profit" value={state.pnl?.gross_profit ?? 0} />
        <Row label="Gross Loss" value={state.pnl?.gross_loss ?? 0} />
        <Row label="Net P/L" value={state.pnl?.net_pnl ?? 0} />
        <Row label="Profit Factor" value={state.pnl?.profit_factor ?? 'n/a'} />
        <Row label="Balance Start" value={state.balance?.start ?? 'N/A'} />
        <Row label="Balance End" value={state.balance?.end ?? 'N/A'} />
        <Row label="Balance Change" value={state.balance?.change ?? 'N/A'} />
      </MetricBlock>

      <MetricBlock title="Risk and Drawdown">
        <Row label="Drawdown" value={state.drawdown?.max_drawdown ?? 0} />
        <Row label="Drawdown %" value={state.drawdown?.max_drawdown_pct ?? 'n/a'} />
        <Row label="Risk Usage" value={JSON.stringify(state.risk_usage)} />
      </MetricBlock>

      <MetricBlock title="Missing Evidence / Blocked Reasons">
        <Row label="Blocked Reasons" value={state.blocked_reasons?.join(', ') || 'NONE'} />
        <Row label="Warnings" value={state.warnings?.join(', ') || 'NONE'} />
        <Row label="Missing Evidence Warnings" value={state.missing_evidence_warnings?.join(', ') || 'NONE'} />
      </MetricBlock>

      <MetricBlock title="Next Safe Action">
        <Row label="Next Safe Action" value={state.next_safe_action || 'START_RUNTIME_EVIDENCE'} />
      </MetricBlock>

      {loading && <p>Loading latest session replay truth...</p>}
    </div>
  );
};

export default MinimalOperatorDashboard;
