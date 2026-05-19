# AI_OS Product Roadmap

Status: canonical summary extracted from legacy `docs/AI_OS`

## Purpose

This roadmap summarizes product and platform direction from legacy `docs/AI_OS` roadmap, dashboard, product, productization, orchestration, and trading-related planning docs. It does not claim these ideas are implemented.

## Current Direction

AI_OS is a local-first guided operating environment with human-controlled AI assistance.

Near-term product focus:

- clean repo structure,
- compact canonical docs,
- safe orchestration,
- dashboard visibility,
- paper-only Trading Lab,
- validation and governance before automation expansion.

## Dashboard Direction

The dashboard should become an operator control center, not a cluttered marketing surface.

Current direction:

- show system status,
- show validator state,
- show protected-file and blocked-action warnings,
- show work packets, approvals, and next safe action,
- keep controls read-only until separately approved,
- prefer fixture/local data before real adapters.

## Operator Control Center Direction

The operator flow should reduce copy/paste and confusion while preserving human approval.

Needed capabilities:

- goal intake,
- work packet generation,
- Codex prompt generation,
- approval inbox draft,
- validator recommendation,
- clean-state reminder,
- next safe command.

## Worker Orchestration Direction

Worker orchestration should converge on one controlled system:

- packets,
- worker registry,
- approvals,
- validators,
- commit packages,
- clean-state gates,
- operator status.

It should not become multiple independent brains.

## Documentation Cleanup Direction

`docs/AI_OS` should be reduced from a 770-file legacy planning swarm into compact canonical docs under:

- `docs/architecture`,
- `docs/workflows`,
- `docs/governance`,
- `docs/infrastructure`,
- `docs/security`,
- `docs/roadmap`,
- `docs/concepts`,
- `docs/audits`.

Legacy docs should be archived only after useful doctrine is extracted.

## Trading Lab Direction

Trading Lab is a paper-only proving ground.

Allowed direction:

- strategy planning,
- backtesting,
- paper signal review,
- latency tracking,
- risk controls,
- evidence and reporting.

Blocked direction:

- broker login,
- OANDA/live API execution,
- real webhooks,
- real orders,
- LLMs in live order execution paths.

## Near-Term Next Steps

1. Human review of these canonical summaries.
2. Pass 12 folder-based archive of clearly generated docs.
3. Separate review for dashboard, dispatcher, and orchestration docs.
4. Promote security and governance docs into canonical locations.
5. Continue orchestration cleanup for v1 examples and direct display dependencies.

## Human-Review Items

- Whether dashboard docs describe current implementation or future product direction.
- Whether productization should stay roadmap-only.
- Which Trading Lab docs belong under active product roadmap versus archive.
- How soon to introduce automation beyond documentation and operator runners.
