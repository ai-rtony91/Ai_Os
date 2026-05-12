# LLM Worker Connection Boundary

AI_OS is not installing external LLM agents in Phase 15.1.

This phase creates a local-first file queue and control layer only.

## Future Worker Rule

Future LLM workers must read task files and write output files only. They cannot directly trade. They cannot access secrets. They cannot bypass validators.

Future workers must follow these boundaries:

- Read local task files.
- Write local output files.
- Stay within allowed paths.
- Respect blocked paths.
- Keep live trading blocked.
- Keep broker and OANDA execution blocked.
- Keep API keys and secrets blocked.
- Wait for validation.
- Wait for user approval before APPLY, commit, or push.

## Control Layer

The local-first file queue is the control layer. External LLM frameworks are not enabled here.

