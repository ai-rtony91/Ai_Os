# AI_OS Orchestration Ownership Doctrine

Purpose:
Define ownership rules for AI_OS Manager, specialist agents, tools, and handoffs.

## Default Owner

AI_OS Manager stays in control by default.

The Manager owns:

- final answer
- packet safety
- validator chain
- approval gate
- profitability priority
- next safe action
- stop point
- path boundary
- branch and worktree awareness

## Specialist Boundary

Specialists are usually tools. A specialist receives bounded context, performs a bounded task, returns structured output, and does not own the next response or branch unless a handoff is explicitly justified.

## Handoff Boundary

Use handoff only when the specialist must own the next response or branch. Handoff requires:

- explicit reason
- owner identity
- lane
- branch
- worktree
- allowed paths
- forbidden paths
- validator chain
- approval rule
- stop point

## Profitability Priority

Trusted, proven profitability outranks feature expansion. Orchestration must not create more agents, UI lanes, voice lanes, or automation paths unless they improve evidence quality, safety, or operator throughput.

