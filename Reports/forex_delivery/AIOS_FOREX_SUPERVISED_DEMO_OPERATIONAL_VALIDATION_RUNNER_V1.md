# AIOS Forex Supervised Demo Operational Validation Runner V1

## Packet Identity

- Mission ID: MISSION-AIOS-001
- Mission Name: AIOS Governed Self-Building Operating System
- Program ID: PRG-FOREX-001
- Program Name: AIOS Forex Supervised Operational Validation Program V1
- Epic ID: EPC-FOREX-001
- Epic Name: Demo Operations
- Bucket ID: BKT-FOREX-001
- Bucket Name: Demo Runtime
- Packet ID: PKT-FOREX-001
- Packet Name: Supervised Demo Operational Validation Runner

## Purpose

This runner decides whether a selected review-ready Forex candidate is eligible to enter supervised demo validation.

## Scope

In scope: deterministic local validation of supplied candidate readiness, owner review state, operational evidence, and hard safety boundaries.

Out of scope: broker access, OANDA access, credential access, .env access, account ID access, live routing, demo routing, paper routing, runtime activation, scheduler creation, daemon creation, webhook creation, production activation, compounding execution, and money movement.

## Implementation Summary

- Created a pure Python local validator with deterministic result keys.
- Created a CLI runner that prints JSON and can write this report when explicitly requested.
- Added focused tests for ready, blocked, rejected, incomplete-evidence, report-write, deterministic-key, and no external behavior paths.
- Latest default sample status: REQUIRE_MORE_EVIDENCE

## Decision Statuses

- READY_FOR_SUPERVISED_DEMO_VALIDATION: all readiness, owner approval, kill switch, and safety checks are satisfied.
- REQUIRE_MORE_EVIDENCE: hard safety boundaries are intact, but readiness evidence is incomplete.
- BLOCKED_BY_SAFETY_BOUNDARY: one or more hard safety boundary checks is explicitly false.
- REJECTED_FOR_DEMO_VALIDATION: the candidate is explicitly not review-ready or explicitly rejected.

## Safety Boundary

This packet does not authorize broker access, OANDA access, credential access, .env access, account ID access, live routing, demo routing, paper routing, runtime activation, scheduler, daemon, webhook, production activation, compounding execution, or money movement.

## Validation

- Validator chain: py_compile, focused pytest, CLI JSON smoke run, CLI report-write smoke run, git diff --check, and git status.
- The default run is intentionally REQUIRE_MORE_EVIDENCE unless explicit supplied input proves readiness.

## Remaining Work

This completes PKT-FOREX-001 only.
Remaining declared implementation/evidence packets after this: 9.

## Next Packet

PKT-FOREX-002 Demo Trade Evidence Collector.
