# AI_OS Promptfoo Boundary

## Status

Promptfoo is future optional tooling for AI_OS. Phase 18.7 does not install Promptfoo, run Promptfoo, create Promptfoo execution configs, call OpenAI, install dependencies, or run network tests.

Promptfoo is only being captured as a future tool boundary so AI_OS can plan red-team and evaluation workflows safely before execution exists.

## Future Uses

Promptfoo may later be considered for:

- Red-team discovery.
- LLM-chain testing.
- Model/provider comparisons.
- Regression checks.
- Prompt and agent safety tests.
- Guardrail adherence testing.
- Fixture-driven local route tests.

## Execution Boundary

Future Promptfoo runs require a human-approved AI_OS packet that names:

- mode
- lane
- branch
- worktree
- allowed paths
- forbidden paths
- target fixtures or local endpoints
- provider/model boundary
- validator chain
- stop point

Future Promptfoo configs must not include secrets, real API keys, broker credentials, OANDA credentials, service account JSON, or `.env` values.

Future Promptfoo must run only against AI_OS-owned fixtures or local endpoints unless a human-approved packet explicitly authorizes another asset. AI_OS must not use Promptfoo to probe third-party systems, external services, live broker systems, OANDA, or Pi GPIO/motor controls.

## Current Phase Blocks

- Do not run Promptfoo yet.
- Do not install Promptfoo yet.
- Do not install dependencies yet.
- Do not call OpenAI.
- Do not call Azure OpenAI or other providers.
- Do not perform network testing.
- Do not run adversarial attacks.

Trusted/proven profitability remains the top priority. Promptfoo must serve safety, correctness, and regression discipline; it must not become a distraction from AI_OS trusted/proven profitability.

