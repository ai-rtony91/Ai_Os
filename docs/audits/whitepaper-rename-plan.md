# Whitepaper Rename Plan

## Purpose

Plan the coordinated rename of the current architecture whitepaper file without changing runtime behavior, launcher behavior, workflows, or protected governance semantics.

This is a planning document only. It does not rename, delete, move, or rewrite any existing whitepaper file.

## Current state

The active protected whitepaper chain is:

- `WHITEPAPER.md` — protected root pointer
- `docs/architecture/AI_OS_V2_WHITEPAPER.md` — current canonical whitepaper candidate
- `README.md` — contains a validation command that references `docs/architecture/AI_OS_V2_WHITEPAPER.md`

The whitepaper H1 has already been cleaned to:

- `# AI_OS Whitepaper`

The filename still contains `AI_OS_V2`.

## Rename target

Proposed target path:

- from: `docs/architecture/AI_OS_V2_WHITEPAPER.md`
- to: `docs/architecture/AI_OS_WHITEPAPER.md`

## Required coordinated changes

A safe rename PR must include all of the following in one branch:

1. Create or rename `docs/architecture/AI_OS_WHITEPAPER.md` with the exact current whitepaper content.
2. Remove `docs/architecture/AI_OS_V2_WHITEPAPER.md` only after the new path exists.
3. Update `WHITEPAPER.md` so its protected pointer references `docs/architecture/AI_OS_WHITEPAPER.md`.
4. Update `README.md` validation command so it references `docs/architecture/AI_OS_WHITEPAPER.md`.
5. Search for remaining live references to `docs/architecture/AI_OS_V2_WHITEPAPER.md`.
6. Leave historical audit references alone unless they are active authority or active validation instructions.

## Do not change in this rename PR

- Do not rewrite whitepaper body language.
- Do not remove historical `AI_OS_V2` context from audit files.
- Do not rename roadmap files.
- Do not touch runtime code.
- Do not touch launcher scripts.
- Do not change Trading Lab behavior.
- Do not change approval, telemetry, or reporting behavior.
- Do not merge or recreate PR #222.

## Risk assessment

Risk level: medium.

Reason:

- The actual content rename is simple.
- The risk is pointer drift if `WHITEPAPER.md` or `README.md` is missed.
- The risk is also duplicate-brain drift if both old and new whitepaper files remain active.

## Validation checklist

Before merge, confirm:

- `WHITEPAPER.md` points to `docs/architecture/AI_OS_WHITEPAPER.md`.
- `README.md` validation command points to `docs/architecture/AI_OS_WHITEPAPER.md`.
- `docs/architecture/AI_OS_WHITEPAPER.md` exists.
- `docs/architecture/AI_OS_V2_WHITEPAPER.md` does not exist in the branch.
- Search for `docs/architecture/AI_OS_V2_WHITEPAPER.md` returns only historical/audit references or no live authority references.
- `git diff --check` passes locally.

## Proposed branch

`rename/whitepaper-path`

## Proposed commit message

`rename(whitepaper): remove V2 from architecture whitepaper path`

## Stop point

Stop after creating the rename PR. Do not merge until the pointer diff is reviewed.
