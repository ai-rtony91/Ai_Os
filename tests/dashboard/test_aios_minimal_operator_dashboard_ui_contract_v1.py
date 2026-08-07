from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "apps/dashboard/src/MinimalOperatorDashboard.jsx"
STYLES = ROOT / "apps/dashboard/src/MinimalOperatorDashboard.css"


def test_home_keeps_exactly_four_ordered_rooms() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    rooms = [("🔐", "Access"), ("📈", "Forex Bot"), ("🛠️", "Utilities"), ("🎵", "Music")]

    positions = [source.index(f"label: '{label}'") for _, label in rooms]
    assert positions == sorted(positions)
    assert source.count("id: '") == 4
    for icon, label in rooms:
        assert f"icon: '{icon}'" in source
        assert f"label: '{label}'" in source


def test_navigation_is_local_accessible_and_restores_focus() -> None:
    source = COMPONENT.read_text(encoding="utf-8")

    assert "useState('home')" in source
    assert "event.key === 'Escape'" in source
    assert "lastRoomButtonRef.current = document.activeElement" in source
    assert "lastRoomButtonRef.current?.focus()" in source
    assert "backButtonRef.current?.focus()" in source
    assert 'aria-label="Back to AIOS home"' in source


def test_rendering_supports_safe_areas_dynamic_viewports_and_reduced_motion() -> None:
    styles = STYLES.read_text(encoding="utf-8")

    assert "env(safe-area-inset-top)" in styles
    assert "min-height: 100dvh" in styles
    assert "overflow-x: hidden" in styles
    assert "touch-action: manipulation" in styles
    assert "prefers-reduced-motion: reduce" in styles
    assert ":focus-visible" in styles
    assert ":active" in styles


def test_forex_room_stays_display_only_and_execution_locked() -> None:
    source = COMPONENT.read_text(encoding="utf-8")

    for safety_label in ("READ ONLY", "DISPLAY_ONLY", "EXEC OFF", "BROKER LOCKED", "Paper-only"):
        assert safety_label in source
    for forbidden_call in ("fetch(", "setTimeout(", "setInterval(", "WebSocket("):
        assert forbidden_call not in source
    for forbidden_control in (">BUY<", ">SELL<", "placeOrder", "submitOrder"):
        assert forbidden_control not in source
