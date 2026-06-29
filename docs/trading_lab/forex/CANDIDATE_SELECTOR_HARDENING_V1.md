# Candidate Selector Hardening V1

## What Was Built

This packet adds a deterministic candidate selector that ranks repo-safe synthetic candidate records and rejects weak or unsafe candidates before promotion.

## What It Blocks

It blocks candidates with insufficient samples, negative expectancy, low profit factor, excessive drawdown, missing walk-forward evidence, weak evidence depth, worsened mitigation, or missing owner-review readiness.

## What It Proves

It proves candidate selection can be hardened with transparent rejection reasons while keeping all protected execution and runtime booleans false.

## How It Advances Forex

It gives AI_OS a repeatable way to select only a review-ready candidate from repo-safe evidence before any demo-readiness or protected broker proof step.

## What Remains Protected

Broker contact, credential use, `.env` access, account identifiers, account inspection, order execution, demo execution, live execution, schedulers, daemons, webhooks, workers, watchers, listeners, and background loops remain blocked.

## Next Safe Action

Use the selected review-ready candidate only as input to owner review and demo readiness decision evidence.
