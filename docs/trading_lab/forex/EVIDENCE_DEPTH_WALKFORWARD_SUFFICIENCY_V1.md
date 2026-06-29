# Evidence Depth Walkforward Sufficiency V1

## What Was Built

This packet adds a deterministic repo-safe evidence depth gate for Forex candidate promotion. The gate checks minimum reviewed trade sample count, minimum walk-forward window count, and an evidence depth score before promotion can continue.

## What It Blocks

It blocks promotion when sample depth is too small, walk-forward coverage is insufficient, or the evidence score is below the review threshold.

## What It Proves

It proves the current repo can classify evidence sufficiency without broker contact, credentials, account identifiers, orders, demo authorization, live authorization, schedulers, daemons, webhooks, or background loops.

## How It Advances Forex

It turns evidence depth into a repeatable local gate that candidate selection and demo readiness can consume before protected broker boundaries are considered.

## What Remains Protected

Broker contact, credential use, `.env` access, account identifiers, account inspection, order execution, demo execution, live execution, schedulers, daemons, webhooks, workers, watchers, listeners, and background loops remain blocked.

## Next Safe Action

Use the generated state and report as repo-safe evidence for the candidate selector hardening gate.
