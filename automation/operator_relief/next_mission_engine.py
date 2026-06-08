"""Next mission candidate engine for Operator Relief."""

from __future__ import annotations

from pathlib import Path

from .packet_queue import PacketQueueReport, default_packet_candidates, write_packet_queue


def generate_next_mission_queue(repo_root: Path, max_candidates: int = 10) -> PacketQueueReport:
    if max_candidates < 5:
        candidates = default_packet_candidates()[:max_candidates]
    else:
        candidates = default_packet_candidates()[: min(max_candidates, 10)]
    return write_packet_queue(repo_root, candidates=candidates)
