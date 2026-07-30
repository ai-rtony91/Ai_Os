"""Validate a schema-only terminal grid profile and produce a pixel layout plan.

This module is deliberately a planner, not a launcher.  It never starts a
process, moves a window, persists configuration, or evaluates pane commands.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, NoReturn


SCHEMA = "AIOS_TERMINAL_LAYOUT_PLAN.v1"
REQUIRED_BLOCKED_ACTIONS = {
    "live_trading",
    "broker_connection",
    "oanda_connection",
    "startup_persistence",
    "scheduled_task_creation",
}
TRADING_SAFETY_FIELDS = {
    "live_trading_enabled",
    "broker_connection_enabled",
    "oanda_enabled",
    "api_keys_allowed",
    "secrets_allowed",
    "real_orders_allowed",
}


class ProfileValidationError(ValueError):
    """Raised when a terminal grid profile is unsafe or malformed."""


def _fail(message: str) -> NoReturn:
    raise ProfileValidationError(message)


def _object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{field} must be an object")
    return value


def _array(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(f"{field} must be an array")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{field} must be a non-empty string")
    return value


def _positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _fail(f"{field} must be a positive integer")
    return value


def _required(mapping: dict[str, Any], field: str, parent: str = "profile") -> Any:
    if field not in mapping:
        _fail(f"{parent}.{field} is required")
    return mapping[field]


def _track_edges(length: int, count: int) -> list[int]:
    """Return gap-free integer track boundaries for a dimension."""
    return [(index * length) // count for index in range(count + 1)]


def build_terminal_layout_plan(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate *profile* and return a deterministic, non-executable plan."""
    if not isinstance(profile, dict):
        _fail("profile must be an object")

    profile_id = _text(_required(profile, "profile_id"), "profile.profile_id")
    profile_name = _text(_required(profile, "profile_name"), "profile.profile_name")
    _text(_required(profile, "schema_version"), "profile.schema_version")
    _text(_required(profile, "profile_type"), "profile.profile_type")

    if _required(profile, "mode") != "schema_only":
        _fail("profile.mode must be 'schema_only'")
    for field, expected in (
        ("local_only", True),
        ("startup_persistence", False),
        ("scheduled_tasks", False),
    ):
        if _required(profile, field) is not expected:
            _fail(f"profile.{field} must be {str(expected).lower()}")

    safety = _object(_required(profile, "trading_safety"), "profile.trading_safety")
    for field in sorted(TRADING_SAFETY_FIELDS):
        if _required(safety, field, "profile.trading_safety") is not False:
            _fail(f"profile.trading_safety.{field} must be false")

    display = _object(_required(profile, "display"), "profile.display")
    width = _positive_integer(
        _required(display, "target_width_px", "profile.display"),
        "profile.display.target_width_px",
    )
    height = _positive_integer(
        _required(display, "target_height_px", "profile.display"),
        "profile.display.target_height_px",
    )
    _text(_required(display, "display_label", "profile.display"), "profile.display.display_label")
    _text(_required(display, "scaling_note", "profile.display"), "profile.display.scaling_note")

    grid = _object(_required(profile, "grid"), "profile.grid")
    columns = _positive_integer(
        _required(grid, "columns", "profile.grid"), "profile.grid.columns"
    )
    rows = _positive_integer(_required(grid, "rows", "profile.grid"), "profile.grid.rows")
    _text(_required(grid, "layout_strategy", "profile.grid"), "profile.grid.layout_strategy")
    _array(_required(grid, "reserved_zones", "profile.grid"), "profile.grid.reserved_zones")

    panes = _array(_required(profile, "panes"), "profile.panes")
    if not panes:
        _fail("profile.panes must contain at least one pane")

    x_edges = _track_edges(width, columns)
    y_edges = _track_edges(height, rows)
    occupied: set[tuple[int, int]] = set()
    pane_ids: set[str] = set()
    planned_panes: list[dict[str, Any]] = []

    for index, raw_pane in enumerate(panes):
        prefix = f"profile.panes[{index}]"
        pane = _object(raw_pane, prefix)
        pane_id = _text(_required(pane, "pane_id", prefix), f"{prefix}.pane_id")
        if pane_id in pane_ids:
            _fail(f"{prefix}.pane_id duplicates '{pane_id}'")
        pane_ids.add(pane_id)

        title = _text(_required(pane, "title", prefix), f"{prefix}.title")
        role = _text(_required(pane, "role", prefix), f"{prefix}.role")
        working_directory = _text(
            _required(pane, "working_directory", prefix), f"{prefix}.working_directory"
        )
        if _required(pane, "startup_command", prefix) is not None:
            _fail(f"{prefix}.startup_command must be null")
        _array(_required(pane, "allowed_actions", prefix), f"{prefix}.allowed_actions")
        blocked = _array(_required(pane, "blocked_actions", prefix), f"{prefix}.blocked_actions")
        if not all(isinstance(action, str) for action in blocked):
            _fail(f"{prefix}.blocked_actions must contain only strings")
        missing_blocks = REQUIRED_BLOCKED_ACTIONS.difference(blocked)
        if missing_blocks:
            _fail(f"{prefix}.blocked_actions is missing: {', '.join(sorted(missing_blocks))}")
        _array(_required(pane, "notes", prefix), f"{prefix}.notes")

        position = _object(_required(pane, "grid_position", prefix), f"{prefix}.grid_position")
        column = _positive_integer(
            _required(position, "column", f"{prefix}.grid_position"),
            f"{prefix}.grid_position.column",
        )
        row = _positive_integer(
            _required(position, "row", f"{prefix}.grid_position"),
            f"{prefix}.grid_position.row",
        )
        column_span = _positive_integer(
            _required(position, "column_span", f"{prefix}.grid_position"),
            f"{prefix}.grid_position.column_span",
        )
        row_span = _positive_integer(
            _required(position, "row_span", f"{prefix}.grid_position"),
            f"{prefix}.grid_position.row_span",
        )
        last_column = column + column_span - 1
        last_row = row + row_span - 1
        if last_column > columns or last_row > rows:
            _fail(f"{prefix}.grid_position is outside the declared grid")

        cells = {
            (cell_column, cell_row)
            for cell_column in range(column, last_column + 1)
            for cell_row in range(row, last_row + 1)
        }
        if cells & occupied:
            _fail(f"{prefix}.grid_position overlaps another pane")
        occupied.update(cells)

        left = x_edges[column - 1]
        top = y_edges[row - 1]
        right = x_edges[last_column]
        bottom = y_edges[last_row]
        planned_panes.append(
            {
                "pane_id": pane_id,
                "title": title,
                "role": role,
                "working_directory": working_directory,
                "grid_position": {
                    "column": column,
                    "row": row,
                    "column_span": column_span,
                    "row_span": row_span,
                },
                "bounds_px": {
                    "x": left,
                    "y": top,
                    "width": right - left,
                    "height": bottom - top,
                },
            }
        )

    _object(_required(profile, "validation"), "profile.validation")
    _array(_required(profile, "notes"), "profile.notes")

    return {
        "schema": SCHEMA,
        "status": "PLANNED_NOT_LAUNCHED",
        "profile_id": profile_id,
        "profile_name": profile_name,
        "display": {"width_px": width, "height_px": height},
        "grid": {"columns": columns, "rows": rows},
        "panes": planned_panes,
        "safety": {
            "executable_commands_included": False,
            "windows_launched": False,
            "startup_persistence_changed": False,
            "scheduled_tasks_changed": False,
            "broker_or_live_trading_enabled": False,
        },
    }


def load_and_plan(profile_path: Path) -> dict[str, Any]:
    """Load a JSON profile from disk and build its layout plan."""
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileValidationError(f"cannot read profile: {exc}") from exc
    return build_terminal_layout_plan(profile)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an AI_OS terminal grid profile and print a non-executable pixel plan."
    )
    parser.add_argument("profile", type=Path, help="path to a terminal grid profile JSON file")
    args = parser.parse_args(argv)
    try:
        plan = load_and_plan(args.profile)
    except ProfileValidationError as exc:
        parser.exit(2, f"BLOCKED: {exc}\n")
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
