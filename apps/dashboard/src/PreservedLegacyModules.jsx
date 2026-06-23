import { useEffect, useRef, useState } from 'react';
import './PreservedLegacyModules.css';

const THEME_OPTIONS = [
  { value: 'default', label: 'Default AI_OS Dark' },
  { value: 'terminal-green', label: 'Terminal Green' },
  { value: 'cyan-command', label: 'Cyan Command' },
  { value: 'amber-warning', label: 'Amber Warning' },
  { value: 'high-contrast', label: 'High Contrast' },
];

const THEME_PALETTES = {
  default: {
    '--legacy-accent': '#38bdf8',
    '--legacy-accent-soft': 'rgba(56, 189, 248, 0.14)',
    '--legacy-glow': 'rgba(56, 189, 248, 0.18)',
    '--legacy-line': 'rgba(88, 118, 160, 0.34)',
  },
  'terminal-green': {
    '--legacy-accent': '#37ff88',
    '--legacy-accent-soft': 'rgba(55, 255, 136, 0.14)',
    '--legacy-glow': 'rgba(55, 255, 136, 0.18)',
    '--legacy-line': 'rgba(55, 255, 136, 0.28)',
  },
  'cyan-command': {
    '--legacy-accent': '#22d3ee',
    '--legacy-accent-soft': 'rgba(34, 211, 238, 0.14)',
    '--legacy-glow': 'rgba(34, 211, 238, 0.18)',
    '--legacy-line': 'rgba(34, 211, 238, 0.28)',
  },
  'amber-warning': {
    '--legacy-accent': '#f6c453',
    '--legacy-accent-soft': 'rgba(246, 196, 83, 0.16)',
    '--legacy-glow': 'rgba(246, 196, 83, 0.18)',
    '--legacy-line': 'rgba(246, 196, 83, 0.28)',
  },
  'high-contrast': {
    '--legacy-accent': '#ffffff',
    '--legacy-accent-soft': 'rgba(255, 255, 255, 0.18)',
    '--legacy-glow': 'rgba(255, 255, 255, 0.22)',
    '--legacy-line': 'rgba(255, 255, 255, 0.42)',
  },
};

const STORAGE_KEYS = {
  theme: 'aios.dashboard.theme',
  dockCollapsed: 'aios.youtubeDockCollapsed',
  radio: 'AIOS_YOUTUBE_DOCK_STATE_V1',
};

const YOUTUBE_API_URL = 'https://www.youtube.com/iframe_api';
const LOCAL_SERVER_COMMAND = 'Local HTTP preview: python -m http.server 8080';
const LOCAL_FILE_FALLBACK = 'Embedded playback unavailable in local file preview. Use local server preview.';
const RESUME_MESSAGE = 'Press Play to resume';

const TRACKS = [
  { videoId: 'VFzsSbdS7Sk', playlistId: 'RDVFzsSbdS7Sk', title: 'AI_OS Dock Track' },
  { videoId: 'g5VSkAHGgF8', playlistId: 'RDAMVMLwd7WQ8L5dQ', title: 'Dock Rotation 2' },
  { videoId: 'nZpdxwnQmjI', playlistId: 'RDAMVMLwd7WQ8L5dQ', title: '97Kickstvr - Waiting For You' },
  { videoId: 'UaB9JBzgPPA', playlistId: 'RDAMVMLwd7WQ8L5dQ', title: 'Last Memory' },
];

const DEFAULT_TRACK = TRACKS[0];
const IS_FILE_PREVIEW = typeof window !== 'undefined' && window.location.protocol === 'file:';

function clampVolume(value) {
  return Math.max(0, Math.min(100, Number(value) || 0));
}

function readStoredTheme() {
  if (typeof window === 'undefined') {
    return 'default';
  }

  try {
    const stored = window.localStorage.getItem(STORAGE_KEYS.theme);
    return THEME_OPTIONS.some((option) => option.value === stored) ? stored : 'default';
  } catch {
    return 'default';
  }
}

