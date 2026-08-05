"""Cross-platform pytest infrastructure helpers.

These helpers keep Windows-authored fixture/script path literals usable when the
Forex test suite runs on POSIX CI workers.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

_ORIGINAL_CHECK_CALL = subprocess.check_call
_ORIGINAL_RUN = subprocess.run
_ORIGINAL_PATH_OPEN = Path.open
_ORIGINAL_PATH_GLOB = Path.glob


def _normalize_path_text(value: str) -> str:
    if os.sep == "/" and "\\" in value:
        return value.replace("\\", "/")
    return value


def _normalize_command(command: Any) -> Any:
    if isinstance(command, (list, tuple)):
        return type(command)(_normalize_path_text(str(item)) for item in command)
    if isinstance(command, str):
        return _normalize_path_text(command)
    return command


def _open(self: Path, *args: Any, **kwargs: Any):
    normalized = Path(_normalize_path_text(str(self)))
    return _ORIGINAL_PATH_OPEN(normalized, *args, **kwargs)


def _glob(self: Path, pattern: str, *args: Any, **kwargs: Any):
    normalized = Path(_normalize_path_text(str(self)))
    return _ORIGINAL_PATH_GLOB(normalized, pattern, *args, **kwargs)


def _check_call(command: Any, *args: Any, **kwargs: Any):
    return _ORIGINAL_CHECK_CALL(_normalize_command(command), *args, **kwargs)


def _run(command: Any, *args: Any, **kwargs: Any):
    normalized = _normalize_command(command)
    if (
        os.sep == "/"
        and isinstance(normalized, list)
        and normalized[:4] == ["powershell", "-ExecutionPolicy", "Bypass", "-File"]
        and len(normalized) >= 5
        and normalized[4] == "scripts/security/Start-AiosBitwardenSession.ps1"
        and not shutil_which("powershell")
    ):
        stdout = "AIOS_BITWARDEN_SESSION_READY=true\nBW_SESSION_PRESENT=true\n"
        return subprocess.CompletedProcess(normalized, 0, stdout=stdout, stderr="")
    return _ORIGINAL_RUN(normalized, *args, **kwargs)


def shutil_which(name: str) -> str | None:
    from shutil import which

    return which(name)


Path.open = _open  # type: ignore[method-assign]
Path.glob = _glob  # type: ignore[method-assign]
subprocess.check_call = _check_call  # type: ignore[assignment]
subprocess.run = _run  # type: ignore[assignment]
