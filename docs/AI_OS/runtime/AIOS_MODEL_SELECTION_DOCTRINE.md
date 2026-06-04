# AI_OS Model Selection Doctrine

Purpose:
Define how AI_OS chooses model strength and runtime placement before any real OpenAI API adapter, Pi car realtime voice lane, or multi-agent orchestration is implemented.

## Core Rule

AI_OS must select models explicitly. Do not rely on SDK defaults.

Every future model-backed agent, tool, judge, planner, or voice session must declare:

- runtime path
- selected model
- reason for the model choice
- consequence level
- fallback behavior
- allowed paths
- forbidden paths
- stop point
- human approval requirements

## Model Strength Guidance

Use stronger models for:

- planner work
- judge or guardrail review
- safety review
- high-consequence reasoning
- merge or approval summaries
- Trading Lab paper-analysis decisions that affect trusted/proven profitability evidence

Use smaller or faster models only for:

- low-risk summaries
- bounded formatting
- fixture generation
- status condensation
- local docs-only drafting
- deterministic helper text

Use workflow-level defaults only when several agents should share the same runtime choice for a controlled workflow. Workflow defaults must still be explicit and documented.

## Profitability Priority

Trusted, proven profitability outranks feature expansion. Model selection must not optimize for novelty, UI polish, voice features, or agent count ahead of paper-trading evidence quality, validator trust, and operator clarity.

## Blocked

- No real OpenAI API call is enabled by this doctrine.
- No API key is requested.
- No `.env` file is created.
- No package install is approved.
- No network call is approved.
- No live trading, broker, OANDA, or real order behavior is approved.

