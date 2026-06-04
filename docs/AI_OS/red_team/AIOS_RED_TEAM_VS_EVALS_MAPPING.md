# AI_OS Red Team vs Evals Mapping

## Mapping

| Concept | AI_OS meaning | Boundary |
| --- | --- | --- |
| Evals | Intended behavior checks. | Confirm expected behavior works under normal or bounded inputs. |
| Red team | Adversarial and bypass checks. | Test misuse, unsafe inputs, prompt injection, approval bypass, forbidden path access, and unsafe tool use. |
| Trace grading | Full-run scoring. | Score the whole agent run, including reasoning path, tool use, stop behavior, and final report. |
| Guardrail eval | Output and rule compliance. | Check whether outputs preserve policies, blocked actions, allowed paths, and required refusal/recovery formats. |
| Improvement loop | Failure-to-fix pipeline. | Turns failures into future fixes through `red_team_case -> red_team_result -> improvement_loop -> Codex handoff -> PR`. |
| Latency doctrine | Cost and runtime restraint. | Prevents slow, expensive, or over-broad test execution when fixture or local checks are enough. |
| Skills doctrine | Reusable bundle safety. | Prevents unsafe reusable bundles from bypassing AI_OS governance, lane limits, or approvals. |
| Dispatch doctrine | Route execution safety. | Prevents unsafe route execution, wrong-lane dispatch, and runtime starts from docs-only packets. |

## Required Rules

- Red team only AI_OS-owned or authorized assets.
- Do not probe third-party systems.
- Do not run destructive tests.
- Do not run live trading tests.
- Do not use real secrets.
- Do not use real broker/API keys.
- Do not run Promptfoo yet.
- Do not install dependencies yet.
- Human approval is required before any executable red-team harness.
- Trusted/proven profitability remains the top priority.

## Practical Use

Evals should answer: did AI_OS do the intended thing?

Red-team cases should answer: did AI_OS refuse or stop when the input tried to make it do the wrong thing?

Trace grading should answer: did the entire run stay inside AI_OS rules from start to stop point?

