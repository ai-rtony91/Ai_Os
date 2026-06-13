"""Tests for .\aios.ps1 -Mode relay and relay operator state aggregation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
AIOS = REPO_ROOT / "aios.ps1"
RELAY_STATE_SCRIPT = REPO_ROOT / "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"


def _run_script_json(script: Path, args: list[str], cwd: Path) -> dict:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-OutputJson",
        *args,
    ]
    raw = subprocess.check_output(cmd, cwd=str(cwd), text=True)
    return json.loads(raw.strip())


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _init_relay_dirs(root: Path) -> Path:
    base = root / "control" / "review_bridge"
    (base / "codex_reports").mkdir(parents=True, exist_ok=True)
    (base / "chatgpt_prompts").mkdir(parents=True, exist_ok=True)
    (base / "pasteback").mkdir(parents=True, exist_ok=True)
    (base / "archive").mkdir(parents=True, exist_ok=True)
    return base


def test_relay_state_reports_empty() -> None:
    with TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        _init_relay_dirs(tmp_root)

        out = _run_script_json(RELAY_STATE_SCRIPT, [], tmp_root)

        assert out["relay_status"] == "EMPTY"
        assert out["needs_codex_report"] is True
        assert out["needs_chatgpt_prompt"] is False
        assert out["needs_chatgpt_review"] is False
        assert out["needs_pasteback"] is False
        assert out["exact_next_action"].startswith("Store a Codex report")
        assert "AIOS_CODEX_CHATGPT_POWERSHELL_RELAY_V1.md" in out["related_existing_notes"][0]


def test_relay_state_needs_chatgpt_prompt_after_report() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        relay_root = _init_relay_dirs(root)

        _write_json(
            relay_root / "codex_reports" / "report.json",
            {
                "packet_id": "AIOS-RELAY-STATE-01",
                "branch": "feature/relay-test",
            },
        )

        out = _run_script_json(RELAY_STATE_SCRIPT, [], root)
        assert out["relay_status"] == "NEEDS_CHATGPT_PROMPT"
        assert out["needs_codex_report"] is False
        assert out["needs_chatgpt_prompt"] is True
        assert out["needs_chatgpt_review"] is False
        assert out["needs_pasteback"] is True


def test_relay_state_needs_chatgpt_review_after_prompt() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        relay_root = _init_relay_dirs(root)

        _write_json(relay_root / "codex_reports" / "report.json", {"packet_id": "AIOS-RELAY-STATE-02", "branch": "feature/relay-test"})
        (relay_root / "chatgpt_prompts" / "prompt.txt").write_text("prompt", encoding="utf-8")

        out = _run_script_json(RELAY_STATE_SCRIPT, [], root)
        assert out["relay_status"] == "NEEDS_CHATGPT_REVIEW"
        assert out["needs_chatgpt_review"] is True
        assert out["needs_pasteback"] is True


def test_relay_state_readies_when_pasteback_passes() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        relay_root = _init_relay_dirs(root)

        _write_json(relay_root / "codex_reports" / "report.json", {"packet_id": "AIOS-RELAY-STATE-03", "branch": "feature/relay-test"})
        (relay_root / "chatgpt_prompts" / "prompt.txt").write_text("prompt", encoding="utf-8")
        _write_json(relay_root / "pasteback" / "pasteback.json", {
            "packet_id": "AIOS-RELAY-STATE-03",
            "safety_scan_passed": True,
        })

        out = _run_script_json(RELAY_STATE_SCRIPT, [], root)
        assert out["relay_status"] == "PASTEBACK_READY"
        assert out["pasteback_ready"] is True
        assert out["pasteback_safety_status"] == "PASSED"
        assert out["needs_pasteback"] is False


def test_relay_state_flags_review_required_when_pasteback_fails() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        relay_root = _init_relay_dirs(root)

        _write_json(relay_root / "codex_reports" / "report.json", {"packet_id": "AIOS-RELAY-STATE-04", "branch": "feature/relay-test"})
        (relay_root / "chatgpt_prompts" / "prompt.txt").write_text("prompt", encoding="utf-8")
        _write_json(relay_root / "pasteback" / "pasteback.json", {
            "packet_id": "AIOS-RELAY-STATE-04",
            "safety_scan_passed": False,
        })

        out = _run_script_json(RELAY_STATE_SCRIPT, [], root)
        assert out["relay_status"] == "PASTEBACK_REVIEW_REQUIRED"
        assert out["pasteback_ready"] is False
        assert out["pasteback_safety_status"] == "FAILED"


def test_aios_mode_relay_aggregates_and_exposes_next_action() -> None:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(AIOS),
        "-Mode",
        "relay",
    ]
    output = subprocess.check_output(cmd, cwd=str(REPO_ROOT), text=True)
    relay_start = output.find("{")
    relay_end = output.rfind("}")
    assert relay_start >= 0 and relay_end > relay_start
    relay_state = json.loads(output[relay_start : relay_end + 1])
    assert relay_state["schema"] == "AIOS_RELAY_OPERATOR_STATE.v1"
    assert "exact_next_action" in relay_state
    assert "Relay operator state helper is unavailable" not in output


def test_aios_mode_relay_read_only() -> None:
    text = AIOS.read_text(encoding="utf-8")
    assert "\"relay\" {" in text
    start = text.index('"relay" {')
    end = text.index('"packet" {')
    relay_block = text[start:end]

    for forbidden in (
        "git push",
        "git commit",
        "git merge",
        "gh pr merge",
        "gh pr create",
        "daemon",
        "runtime/",
    ):
        assert forbidden not in relay_block
