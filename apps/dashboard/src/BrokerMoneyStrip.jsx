import { useEffect, useMemo, useState } from 'react';
import fallbackMoneyStrip from '../mock-data/aios-oanda-money-strip-v1.example.json';

const MONEY_STRIP_API = '/api/forex/oanda/money-strip';

function show(value, fallback = 'UNKNOWN') {
  if (value === null || value === undefined || value === '') {
    return fallback;
  }
  return String(value).toUpperCase();
}

function moneyValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'UNKNOWN';
  }
  if (typeof value === 'number') {
    return new Intl.NumberFormat('en-US', {
      maximumFractionDigits: 2,
      minimumFractionDigits: 2
    }).format(value);
  }
  return String(value).toUpperCase();
}

function pairValue(value) {
  return show(value).replace('_', '/');
}

function blockedModel(reason) {
  return {
    ...fallbackMoneyStrip,
    blocked_reason: reason,
    status: 'BLOCKED',
    stale_status: 'BLOCKED',
    execution_allowed: false,
    order_placement_allowed: false,
    demo_order_allowed: false,
    live_order_allowed: false
  };
}

function MoneyMetric({ label, value, emphasis = false }) {
  return (
    <div className={emphasis ? 'brokerMoneyMetric brokerMoneyMetric-emphasis' : 'brokerMoneyMetric'}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default function BrokerMoneyStrip() {
  const [model, setModel] = useState(fallbackMoneyStrip);

  useEffect(() => {
    let active = true;

    async function loadMoneyStrip() {
      try {
        const response = await fetch(MONEY_STRIP_API, { method: 'GET' });
        if (!response.ok) {
          throw new Error(`HTTP_${response.status}`);
        }
        const payload = await response.json();
        if (active) {
          setModel({
            ...fallbackMoneyStrip,
            ...payload,
            execution_allowed: false,
            order_placement_allowed: false,
            demo_order_allowed: false,
            live_order_allowed: false
          });
        }
      } catch (error) {
        if (active) {
          setModel(blockedModel(`READ_ERROR:${error.name || 'Error'}`));
        }
      }
    }

    loadMoneyStrip();

    return () => {
      active = false;
    };
  }, []);

  const metrics = useMemo(() => {
    const realized = moneyValue(model.realized_pl);
    const unrealized = moneyValue(model.unrealized_pl);
    const marginUsed = moneyValue(model.margin_used);
    const marginAvailable = moneyValue(model.margin_available);
    const marginPercent = moneyValue(model.margin_used_percent);
    return [
      { label: 'BAL', value: moneyValue(model.balance), emphasis: true },
      { label: 'NAV', value: moneyValue(model.nav ?? model.equity), emphasis: true },
      { label: 'P/L', value: `${realized} / ${unrealized}` },
      { label: 'MARGIN', value: `${marginUsed} / ${marginAvailable} ${marginPercent}` },
      {
        label: 'OPEN',
        value: `${show(model.open_trade_count, '0')}T ${show(model.open_position_count, '0')}P ${show(model.pending_order_count, '0')}O`
      },
      { label: 'PAIR', value: pairValue(model.selected_pair) },
      { label: 'SPREAD', value: moneyValue(model.spread) },
      {
        label: 'TARGET',
        value: `${show(model.target_return_min_percent, '100')}%-${show(model.target_return_max_percent, '120')}%`
      },
      { label: 'EXEC OFF', value: 'FALSE' }
    ];
  }, [model]);

  const state = show(model.status, 'BLOCKED');
  const source = show(model.source_label, 'NO_READ_MODEL_AVAILABLE');
  const updated = show(model.freshness_utc, 'UNKNOWN');

  return (
    <section id="broker-money-strip" className="brokerMoneyStrip" aria-label="Read-only broker money strip">
      <div className="brokerMoneyHead">
        <div>
          <p className="eyebrow">Broker money</p>
          <h2>OANDA read-only strip</h2>
        </div>
        <div className="brokerMoneyState" aria-label="Read-only money status">
          <span>{state}</span>
          <strong>{source}</strong>
          <small>{updated}</small>
        </div>
      </div>

      <div className="brokerMoneyMetrics">
        {metrics.map((metric) => (
          <MoneyMetric key={metric.label} {...metric} />
        ))}
      </div>
    </section>
  );
}
