from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class ValidatorRecord:
    validator_id: str
    name: str
    path: str
    command: str
    mode: str
    scope: str
    requires_network_boolean: bool = False
    requires_secrets_boolean: bool = False
    mutates_files_boolean: bool = False
    protected_paths_touched_boolean: bool = False
    status: str = "DISCOVERED"


@dataclass
class ValidatorInventory:
    validators: list[ValidatorRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"validators": [asdict(record) for record in self.validators]}


def discover_validators(repo_root: Path, tracked_files: list[str]) -> ValidatorInventory:
    records: list[ValidatorRecord] = []
    for file_name in tracked_files:
        lower = file_name.lower()
        if "validator" not in lower and "test-" not in lower and not lower.startswith("tests/"):
            continue
        path = repo_root / file_name
        if file_name.endswith(".ps1"):
            command = f"powershell -NoProfile -ExecutionPolicy Bypass -File {file_name}"
            mode = "POWERSHELL"
        elif file_name.endswith(".py"):
            command = f"python -m py_compile {file_name}" if not lower.startswith("tests/") else f"python -m pytest {file_name}"
            mode = "PYTHON"
        else:
            command = "read-only evidence"
            mode = "DOCUMENT"
        records.append(
            ValidatorRecord(
                validator_id=f"validator-{len(records) + 1:03d}",
                name=path.stem,
                path=file_name,
                command=command,
                mode=mode,
                scope="local",
            )
        )
        if len(records) >= 250:
            break
    return ValidatorInventory(records)
