from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestration.dashboard.aios_dashboard_state_report import render_dashboard_state_report


MODE = "GATED_MARKDOWN_REPORT_OUTPUT"
APPROVED_ROOT_PARTS = ("reports", "dashboard_state")
DEFAULT_ROOT = Path("Reports") / "dashboard_state"
DEFAULT_FILENAME_PREFIX = "dashboard_state_report_"
MARKDOWN_SUFFIX = ".md"
MAX_FILENAME_LENGTH = 160


def write_dashboard_state_report(
    projected_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
    output_root: str | Path | None = None,
    filename: str | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    effective_now = now_utc or _utc_now_text()
    flags = _safety_flags(overwrite=overwrite is True)

    if not isinstance(overwrite, bool):
        return _metadata("BLOCKED", reason="invalid_overwrite", safety_flags=flags)

    root, root_reason = _resolve_output_root(output_root)
    if root_reason:
        return _metadata("BLOCKED", reason=root_reason, safety_flags=flags)
    flags["approved_output_root"] = True

    safe_filename, filename_reason = _resolve_filename(filename, effective_now)
    if filename_reason:
        return _metadata("BLOCKED", reason=filename_reason, safety_flags=flags)
    flags["safe_filename"] = True

    target = (root / safe_filename).resolve()
    if not _is_path_confined(root, target):
        return _metadata("BLOCKED", reason="path_escape", safety_flags=flags)
    flags["path_confined"] = True

    content = render_dashboard_state_report(
        projected_state=projected_state,
        evidence=evidence,
        now_utc=effective_now,
    )
    if not isinstance(content, str) or not content.strip():
        return _metadata("BLOCKED", output_path=str(target), reason="empty_content", safety_flags=flags)
    flags["non_empty_markdown"] = True

    if target.exists() and not overwrite:
        return _metadata("BLOCKED", output_path=str(target), reason="target_exists", safety_flags=flags)

    root.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    bytes_written = len(content.encode("utf-8"))

    return _metadata(
        "WROTE",
        output_path=str(target),
        bytes_written=bytes_written,
        reason="written",
        safety_flags=flags,
    )


def _resolve_output_root(output_root: str | Path | None) -> tuple[Path, str]:
    try:
        raw_root = DEFAULT_ROOT if output_root is None else Path(output_root)
        if not raw_root.is_absolute():
            raw_root = _repo_root() / raw_root
        root = raw_root.resolve()
    except (OSError, RuntimeError, TypeError, ValueError):
        return Path(), "invalid_output_root"

    if not _is_approved_root(root):
        return root, "unapproved_output_root"
    return root, ""


def _resolve_filename(filename: str | None, now_utc: str) -> tuple[str, str]:
    if filename is None:
        timestamp, reason = _timestamp_for_filename(now_utc)
        if reason:
            return "", reason
        filename = f"{DEFAULT_FILENAME_PREFIX}{timestamp}{MARKDOWN_SUFFIX}"

    if not isinstance(filename, str) or not _is_safe_filename(filename):
        return "", "unsafe_filename"
    return filename, ""


def _is_approved_root(root: Path) -> bool:
    parts = tuple(part.lower() for part in root.parts)
    return len(parts) >= 2 and parts[-2:] == APPROVED_ROOT_PARTS


def _is_safe_filename(filename: str) -> bool:
    if len(filename) > MAX_FILENAME_LENGTH:
        return False
    if filename != Path(filename).name:
        return False
    if Path(filename).is_absolute():
        return False
    if not filename.endswith(MARKDOWN_SUFFIX):
        return False
    if filename.startswith("."):
        return False
    return all(char.isalnum() or char in "._-" for char in filename)


def _is_path_confined(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return target.parent == root


def _timestamp_for_filename(now_utc: str) -> tuple[str, str]:
    text = str(now_utc).strip()
    if not text:
        return "", "invalid_now_utc"
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return "", "invalid_now_utc"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    return parsed.strftime("%Y%m%d_%H%M%SZ"), ""


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _safety_flags(*, overwrite: bool) -> dict[str, bool]:
    return {
        "approved_output_root": False,
        "safe_filename": False,
        "path_confined": False,
        "non_empty_markdown": False,
        "overwrite": overwrite,
        "markdown_only": True,
        "control_authority": False,
        "execution_allowed": False,
        "mutation_allowed": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
    }


def _metadata(
    status: str,
    *,
    output_path: str = "",
    bytes_written: int = 0,
    reason: str,
    safety_flags: Mapping[str, bool],
) -> dict[str, Any]:
    return {
        "status": status,
        "output_path": output_path,
        "bytes_written": bytes_written,
        "mode": MODE,
        "safety_flags": dict(safety_flags),
        "reason": reason,
    }


__all__ = ["write_dashboard_state_report"]
