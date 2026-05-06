# AI_OS Report Writer Input Contract Draft

## Purpose

This draft defines allowed and blocked source inputs for future report-writer preview and writing workflows.

Report writers may not write until separate approval.

## Input Scope

Future report-writer preview may consume approved, text-based outputs from validators and status helpers.

Input must be traceable, bounded, and suitable for human review.

## Input Non-Scope

This stage does not create a report writer, write report files, write metrics, write checkpoint index entries, write production telemetry, or create background automation.

## Allowed Inputs

Allowed inputs may include:

- validator output
- git status output
- protected diff output
- workflow state output
- Morning Brief state output
- dashboard snapshot output
- operator telemetry state output

## Blocked Inputs

Blocked inputs include:

- secrets
- credentials
- broker tokens
- private keys
- recovery keys
- live trading data
- uncontrolled screen contents

## Required Source Metadata

Future report-writer preview must identify source command, source file, source timestamp if available, source mode, and whether the source was DRY_RUN or APPLY.

## Required Validation Metadata

Future report-writer preview must identify validator_to_run, approval_required, protected-file check state, and whether DAILY_METRICS or CHECKPOINT_INDEX are involved.

## Output Preview Requirements

Output preview must show target_file, source_input, proposed_action, proposed_fields, blocked_fields, backup_required, validator_to_run, and approval_required before any write.

## Human Approval Requirements

Human approval is required before any report writer can write files.

Human approval is required before any writer can touch protected files, DAILY_METRICS, CHECKPOINT_INDEX, production telemetry, broker/trading output, or credentials.

## Future Stage 22

Future Stage 22 may define a DRY_RUN-only report-writer preview helper.

Future Stage 22 must preserve the rule that report writers may not write until separate approval.
