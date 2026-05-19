# Phase 14.14 Strategy Performance Memory Engine

## Purpose

The strategy memory engine is the first paper-only AI_OS layer for tracking whether a strategy is getting better, getting worse, or becoming unreliable.

This stage does not execute trades. It creates a local reference model for remembering recent strategy performance and adjusting confidence before any future action is considered.

## Why Systems Need Memory

A strategy can look strong in one period and weak in another. Without memory, AI_OS would treat every signal as if the strategy quality never changed. That is dangerous because markets shift, spreads change, latency changes, and recent paper results can decay.

Memory helps AI_OS ask a better question: is this strategy still behaving like the version that tested well?

## Expectancy Decay

Expectancy is the average expected result over many samples. If recent paper outcomes get worse, expectancy can decay even when the older scorecard still looks healthy.

The memory layer should flag that decay instead of relying only on older performance.

## Regime-Based Degradation

Some strategies work in trending conditions and fail in choppy conditions. Others work in ranges and fail during fast breakouts.

Regime-based degradation means the strategy may be losing quality because the current market state no longer matches the intended environment.

## Session-Based Degradation

Performance can change by session. A setup that behaves well during London or New York may be weak during quiet or illiquid periods.

The memory engine tracks session context so a strategy can be reduced or blocked when recent session evidence is poor.

## Latency Degradation

If signal handling becomes too slow, paper results can become less reliable. A strategy may depend on timely confirmation, and delayed routing can damage the expected result.

The memory layer keeps a latency penalty as a paper-only adjustment to strategy confidence.

## Strategy Fatigue

Strategy fatigue happens when a setup keeps appearing but recent evidence shows weaker quality. That can come from overuse, changing conditions, or a pattern becoming crowded.

The memory engine should mark fatigue before the system keeps repeating low-quality paper decisions.

## Overfitting Danger

Overfitting happens when a strategy is tuned too closely to old examples and does not generalize. A high historical score is not enough by itself.

Adaptive memory helps compare recent paper behavior against old expectations.

## Why Adaptive Scoring Matters

Adaptive scoring helps AI_OS reduce confidence when evidence worsens and raise confidence only when enough recent paper data supports it.

The output remains paper-only:

- live_execution_status: BLOCKED
- strategy_allowed is only a paper review field
- scorecard_ready means ready for local review, not execution

Unsafe execution paths remain blocked.
