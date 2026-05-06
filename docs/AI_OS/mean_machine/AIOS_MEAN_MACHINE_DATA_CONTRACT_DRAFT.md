# AI_OS Mean Machine Data Contract Draft

## Purpose

This draft defines future data fields Mean Machine may read or write as dashboard-visible output.

All fields are advisory/visibility-only at this stage. execution_allowed must remain false.

## Data Contract Scope

The contract may guide future static dashboard display, DRY_RUN validation, and operator review workflows.

Mean Machine output must remain informational and must not trigger broker routing, webhook firing, strategy activation, credential access, or order placement.

## Data Contract Non-Scope

This draft does not create live execution.

This draft does not create broker integration.

This draft does not enable webhooks.

This draft does not access credentials, broker tokens, private keys, recovery keys, or secrets.

This draft does not create production telemetry writers or scheduled tasks.

## Future Input Fields

Future Mean Machine input fields may include:

| Field | Purpose |
| --- | --- |
| `symbol` | Instrument or market symbol for display. |
| `market` | Market category for display. |
| `timeframe` | Timeframe under review. |
| `screener_signal_type` | Signal type from the screener contract. |
| `screener_confidence_score` | Confidence score from screener output. |
| `trend_state` | Future trend state label. |
| `volume_state` | Future volume state label. |
| `volatility_state` | Future volatility state label. |
| `risk_state` | Risk state for operator review. |
| `telemetry_mode` | Telemetry mode from approved telemetry mapping. |
| `production_ready` | Production readiness state for display. |

## Future Output Fields

Future Mean Machine output fields may include:

| Field | Purpose |
| --- | --- |
| `mean_machine_state` | Advisory component state. |
| `analysis_summary` | Human-readable analysis summary. |
| `disagreement_flag` | Whether inputs disagree or require review. |
| `confidence_adjustment` | Advisory adjustment for review only. |
| `review_required` | Whether human review is required. |
| `approval_required` | Whether approval is required. |
| `execution_allowed` | Must remain false. |

## Risk Fields

Risk fields must remain display-only and may include `risk_state`, disagreement state, confidence adjustment, and review-required state.

Risk fields must not place orders, route broker requests, fire webhooks, access credentials, or activate strategies.

## Approval Fields

Approval fields may include `approval_required` and `review_required`.

Approval fields must not bypass human review or create an approval automatically.

## Blocked Fields

The data contract must not include fields that enable:

- Broker order placement.
- Live trading.
- Webhook firing.
- Auto-routing.
- Credential access.
- Strategy activation.
- `execution_allowed true`.

## Protected Data Restrictions

No credential, broker token, private key, recovery key, or live order field is allowed.

Protected data must not be read, stored, displayed, routed, logged, or transformed by Mean Machine in this stage.

## Future Stage 19

Future Stage 19 may propose static sample data or a DRY_RUN-only validator extension.

Future Stage 19 must keep execution_allowed false unless a separate approval explicitly changes scope.
