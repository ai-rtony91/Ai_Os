# AIOS Forex Live Micro Exception Owner Approval Card V1

## Purpose
- Capture explicit owner signoff fields before any live-micro exception review progression.
- This card is read-only evidence capture and cannot authorize execution.

## Explicit yes/no fields
- one-live-micro-trade-only_acknowledgement: `YES` / `NO`
- micro-size_acknowledgement: `YES` / `NO`
- sl_tp_acknowledgement: `YES` / `NO`
- daily-stop_acknowledgement: `YES` / `NO`
- max-loss_acknowledgement: `YES` / `NO`
- kill-switch_acknowledgement: `YES` / `NO`
- no-22hr-live-free-run_acknowledgement: `YES` / `NO`
- post-trade-evidence-capture_acknowledgement: `YES` / `NO`
- owner-live-micro-exception-approval: `YES` / `NO`

## Required confirmations
- Confirm the path from `REQUIRE_MORE_EVIDENCE` to `LIVE_MICRO_EXCEPTION_REVIEW_READY` is allowed for this operator context: `YES` / `NO`.
- Confirm the micro exception is constrained to one order max: `YES` / `NO`.
- Confirm micro-size controls are set and owner-valid: `YES` / `NO`.
- Confirm SL/TP placement and enforcement are verified for this exception type: `YES` / `NO`.
- Confirm daily stop threshold and reset rules are understood and enforceable: `YES` / `NO`.
- Confirm max loss is bounded and owner-approved for live-micro use: `YES` / `NO`.
- Confirm kill-switch path is immediate and testable: `YES` / `NO`.
- Confirm no 22-hour free-run operation will be used: `YES` / `NO`.
- Confirm post-trade evidence capture plan is in place before any live-micro close: `YES` / `NO`.
- Confirm no credentials or account identifiers are accepted in repo artifacts for this stage: `YES` / `NO`.
