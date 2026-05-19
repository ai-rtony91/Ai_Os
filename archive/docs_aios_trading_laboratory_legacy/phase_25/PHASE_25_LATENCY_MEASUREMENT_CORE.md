# Phase 25 Latency Measurement Core

## Purpose

Phase 25 creates a paper-only latency measurement core for Trading Lab.

The goal is to turn latency from a display field into a local measurement contract across the paper workflow:

paper signal -> validation -> route preview -> paper simulation -> journal -> scorecard

## Required Fields

- alert_created_time
- alert_received_time
- validation_start_time
- validation_end_time
- route_preview_time
- paper_execution_time
- journal_write_time
- scorecard_update_time
- total_delay_seconds
- stale_status
- delayed_reason
- clock_skew_status
- step_delays
- live_execution
- broker
- real_order
- api_key_required

## Step Delays

The fixture tracks these derived delay slots:

- alert_to_receive_seconds
- receive_to_validation_start_seconds
- validation_duration_seconds
- validation_to_route_preview_seconds
- route_preview_to_paper_execution_seconds
- paper_execution_to_journal_seconds
- journal_to_scorecard_seconds

If timestamps are unavailable, values stay null, Pending validation, or Not measured.

If any measured step is negative, the validator must treat it as clock skew and keep the workflow under review.

## Safety Boundary

Phase 25 is paper-only and local mock-data only.

Required states:

- live_execution: BLOCKED
- broker: BLOCKED
- real_order: BLOCKED
- api_key_required: false

Latency status must never unlock broker routing, live trading, real webhooks, real orders, OANDA, account connection, API keys, secrets, or autonomous execution.

## Dashboard Placement

Trading Lab only.

Display may appear inside Advanced Diagnostics or a workstation secondary panel. Keep the main workstation compact and show only a concise latency badge there if needed.

## Next Safe Action

Run the Phase 25 dry-run validator before using latency measurement in replay, journal, scorecard, or handoff review.
