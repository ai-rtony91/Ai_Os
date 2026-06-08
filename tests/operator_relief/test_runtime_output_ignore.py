from __future__ import annotations

from pathlib import Path


def test_operator_relief_runtime_outputs_are_ignored() -> None:
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "reports/operator_relief/" in gitignore
    assert "Reports/operator_relief/" in gitignore


def test_operator_relief_source_and_tests_are_not_ignored() -> None:
    gitignore_lines = [
        line.strip()
        for line in Path(".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    assert "automation/operator_relief/" not in gitignore_lines
    assert "tests/operator_relief/" not in gitignore_lines
