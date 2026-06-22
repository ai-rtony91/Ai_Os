import liveOperatorPanel from "../mock-data/aios-live-operator-panel-v1.example.json";
import "./AIOSLiveOperatorPanel.css";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2
});

function displayValue(value) {
  if (value === null || value === undefined || value === "") {
    return "UNKNOWN";
  }
  if (typeof value === "number") {
    return currencyFormatter.format(value);
  }
  return String(value);
}

function TruthCell({ label, value, tone = "neutral" }) {
  return (
    <div className={`liveTruthCell liveTruthCell-${tone}`}>
      <span>{label}</span>
      <strong>{displayValue(value)}</strong>
    </div>
  );
}

function statusTone(value) {
  const text = String(value ?? "").toUpperCase();
  if (text.includes("READY") || text.includes("CLEAR") || text === "DISABLED") {
    return "ready";
  }
  if (text.includes("BLOCK") || text.includes("ENABLED") || text.includes("NOT_CLEAR")) {
    return "blocked";
  }
  if (text.includes("REVIEW") || text.includes("UNKNOWN")) {
    return "review";
  }
  return "neutral";
}

export default function AIOSLiveOperatorPanel() {
  const panel = liveOperatorPanel;
  const blockers = panel.blockers?.length ? panel.blockers : ["No runtime blockers supplied in fixture."];

  return (
    <section className="aiosLiveOperatorPanel" aria-label="AIOS final live operator bridge">
      <div className="liveOperatorTopline">
        <div>
          <p className="liveOperatorEyebrow">Final live operator bridge V1</p>
          <h2>Single micro-trade arming surface</h2>
          <p>
            This dashboard shows readiness evidence only. It does not place the order and it does not
            hold credentials or account identifiers.
          </p>
        </div>
        <div className={`liveBridgeBadge liveBridgeBadge-${statusTone(panel.live_bridge_status)}`}>
          {panel.live_bridge_status}
        </div>
      </div>

      <div className="liveNoticeGrid">
        <article>
          <span>Dashboard authority</span>
          <strong>No order execution</strong>
          <p>Final execution requires a separate explicit protected live action authorization.</p>
        </article>
        <article>
          <span>Fixture state</span>
          <strong>{String(panel.fixture_data)}</strong>
          <p>Broker call performed: {String(panel.broker_call_performed)}</p>
        </article>
      </div>

      <div className="liveTruthGrid">
        <TruthCell label="Mode" value={panel.mode} />
        <TruthCell label="Balance" value={panel.balance} />
        <TruthCell label="Equity" value={panel.equity} />
        <TruthCell label="Realized P/L" value={panel.realized_pl} />
        <TruthCell label="Open risk" value={panel.open_risk} />
        <TruthCell label="Active trades" value={panel.active_trades} />
        <TruthCell label="Instrument" value={panel.instrument} />
        <TruthCell label="Side" value={panel.side} />
        <TruthCell label="Units" value={panel.units} />
        <TruthCell label="Stop loss" value={panel.stop_loss} />
        <TruthCell label="Take profit" value={panel.take_profit} />
        <TruthCell label="Max loss gate" value={panel.max_loss_gate} tone={statusTone(panel.max_loss_gate)} />
        <TruthCell label="Daily stop gate" value={panel.daily_stop_gate} tone={statusTone(panel.daily_stop_gate)} />
        <TruthCell label="Kill switch" value={panel.kill_switch} tone={statusTone(panel.kill_switch)} />
        <TruthCell
          label="Broker connector"
          value={panel.broker_connector_status}
          tone={statusTone(panel.broker_connector_status)}
        />
        <TruthCell label="Evidence freshness" value={panel.evidence_freshness} />
      </div>

      <div className="liveOperatorFooter">
        <div>
          <h3>Blockers</h3>
          <ul>
            {blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        </div>
        <div className="liveNextAction">
          <span>Next safe action</span>
          <strong>{panel.next_safe_action}</strong>
        </div>
      </div>
    </section>
  );
}

