"""Route only v1-approved local validators."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationResult:
    path: str
    validator: str
    success: bool
    message: str
    stdout_tail: str = ""
    stderr_tail: str = ""
    command: list[str] | None = None
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _tail(text: str, limit: int = 1200) -> str:
    return text[-limit:] if len(text) > limit else text


def select_validator(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".py":
        return "py_compile"
    if suffix == ".json":
        return "json_parse"
    if suffix == ".md":
        return "manual_review_markdown"
    if suffix == ".ps1":
        return "manual_review_powershell"
    return "unsupported_extension"


def run_validator(path: str | Path) -> ValidationResult:
    file_path = Path(path)
    validator = select_validator(file_path)

    if validator == "py_compile":
        command = [sys.executable, "-m", "py_compile", str(file_path)]
        result = subprocess.run(command, capture_output=True, text=True, shell=False, check=False)
        return ValidationResult(
            path=str(file_path),
            validator=validator,
            success=result.returncode == 0,
            message="Python compile passed." if result.returncode == 0 else "Python compile failed.",
            stdout_tail=_tail(result.stdout),
            stderr_tail=_tail(result.stderr),
            command=command,
            executable=False,
        )

    if validator == "json_parse":
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
            return ValidationResult(str(file_path), validator, True, "JSON parse passed.", executable=False)
        except (OSError, json.JSONDecodeError) as exc:
            return ValidationResult(str(file_path), validator, False, f"JSON parse failed: {exc}", executable=False)

    if validator == "manual_review_markdown":
        return ValidationResult(str(file_path), validator, True, "Markdown readback/manual review required.", executable=False)

    if validator == "manual_review_powershell":
        return ValidationResult(str(file_path), validator, True, "PowerShell manual review required; not executed in v1.", executable=False)

    return ValidationResult(str(file_path), validator, False, "No v1 validator is defined for this extension.", executable=False)
