# AIOS Self Build Next

## Purpose

`aios_self_build_next.py` selects the next campaign stage that is ready for
human-reviewed AI_OS self-build work and renders a JSON Codex packet preview.
It is a bridge from campaign registry state to packet-preview state.

## Command

```powershell
python automation/orchestration/aios_self_build_next.py
```

To save the selected packet preview:

```powershell
python automation/orchestration/aios_self_build_next.py --write-packet
```

The default packet-preview output directory is:

```text
automation/orchestration/work_packets/preview
```

Use `--output-dir` to write to another guarded preview directory:

```powershell
python automation/orchestration/aios_self_build_next.py --write-packet --output-dir .tmp_aios_packet_preview
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
- `written_packet_path` when `--write-packet` is used, otherwise `null`
- safety booleans that all remain `false`

The written packet text begins with:

```text
CODEX-ONLY PROMPT
```

It includes `AI_OS EXECUTION TOKEN`, `AI_OS BOOTSTRAP REQUIRED`, packet ID,
mission, worker, lane, branch, worktree, allowed paths, forbidden paths,
validators, stop point, and final report format.

## Safety Boundary

This command does not write files, mutate the campaign registry, create work
packets, mutate approvals, mutate queues, launch workers, launch runtime, start
schedulers or daemons, touch broker/live-trading paths, commit, or push.

The only optional write behavior is `--write-packet`, which writes a packet
preview `.txt` file to a guarded preview directory. The output guard blocks
`Reports/`, `control/review_bridge/`, active/complete/blocked packet-state
folders, queue paths, approval paths, and worker paths.

The packet preview is evidence for Anthony review only. It is not executable
approval and does not bypass AGENTS.md, validator chains, protected-action
gates, or Human Owner approval.