function readSavedRadioState() {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const parsed = JSON.parse(window.localStorage.getItem(STORAGE_KEYS.radio) || '{}');
    if (!parsed || typeof parsed !== 'object') {
      return null;
    }

    return {
      time: Math.max(0, Number(parsed.time) || 0),
      volume: clampVolume(parsed.volume ?? 70),
      muted: parsed.muted === true,
      collapsed: parsed.collapsed === true,
      wasPlaying: parsed.wasPlaying === true,
      savedAt: Number(parsed.savedAt) || 0,
    };
  } catch {
    return null;
  }
}

function readStoredDockCollapsed(savedState) {
  if (typeof window === 'undefined') {
    return savedState?.collapsed ?? true;
  }

  try {
    const stored = window.localStorage.getItem(STORAGE_KEYS.dockCollapsed);
    if (stored === 'true') {
      return true;
    }
    if (stored === 'false') {
      return false;
    }
    return savedState?.collapsed ?? true;
  } catch {
    return savedState?.collapsed ?? true;
  }
}

function ControlButton({ active = false, label, onClick, stateLabel, title }) {
  return (
    <button
      className={`button button-readonly legacyDockButton ${active ? 'is-active' : ''}`}
      type="button"
      onClick={onClick}
      title={title}
    >
      <span>{label}</span>
      <small>{stateLabel}</small>
    </button>
  );
}

function LegacyModuleCard({ eyebrow, title, children, statusClass = 'status-neutral' }) {
  return (
    <article className="legacyModuleCard">
      <div className="legacyModuleCardHead">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
        </div>
        <span className={`statusPill ${statusClass}`}>{eyebrow}</span>
      </div>
      {children}
    </article>
  );
}

