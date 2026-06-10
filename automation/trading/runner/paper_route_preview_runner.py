"""Paper route preview runner for signal fixtures."""

from __future__ import annotations

from typing import Any

from aios.modules.trader.routes.paper_route_preview import build_paper_route_preview


def run_paper_route_previews(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_paper_route_preview(payload) for payload in payloads]

