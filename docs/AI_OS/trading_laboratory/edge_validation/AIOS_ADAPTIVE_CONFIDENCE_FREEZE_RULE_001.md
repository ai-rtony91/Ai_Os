# AI_OS Adaptive Confidence Freeze Rule 001

## Purpose

This rule formalizes adaptive confidence freeze behavior across AI_OS trading intelligence.

AI_OS may lower confidence quickly when a strategy becomes unstable. AI_OS must not raise confidence automatically again until enough paper evidence proves recovery.

## Freeze Triggers

- stability_score below threshold
- drawdown_pressure above threshold
- regime_reliability_score below threshold
- rolling_expectancy below threshold
- sample_size below minimum
- edge_state is WATCH
- edge_state is WEAK_EDGE
- edge_state is NO_EDGE

## Freeze Behavior

- block confidence increases
- allow confidence decreases
- lower ranking priority
- reduce recommended paper size
- require stronger confirmations
- require more paper evidence
- prevent fast re-promotion
- force WATCH state when unstable

## Recovery Conditions

- rolling stability recovered
- drawdown pressure reduced
- rolling expectancy positive
- minimum sample size met
- regime reliability recovered
- edge confidence recovered
- multiple paper sessions confirmed

## Required States

- CONFIDENCE_ACTIVE
- CONFIDENCE_FROZEN
- RECOVERY_REQUIRED
- WATCH
- WEAK_EDGE
- NO_EDGE

## Safety State

- paper_only_status: PAPER_ONLY
- live_execution_status: BLOCKED
- broker_api_status: BLOCKED
- autonomous_execution_status: BLOCKED
- internet_call_status: BLOCKED

This policy is recommendation-only and paper-only. It does not enable live execution.
