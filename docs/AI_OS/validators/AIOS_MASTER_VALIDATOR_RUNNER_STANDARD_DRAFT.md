# AIOS Master Validator Runner Standard Draft

Status: Draft planning doc
Stage: 12.2

## Purpose

Define the standard for a single read-only runner that invokes AI_OS DRY_RUN validators.

## Requirements

- enumerate validator paths
- detect missing validators
- run validators read-only
- summarize PASS/FAIL status
- escalate failed validators
- avoid writing files by default

## Output Format

- validator_path
- exists
- exit_code
- status
- next_action

## Boundary

The runner must not connect brokers, add secrets, create trading code, or modify protected root governance files.
