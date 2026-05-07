# AIOS Recovery Workflow Draft

Status: Draft planning doc
Stage: 12.9

## Workflow

1. Stop current action.
2. Capture error.
3. Identify affected files.
4. Read latest checkpoint.
5. Propose recovery DRY_RUN.
6. Wait for approval.

## Boundary

Recovery does not delete, reset, or overwrite automatically.
