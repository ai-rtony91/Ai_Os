# AI_OS Agent Improvement Loop Method

Purpose:
Define the AI_OS self-improvement flywheel for turning real worker evidence into safer packets, stronger validators, and clearer handoffs.

This method is inspired by agent improvement loop patterns, but it is translated into AI_OS architecture. It does not copy any external notebook, call OpenAI, install packages, create live tracing, or grant runtime autonomy.

## Loop

Trace capture -> feedback -> eval generation -> validation gate -> improvement ranking -> Codex handoff -> harness update.

## Stage Details

1. Trace capture
   Capture evidence from Codex runs, worker reports, paste-back summaries, validator reports, PR checks, merge results, and blocked reports.

2. Feedback
   Add human feedback and model feedback. Human feedback includes Anthony's corrections, approvals, frustration markers, wrong-path reports, and too-sloppy events. Model feedback includes LLM-as-judge feedback, guardrail review, packet truth eval, safety checks, and hallucination checks.

3. Eval generation
   Convert repeated failures into reusable test cases for packet quality, repo truth, path correctness, safety compliance, and contextual coherence.

4. Validation gate
   Require local validation before any improvement becomes an APPLY packet. Validation must be docs/fixtures-only unless separately approved.

5. Improvement ranking
   Rank next improvements by safety impact, copy-paste reduction, automation value, repo execution value, trading safety value, trusted/proven profitability priority, friction reduction, frequency, blocker severity, and implementation risk.

6. Codex handoff
   Generate a Codex-ready draft packet for the highest-ranked improvement. Draft packets have no execution authority until a human-approved tokenized packet is issued.

7. Harness update
   Update AI_OS instructions, packet format, validators, routing, approval gates, or output contracts only through a scoped APPLY lane.

## Non-Goals

- No uncontrolled self-modification.
- No automatic commit, push, merge, or PR creation.
- No live OpenAI API calls.
- No runtime telemetry writes.
- No approval inbox runtime writes.
- No broker, OANDA, live trading, or real order behavior.
