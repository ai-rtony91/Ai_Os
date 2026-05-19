# AI_OS Operator Visibility Model 001

The operator visibility model defines what AI_OS must show before any future automation trust can increase.

## Operator Questions

- Why does AI_OS trust this condition?
- Why does AI_OS distrust this condition?
- Why did confidence freeze?
- Why did edge degrade?
- Why did macro risk increase?
- Why did replay fail?
- Why was portfolio exposure reduced?

## Readable State Requirements

The dashboard should make confidence, edge, macro, replay, warning, and portfolio states readable without exposing raw internal clutter by default.

## Safety Boundary

This layer provides visibility only. It does not execute trades and does not connect to broker APIs.

