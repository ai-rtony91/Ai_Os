"""Preview-only CLI for ChatGptToOrchestrationAdapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .classifier import classify_packet
from .envelope import build_envelope
from .models import RepoState
from .parser import parse_packet
from .validator import validate_packet


def run_preview(raw_text: str, repo_state: RepoState) -> dict:
    parsed = parse_packet(raw_text)
    validation = validate_packet(parsed, repo_state)
    classification = classify_packet(parsed, validation)
    return build_envelope(parsed, validation, classification, repo_state)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preview ChatGPT packet to AI_OS orchestration envelope.")
    parser.add_argument("--input-packet", help="Path to packet text. Reads stdin when omitted.")
    parser.add_argument("--repo-root", default="C:\\Dev\\Ai.Os")
    parser.add_argument("--branch", default="UNKNOWN")
    parser.add_argument("--worktree", default="C:\\Dev\\Ai.Os")
    parser.add_argument("--git-status-short-branch", default="UNKNOWN")
    parser.add_argument("--dirty-state-class", default="UNKNOWN")
    parser.add_argument("--output-json", help="Optional approved output path for preview JSON.")
    args = parser.parse_args(argv)

    raw_text = Path(args.input_packet).read_text(encoding="utf-8") if args.input_packet else sys.stdin.read()
    repo_state = RepoState(
        repo_root=args.repo_root,
        branch=args.branch,
        worktree=args.worktree,
        git_status_short_branch=args.git_status_short_branch,
        dirty_state_class=args.dirty_state_class,
    )
    result = run_preview(raw_text, repo_state)
    output = json.dumps(result, indent=2, sort_keys=True)

    if args.output_json:
        Path(args.output_json).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
