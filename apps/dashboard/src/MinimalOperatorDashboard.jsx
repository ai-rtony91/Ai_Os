import { useMemo, useState } from 'react';
import './MinimalOperatorDashboard.css';

const HOME_ROOMS = [
  {
    id: 'safety',
    icon: '🛡️',
    label: 'Safety, security, and login boundary',
  },
  {
    id: 'forex',
    icon: '🤖',
    label: 'Forex bot',
  },
  {
    id: 'system',
    icon: '🛠️',
    label: 'System and tools',
  },
  {
    id: 'music',
    icon: '🎵',
    label: 'Music and utilities',
  },
];

const PAIRS = [
  { pair: 'EUR/USD', flags: '🇪🇺 🇺🇸', state: 'WATCH' },
  { pair: 'GBP/USD', flags: '🇬🇧 🇺🇸', state: 'WATCH' },
  { pair: 'USD/JPY', flags: '🇺🇸 🇯🇵', state: 'WATCH' },
  { pair: 'USD/CAD', flags: '🇺🇸 🇨🇦', state: 'WATCH' },
  { pair: 'AUD/USD', flags: '🇦🇺 🇺🇸', state: 'WATCH' },
  { pair: 'NZD/USD', flags: '🇳🇿 🇺🇸', state: 'WATCH' },
];

const DETAIL_COPY = {
  safety: {
    icon: '🛡️',
    title: 'Safety',
    rows: [
      ['LOGIN', 'PROTECTED'],
      ['SSO', 'NOT PROVEN'],
      ['CLOUDFLARE', 'NOT PROVEN'],
      ['STATUS', 'OPERATOR REQUIRED'],
    ],
    note: 'Credential, account, Azure, Cloudflare, and broker actions are not available from this dashboard.',
  },
  system: {
    icon: '🛠️',
    title: 'System',
    rows: [
      ['TOOLS', 'LOCAL'],
      ['RUNTIME', 'DISPLAY ONLY'],
      ['SCHEDULER', 'OFF'],
      ['WEBHOOK', 'OFF'],
    ],
    note: 'System controls stay informational until Anthony approves a separate scoped lane.',
  },
  music: {
    icon: '🎵',
    title: 'Music',
    rows: [
      ['DOCK', 'TUCKED'],
      ['UTILITY', 'LOCAL'],
      ['AUTOPLAY', 'OFF'],
      ['NETWORK', 'OFF'],
    ],
    note: 'Music and utility controls are kept out of the home screen to preserve the four-icon command surface.',
  },
};

function IconHome({ onOpen }) {
  return (
    <section className="minimalHome" aria-label="AIOS owner command rooms">
      <header className="homeTopbar">
        <span className="brandMark">AIOS</span>
        <span className="executionLock">EXEC OFF</span>
      </header>

      <nav className="iconRoomGrid" aria-label="Primary dashboard rooms">
        {HOME_ROOMS.map((room) => (
          <button
            aria-label={room.label}
            className="iconRoomButton"
            key={room.id}
            onClick={() => onOpen(room.id)}
            title={room.label}
            type="button"
          >
            <span aria-hidden="true">{room.icon}</span>
          </button>
        ))}
      </nav>
    </section>
  );
}

function BackButton({ onClick }) {
  return (
    <button aria-label="Back to AIOS home" className="backButton" onClick={onClick} title="Back" type="button">
      <span aria-hidden="true">←</span>
    </button>
  );
}

function DetailRoom({ room, onBack }) {
  if (room === 'forex') {
    return <ForexRoom onBack={onBack} />;
  }

  const detail = DETAIL_COPY[room];

  return (
    <section className="detailRoom" aria-labelledby={`${room}-title`}>
      <BackButton onClick={onBack} />
      <header className="detailHeader">
        <span aria-hidden="true" className="detailIcon">
          {detail.icon}
        </span>
        <h1 id={`${room}-title`}>{detail.title}</h1>
      </header>

      <div className="detailGrid" aria-label={`${detail.title} status`}>
        {detail.rows.map(([label, value]) => (
          <div className="statusTile" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <p className="roomNote">{detail.note}</p>
    </section>
  );
}

function ForexRoom({ onBack }) {
  return (
    <section className="detailRoom forexRoom" aria-labelledby="forex-title">
      <BackButton onClick={onBack} />
      <header className="detailHeader">
        <span aria-hidden="true" className="detailIcon">
          🤖
        </span>
        <h1 id="forex-title">Forex Bot</h1>
      </header>

      <div className="forexLockStrip" aria-label="Forex execution state">
        <span>READ ONLY</span>
        <span>EXEC OFF</span>
        <span>BROKER LOCKED</span>
      </div>

      <div className="pairGrid" aria-label="Read-only Forex pair watchlist">
        {PAIRS.map((item) => (
          <article className="pairBadge" key={item.pair}>
            <span aria-hidden="true" className="pairFlags">
              {item.flags}
            </span>
            <strong>{item.pair}</strong>
            <small>{item.state}</small>
          </article>
        ))}
      </div>

      <p className="roomNote">
        Trading execution remains locked. This room contains read-only pair identity and no order controls.
      </p>
    </section>
  );
}

export default function MinimalOperatorDashboard() {
  const [activeRoom, setActiveRoom] = useState('home');
  const roomIds = useMemo(() => new Set(HOME_ROOMS.map((room) => room.id)), []);
  const isHome = activeRoom === 'home' || !roomIds.has(activeRoom);

  return (
    <main className="minimalOperatorDashboard" aria-label="AIOS minimal operator dashboard">
      {isHome ? (
        <IconHome onOpen={setActiveRoom} />
      ) : (
        <DetailRoom room={activeRoom} onBack={() => setActiveRoom('home')} />
      )}
    </main>
  );
}
