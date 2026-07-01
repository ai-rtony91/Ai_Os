# AIOS Forex Owner Consent And Trade Authority Policy V1

## Status

Internal product policy. This document is not legal advice, not trading authorization, not broker approval, and not release approval.

AIOS Forex is not Play Store ready until final release review. AIOS Forex is not legally or commercially approved until owner legal/compliance review.

## Purpose

This policy defines the consent and authority boundaries required before AIOS Forex Vacation Mode control-plane implementation proceeds.

## Owner Approval Hierarchy

Authority order:

1. Human Owner approval.
2. `RISK_POLICY.md` safety boundary.
3. Packet scope and allowed paths.
4. Source implementation gates.
5. Validator evidence.
6. Dashboard or report state.

Validator, dashboard, alert, report, packet, or telemetry output cannot grant approval by itself.

## Read-Only States

Read-only states may inspect policy, local evidence, dry-run status, sanitized reports, and metadata. Read-only states must not mutate broker state, send orders, send notifications, start schedulers, start daemons, call webhooks, or change authority state.

## Metadata-Only States

Metadata-only readiness may show that docs, validators, evidence, or owner-review prerequisites exist. Metadata-only readiness is not live execution authority.

## Owner-Review States

Owner-review states require Anthony to approve or reject the exact next action. These states must show:

- requested action.
- risk boundary.
- evidence.
- stop condition.
- approval window.
- expected result.
- kill-switch or shutdown path.

## Live-Micro Action Boundary

Any future live-micro boundary must follow `RISK_POLICY.md`. Required concepts include one order only, explicit arming, maximum loss, daily stop, stop loss, order type, approval window, sanitized evidence, and hard stop after fill, rejection, error, timeout, or expiry.

This document does not activate that boundary.

## Vacation Mode Authority Boundary

Vacation Mode may coordinate observation, readiness display, owner prompts, and controlled review state after implementation. It must not:

- call broker APIs.
- route live orders.
- retry trades.
- escalate authority.
- hide risk.
- bypass owner approval.
- persist credential values.
- expose account identifiers.
- run as hidden background execution.

## One-Action Stop Rule

Any approved live-micro action must stop after one action outcome. Fill, rejection, error, timeout, cancelled state, or approval expiry ends the action window and requires owner review before any next attempt.

## Repeat Attempt Gate

Repeat attempts require a new owner review. No dashboard state, alert, strategy output, or Vacation Mode state may approve repeated attempts by implication.

## Kill Switch And Stop Authority

Kill-switch and stop authority must override automation. Before release, AIOS Forex must define:

- user-visible stop control.
- owner emergency-stop process.
- daily-loss stop handling.
- approval expiry handling.
- shutdown evidence.
- support/escalation path.

## Alert Acknowledgement Model

Acknowledging an alert means the owner saw it. It does not approve a trade, repeat attempt, broker action, credential access, notification sending, scheduler creation, daemon creation, webhook creation, deployment, or public release.

## Evidence After Action

Any approved action must emit sanitized evidence showing:

- approval record.
- action attempted.
- outcome.
- stop condition.
- risk controls.
- redaction result.
- next owner-review requirement.

## No Autonomous Escalation

AIOS Forex must not escalate beyond approved limits. Metadata, alerts, reports, readiness states, or validation passes may recommend review but cannot become execution authority.
