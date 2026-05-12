# Paper Bot Core Spec

## Purpose

Paper Bot Core gives AI_OS a safe Trading Lab foundation for paper-only trading review.

## Inputs

- mock signal
- latency note
- regime tag
- risk gate result
- paper decision
- paper trade result
- scorecard values

## Outputs

- paper-only decision
- blocked or allowed paper simulation state
- scorecard summary
- next safe action

## Safety

The default state is blocked. A paper decision can move forward only when mock conditions pass the risk gate.

No real execution path exists in this folder.

