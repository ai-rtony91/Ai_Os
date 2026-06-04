# AI_OS Trace Feedback Eval Flow

Purpose:
Define how AI_OS turns execution traces and feedback into reusable evals.

## Trace Sources

AI_OS trace events may include:

- Codex worked-for duration
- packet ID
- branch
- worktree
- files touched
- validation pass/fail
- user feedback
- assistant correction events
- path mismatch events
- merge or PR result
- safety flags

## Feedback Sources

Human feedback:

- Anthony's corrections
- approval or rejection
- frustration markers
- wrong-path reports
- conflicting-instruction reports
- too-sloppy events

Model feedback:

- LLM-as-judge feedback
- guardrail review
- packet truth eval
- hallucination check
- safety check
- path compliance check
- validator completeness check

## Eval Conversion

Repeated trace or feedback patterns become eval cases through eval case generation when they are:

- safety relevant
- recurring
- expensive for the operator
- likely to cause wrong repo work
- likely to cause false validation claims
- likely to weaken approval gates
- likely to reduce trusted/proven profitability evidence quality

## Required Result

Each eval case must include:

- input condition
- expected assistant behavior
- blocked assistant behavior
- source-of-truth rule
- validator command or checklist
- pass/fail criteria
- recommended harness improvement
