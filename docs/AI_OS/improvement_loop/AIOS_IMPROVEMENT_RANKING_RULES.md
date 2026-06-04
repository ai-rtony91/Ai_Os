# AI_OS Improvement Ranking Rules

Purpose:
Define how AI_OS ranks candidate improvements from traces, feedback, and eval results.

## Ranking Criteria

Each recommendation is scored on:

- safety impact
- copy-paste reduction
- automation value
- repo execution value
- trading safety value
- trusted/proven profitability priority
- user-friction reduction
- frequency of repeated issue
- blocker severity
- implementation risk

## Suggested Scale

Use integer scores from `1` to `5`.

High priority means:

- safety impact is high
- issue repeats often
- operator friction is high
- trusted/proven profitability evidence is protected or improved
- implementation risk is low or manageable
- improvement strengthens existing gates instead of bypassing them

Low priority means:

- issue is rare
- value is mostly cosmetic
- implementation risk is high
- scope overlaps protected runtime systems
- dependency on live API, live telemetry, or package install is required

## Ranking Output

Ranked output should include:

- recommendation ID
- title
- evidence references
- scored criteria
- total priority score
- risk class
- next Codex handoff title
- required approval lane
- stop point
