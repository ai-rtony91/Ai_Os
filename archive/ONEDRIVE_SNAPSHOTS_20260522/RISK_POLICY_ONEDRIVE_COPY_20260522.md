# AI_OS Risk Policy Index

## Purpose

This root file points to current AI_OS safety and risk-control rules.

## Source Rule Files

- Master rules: `docs\AI_OS\02_RULES\AIOS_MASTER_RULES.md`
- No-touch rules: `docs\AI_OS\02_RULES\AIOS_NO_TOUCH_RULES.md`
- Data integrity rules: `docs\AI_OS\02_RULES\DATA_INTEGRITY_AND_CORRUPTION_PREVENTION_RULES.txt`
- Checkpoint rules: `docs\AI_OS\02_RULES\CHECKPOINT_AND_STAGE_COMPLETION_RULES.txt`
- Hallucination prevention rules: `docs\AI_OS\02_RULES\HALLUCINATION_PREVENTION_RULES.txt`

## Root Policy

No files may be moved, deleted, renamed, overwritten, or merged without dry-run review, explicit approval, and a safe rollback path.

Secrets, credentials, broker tokens, private keys, and Windows security settings are no-touch unless a separate approved safety process exists.