export default function PreservedLegacyModules() {
  const savedRadioState = useState(() => readSavedRadioState())[0];
  const [theme, setTheme] = useState(() => readStoredTheme());
  const [dockCollapsed, setDockCollapsed] = useState(() => readStoredDockCollapsed(savedRadioState));
  const [volume, setVolume] = useState(() => savedRadioState?.volume ?? 70);
  const [muted, setMuted] = useState(() => savedRadioState?.muted ?? false);
  const [isPlaying, setIsPlaying] = useState(() => savedRadioState?.wasPlaying ?? false);
  const [radioStatus, setRadioStatus] = useState(() => RESUME_MESSAGE);
  const [previewNote, setPreviewNote] = useState(() => (
    IS_FILE_PREVIEW ? LOCAL_FILE_FALLBACK : LOCAL_SERVER_COMMAND
  ));

  const playerMountRef = useRef(null);
  const playerRef = useRef(null);
  const pendingActionRef = useRef(null);
  const scriptLoadingRef = useRef(false);
  const embedModeRef = useRef('playlist');
  const singleFallbackAttemptedRef = useRef(false);
  const hydratedRef = useRef(false);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEYS.theme, theme);
    } catch {
      // Visual preference only; ignore unavailable storage.
    }
  }, [theme]);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.aiosLegacyTheme = theme;
    }
  }, [theme]);

  useEffect(() => {
    hydratedRef.current = true;
  }, []);

  useEffect(() => {
    if (!hydratedRef.current) {
      return;
    }

    saveRadioState();
  }, [dockCollapsed, isPlaying, muted, volume]);

  useEffect(() => {
    const handlePageHide = () => {
      saveRadioState();
    };

    window.addEventListener('pagehide', handlePageHide);
    return () => window.removeEventListener('pagehide', handlePageHide);
  }, []);

  useEffect(() => {
    return () => {
      if (typeof playerRef.current?.destroy === 'function') {
        playerRef.current.destroy();
      }
      playerRef.current = null;
    };
  }, []);

  function saveRadioState(overrides = {}) {
    try {
      const player = playerRef.current;
      const snapshot = {
        time: 0,
        volume: clampVolume(overrides.volume ?? volume),
        muted: overrides.muted ?? muted,
        collapsed: overrides.collapsed ?? dockCollapsed,
        wasPlaying: overrides.wasPlaying ?? isPlaying,
        savedAt: Date.now(),
      };

      if (player) {
        if (typeof player.getCurrentTime === 'function') {
          snapshot.time = Math.max(0, Number(player.getCurrentTime()) || 0);
        }

        if (typeof player.getVolume === 'function') {
          snapshot.volume = clampVolume(player.getVolume() ?? snapshot.volume);
        }

        if (typeof player.isMuted === 'function') {
          snapshot.muted = player.isMuted();
        }
      }

      window.localStorage.setItem(STORAGE_KEYS.radio, JSON.stringify(snapshot));
      window.localStorage.setItem(STORAGE_KEYS.dockCollapsed, String(snapshot.collapsed));
    } catch {
      // Safe UI/player state only; ignore unavailable storage.
    }
  }

  function applyPreviewState() {
    if (IS_FILE_PREVIEW) {
      setRadioStatus(LOCAL_FILE_FALLBACK);
      setPreviewNote(LOCAL_SERVER_COMMAND);
      return;
    }

    const stored = readSavedRadioState();
    if (!stored) {
      setRadioStatus(RESUME_MESSAGE);
      setPreviewNote(LOCAL_SERVER_COMMAND);
      return;
    }

    setDockCollapsed(stored.collapsed);
    setVolume(stored.volume);
    setMuted(stored.muted);
    setRadioStatus(RESUME_MESSAGE);
    setPreviewNote(LOCAL_SERVER_COMMAND);

    const player = playerRef.current;
    if (player) {
      try {
        if (typeof player.setVolume === 'function') {
          player.setVolume(stored.volume);
        }

        if (stored.muted && typeof player.mute === 'function') {
          player.mute();
        } else if (!stored.muted && typeof player.unMute === 'function') {
          player.unMute();
        }

        if (stored.time > 0 && typeof player.seekTo === 'function') {
          player.seekTo(stored.time, true);
        }
      } catch {
        // Player restoration is best-effort only.
      }
    }
  }

  function createPlayer() {
    if (!playerMountRef.current || playerRef.current || !window.YT?.Player) {
      return;
    }

    embedModeRef.current = 'playlist';
    singleFallbackAttemptedRef.current = false;

    playerRef.current = new window.YT.Player(playerMountRef.current, {
      height: '200',
      width: '320',
      videoId: DEFAULT_TRACK.videoId,
      playerVars: {
        autoplay: 0,
        playsinline: 1,
        rel: 0,
        list: DEFAULT_TRACK.playlistId,
        listType: 'playlist',
      },
      events: {
        onReady: () => {
          setRadioStatus(RESUME_MESSAGE);
          applyPreviewState();

          const pendingAction = pendingActionRef.current;
          pendingActionRef.current = null;

          if (pendingAction) {
            runPlayerAction(pendingAction);
          }
        },
        onError: () => {
          if (embedModeRef.current === 'playlist' && !singleFallbackAttemptedRef.current) {
            singleFallbackAttemptedRef.current = true;
            embedModeRef.current = 'video';
            setRadioStatus('Playlist unavailable - trying video');

            try {
              playerRef.current?.loadVideoById(DEFAULT_TRACK.videoId);
              return;
            } catch {
              // Fall through to the unavailable message below.
            }
          }

          setRadioStatus('Embed unavailable inside AI_OS.');
          setMuted(false);
        },
        onStateChange: (event) => {
          if (!window.YT?.PlayerState) {
            return;
          }

          if (event.data === window.YT.PlayerState.PLAYING) {
            setIsPlaying(true);
            setRadioStatus('Playing inside AI_OS');
            saveRadioState({ wasPlaying: true });
            return;
          }

          if (event.data === window.YT.PlayerState.PAUSED || event.data === window.YT.PlayerState.ENDED) {
            setIsPlaying(false);
            setRadioStatus('Paused');
            saveRadioState({ wasPlaying: false });
          }
        },
      },
    });
  }

  function loadYouTubeApi() {
    if (typeof window === 'undefined') {
      return;
    }

    if (window.YT?.Player) {
      createPlayer();
      return;
    }

    if (scriptLoadingRef.current) {
      return;
    }

    scriptLoadingRef.current = true;
    window.onYouTubeIframeAPIReady = () => {
      scriptLoadingRef.current = false;
      createPlayer();
    };

    const existingScript = document.querySelector('script[data-aios-youtube-api="true"]');
    if (existingScript) {
      return;
    }

    const script = document.createElement('script');
    script.async = true;
    script.src = YOUTUBE_API_URL;
    script.dataset.aiosYoutubeApi = 'true';
    document.head.appendChild(script);
  }

  function ensurePlayer(action) {
    if (playerRef.current) {
      return true;
    }

    if (IS_FILE_PREVIEW) {
      setRadioStatus(LOCAL_FILE_FALLBACK);
      setPreviewNote(LOCAL_SERVER_COMMAND);
      return false;
    }

    pendingActionRef.current = action;
    setRadioStatus('Loading inside AI_OS');
    setPreviewNote(LOCAL_SERVER_COMMAND);
    loadYouTubeApi();
    return false;
  }

  function runPlayerAction(action) {
    const player = playerRef.current;
    if (!player || !window.YT?.PlayerState) {
      return;
    }

    try {
      if (action === 'play') {
        const state = typeof player.getPlayerState === 'function' ? player.getPlayerState() : null;
        if (state === window.YT.PlayerState.PLAYING) {
          player.pauseVideo();
          setIsPlaying(false);
          setRadioStatus('Paused');
          saveRadioState({ wasPlaying: false });
          return;
        } else {
          player.playVideo();
          setIsPlaying(true);
          setRadioStatus('Playing inside AI_OS');
          saveRadioState({ wasPlaying: true });
          return;
        }
      }

      if (action === 'next') {
        player.nextVideo();
      }

      if (action === 'back') {
        player.previousVideo();
      }

      if (action === 'mute') {
        const isMuted = typeof player.isMuted === 'function' && player.isMuted();
        if (isMuted) {
          player.unMute();
          setMuted(false);
        } else {
          player.mute();
          setMuted(true);
        }
      }

      saveRadioState();
    } catch {
      setRadioStatus('Music control unavailable.');
    }
  }

  function handleDockControl(action) {
    if (action === 'expand') {
      const nextCollapsed = !dockCollapsed;
      setDockCollapsed(nextCollapsed);
      saveRadioState({ collapsed: nextCollapsed });
      return;
    }

    if (!ensurePlayer(action)) {
      return;
    }

    runPlayerAction(action);
  }

  function handleVolumeChange(nextValue) {
    const nextVolume = clampVolume(nextValue);
    setVolume(nextVolume);

    const player = playerRef.current;
    if (!player) {
      saveRadioState({ volume: nextVolume });
      return;
    }

    try {
      if (typeof player.setVolume === 'function') {
        player.setVolume(nextVolume);
      }

      if (nextVolume > 0 && typeof player.isMuted === 'function' && player.isMuted()) {
        player.unMute();
        setMuted(false);
      }

      saveRadioState({ volume: nextVolume, muted: false });
    } catch {
      setRadioStatus('Volume control unavailable.');
    }
  }

  function handleSoftRefresh() {
    setTheme(readStoredTheme());
    applyPreviewState();
    saveRadioState();
  }

  function themeStyle() {
    return THEME_PALETTES[theme] ?? THEME_PALETTES.default;
  }

  const selectedThemeLabel =
    THEME_OPTIONS.find((option) => option.value === theme)?.label ?? 'Default AI_OS Dark';

  return (
    <section
      className="legacyPreserveSurface"
      aria-label="Preserved legacy dashboard modules"
      style={themeStyle()}
    >
      <div className="legacySurfaceHeader">
        <div>
          <p className="eyebrow">Legacy preservation lane</p>
          <h2>Utilities, Dock, and Music Player</h2>
          <p className="legacySurfaceSummary">
            Mounted from the older dashboard so the new deployment page can keep the same controls
            without deleting the source page yet.
          </p>
        </div>

        <div className="legacyStatusChips" aria-label="Preserved modules">
          <span className="statusPill status-good">Utilities</span>
          <span className="statusPill status-neutral">Dock</span>
          <span className="statusPill status-warn">Music Player</span>
        </div>
      </div>

      <div className="legacyModuleGrid">
        <LegacyModuleCard eyebrow="Utilities" title="Dashboard Utilities" statusClass="status-good">
          <div className="legacyUtilityBody">
            <label className="legacySelectField" htmlFor="dashboardThemeSelector">
              <span>Theme</span>
              <select
                id="dashboardThemeSelector"
                value={theme}
                onChange={(event) => setTheme(event.target.value)}
              >
                {THEME_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <button className="button button-readonly legacySoftRefreshButton" type="button" onClick={handleSoftRefresh}>
              Soft Refresh
            </button>

            <p className="legacyUtilityNote">
              Theme selection persists locally. Soft refresh reapplies the saved state without touching
              any backend or broker path.
            </p>
          </div>
        </LegacyModuleCard>

        <LegacyModuleCard eyebrow="Dock" title="Music Dock" statusClass="status-neutral">
          <div className="legacyDockTopline">
            <div>
              <p className="legacyDockEyebrow">Music Dock #1</p>
              <strong>{radioStatus}</strong>
            </div>

            <button
              className="button button-readonly legacyExpandButton"
              type="button"
              onClick={() => handleDockControl('expand')}
            >
              {dockCollapsed ? 'Expand Dock' : 'Minimize Dock'}
            </button>
          </div>

          <div className={`legacyDockControls ${dockCollapsed ? 'is-collapsed' : ''}`}>
            <ControlButton
              label="Previous"
              stateLabel="Track"
              title="Previous track"
              onClick={() => handleDockControl('back')}
            />
            <ControlButton
              active={isPlaying}
              label={isPlaying ? 'Pause' : 'Play'}
              stateLabel={radioStatus}
              title={isPlaying ? 'Pause Dock Player' : 'Play Dock Player'}
              onClick={() => handleDockControl('play')}
            />
            <ControlButton
              label="Next"
              stateLabel="Track"
              title="Next track"
              onClick={() => handleDockControl('next')}
            />
            <ControlButton
              active={muted}
              label={muted ? 'Unmute' : 'Mute'}
              stateLabel={muted ? 'Muted' : 'Audio'}
              title={muted ? 'Unmute Dock Player' : 'Mute Dock Player'}
              onClick={() => handleDockControl('mute')}
            />
          </div>

          <p className="legacyDockHint">
            The dock keeps the player mounted and only hides the expanded body when collapsed.
          </p>
        </LegacyModuleCard>

        <LegacyModuleCard eyebrow="Music Player" title="YouTube Player" statusClass="status-warn">
          <div className={`legacyPlayerPanel ${dockCollapsed ? 'is-collapsed' : ''}`}>
            <div className="legacyPlayerFrame" aria-label="Dock music player">
              <div ref={playerMountRef} className="legacyPlayerMount" />
            </div>

            <label className="legacyVolumeRow" aria-label="Dock player volume">
              <span>Volume</span>
              <input
                type="range"
                min="0"
                max="100"
                value={volume}
                onChange={(event) => handleVolumeChange(event.target.value)}
              />
              <strong>{volume}</strong>
            </label>

            <p className="legacyPlayerNote">{previewNote}</p>
            <p className="legacyPlayerMeta">
              Saved theme: {selectedThemeLabel}. Player state remains local-only and does not include
              credentials or account identifiers.
            </p>
          </div>
        </LegacyModuleCard>
      </div>
    </section>
  );
}
