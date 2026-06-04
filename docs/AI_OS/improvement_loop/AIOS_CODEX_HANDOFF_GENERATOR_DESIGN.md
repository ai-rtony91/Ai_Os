# AI_OS Codex Handoff Generator Design

Purpose:
Define how ranked AI_OS improvements become Codex-ready draft packets.

## Inputs

- ranked improvement recommendation
- supporting traces
- human feedback
- model feedback
- eval case
- trusted/proven profitability priority evidence when the improvement affects Trading Lab decisions
- allowed paths
- forbidden paths
- validation chain
- stop point

## Output

The generator produces a draft packet with:

- `CODEX-ONLY PROMPT`
- execution token placeholder set to `DRAFT_ONLY_DO_NOT_EXECUTE`
- title
- lane
- worktree
- branch
- mission
- precheck
- allowed paths
- forbidden paths
- hard blocks
- validation chain
- stop point
- final report format

## Authority Boundary

Generated handoffs are drafts only. They do not authorize execution, APPLY, commit, push, merge, rebase, force push, API use, package install, runtime writes, Night Supervisor edits, broker edits, OANDA edits, or live trading.

## Reuse of Existing AI_OS Handoff Tooling

Existing handoff tooling under `automation/orchestration/handoff/` remains a nearby pattern. Phase 18 does not replace it. Phase 18 defines evidence-ranked improvement handoffs that may later integrate with the existing handoff generator through a separately approved APPLY packet.
