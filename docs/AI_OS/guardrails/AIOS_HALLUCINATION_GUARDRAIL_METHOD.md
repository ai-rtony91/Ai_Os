# AI_OS Hallucination Guardrail Method

Purpose:
Define a local, docs-only method for evaluating AI_OS assistant output against repo source-of-truth rules.

This method is inspired by eval-set guardrail patterns, but it is translated for AI_OS. It does not copy any external notebook, does not call OpenAI, does not require an API key, and does not install packages.

## AI_OS Translation

| Generic eval concept | AI_OS meaning |
| --- | --- |
| Source-of-truth policy | `AGENTS.md`, `docs/AI_OS/AGENTS.md` when present, workflow docs, governance docs, safety rules |
| Assistant output | Codex packet, Codex report, planner output, validator output, PR handoff, merge report |
| Hallucination | Unsupported repo claim, fake file claim, false safety claim, missing rule, wrong path, wrong branch, wrong status, invented validation result |
| Policy compliance | Follows AGENTS.md, allowed paths, forbidden paths, stop point, approval rules, no secrets, no live trading |
| Contextual coherence | Matches current phase, stage, lane, worktree, branch, repo status, and validated evidence |

## Eval Set Pattern

An AI_OS guardrail eval set contains:

1. A source-of-truth bundle.
2. One or more assistant outputs to evaluate.
3. A claim extraction list.
4. Sentence-level or claim-level scoring.
5. JSON result output.
6. Aggregate metrics for pass/fail readiness.

The eval must treat missing evidence as failure for factual claims. A claim is not true because it is plausible; it is true only when supported by an approved source or current command evidence.

## Claim Scoring

Each claim receives binary scores for:

- factual accuracy
- repo state accuracy
- path accuracy
- workflow compliance
- safety compliance
- contextual coherence

Each claim also receives:

- hallucination risk: `LOW`, `MEDIUM`, or `HIGH`
- pass/fail: `PASS` or `FAIL`
- rationale

## Metrics

AI_OS guardrail reports should calculate:

- total claims
- passing claims
- failing claims
- factual accuracy rate
- policy compliance rate
- safety compliance rate
- high-risk hallucination count
- precision-style supported-claim rate
- recall-style required-rule-coverage rate

These metrics are advisory in DRY_RUN. They do not approve APPLY, commit, push, merge, live API use, or live trading.

## Hard Blocks

The guardrail method must never:

- request or store API keys
- create `.env`
- make OpenAI calls
- make network calls
- install packages
- write runtime telemetry
- write approval inbox runtime state
- touch Night Supervisor runtime paths
- touch broker, OANDA, live trading, or order execution paths
