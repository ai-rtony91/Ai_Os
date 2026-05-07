# AI_OS Stage 97 LLM Live Order Path Exclusion Draft

## Purpose

This draft defines the LLM/live-order-path exclusion rule. Production readiness is not approved by this draft.

No protected root files are edited by this draft. Human approval is required before any future trading integration review. This draft creates no live automation and no trading automation. LLMs must not be placed in the live order path.

## Exclusion Rule

- LLMs must not be placed in the live order path.
- LLMs may assist with documentation, planning, validation, review, and offline analysis.
- LLMs may not approve orders, route orders, place orders, modify broker instructions, or bypass risk controls.
- Deterministic execution systems must own live order routing if future trading is approved.
- Human approval and risk controls are required before any future trading integration.

## Non-Approval Rule

This file does not approve trading integration.

## Boundary

This draft does not approve production readiness, broker automation, live trading, active writers, persistence, startup automation, protected root file edits, or live automation.
