# AI_OS Harness Definition

Purpose:
Define the AI_OS harness that the improvement loop can evaluate and propose changes against.

## Harness Components

- `AGENTS.md`
- tokenized Codex packet format
- worker routing rules
- validator chain
- approval rules
- output contract
- stop points
- allowed and forbidden paths
- clean-state rules
- branch and worktree verification
- protected main PR lane
- commit, push, and merge gates

## Harness Responsibilities

The harness must keep work bounded, observable, and reversible. It must prove:

- the packet has an authorized execution token
- the lane is named
- the branch and worktree are verified
- allowed paths are explicit
- forbidden paths are explicit
- validators are attached
- stop point is explicit
- protected actions require current-session human approval
- final reports include changed files, validation, git status, commit status, and push status

## Improvement Boundary

The improvement loop may propose harness changes, but it must not apply them automatically. A harness update requires:

1. trace evidence
2. ranked recommendation
3. draft Codex handoff
4. human-approved APPLY packet
5. validation
6. separate commit approval
7. protected main PR lane
