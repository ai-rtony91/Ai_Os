# AIOS Self Build Next

## Purpose

`aios_self_build_next.py` selects the next campaign stage that is ready for
human-reviewed AI_OS self-build work and renders a JSON Codex packet preview.
It is a bridge from campaign registry state to packet-preview state.

## Command

```powershell
python automation/orchestration/aios_self_build_next.py
```

The command reads:

```text
automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json
```

It selects the highest-priority stage with:

- `status: READY`
- complete stage-level dependencies
- no stage blockers
- no campaign blockers

## Output

The command prints JSON to stdout. The output includes:

- selected campaign, phase, and stage metadata
- a `packet_preview` object with packet ID, mission, worker, lane, branch,
  worktree, allowed paths, forbidden paths, validators, stop point, and final
  report format
- safety booleans that all remain `false`

## Safety Boundary

This command does not write files, mutate the campaign registry, create work
packets, mutate approvals, mutate queues, launch workers, launch runtime, start
schedulers or daemons, touch broker/live-trading paths, commit, or push.

The packet preview is evidence for Anthony review only. It is not executable
approval and does not bypass AGENTS.md, validator chains, protected-action
gates, or Human Owner approval.
