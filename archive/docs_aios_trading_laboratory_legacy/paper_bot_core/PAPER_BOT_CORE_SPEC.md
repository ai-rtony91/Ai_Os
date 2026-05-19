# Paper Bot Core Spec

## Purpose

Paper Bot Core gives AI_OS a safe Trading Lab foundation for paper trading review. It uses local paper-trade sample data and never places real trades.

## Inputs

- Paper Trade Signal
- Paper Simulation timing note
- Paper Regime Review
- Paper Risk Gate result
- Paper Decision
- Paper Trade Result
- Paper Scorecard values

## Outputs

- Paper Decision only
- blocked or allowed Paper Simulation state
- Paper Scorecard summary
- Next Safe Action

## Safety

The Paper Risk Gate blocks by default. A Paper Decision can move forward only when paper trade review conditions pass.

No real execution path exists in this folder. Broker, OANDA, MT5, TradingView, TradersPost, credentials, API keys, account login, real webhook, and real order paths remain BLOCKED.
