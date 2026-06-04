# AI_OS Dispatch Red Team Integration

Dispatch hardening must consume Phase 18.7 red-team doctrine before routing future autonomy packets.

## Integration Points

- Prompt injection risk adds `PROMPT_INJECTION_RISK`.
- Unreviewed adversarial surface adds `RED_TEAM_REQUIRED`.
- Unknown tool, Skill, connector, webpage, PDF, email, uploaded document, or tool-output authority adds `UNKNOWN_RISK` unless explicitly validated.
- Promptfoo overreach into third-party testing adds `PROMPTFOO_EXECUTION_RISK` and `FORBIDDEN_PATH_RISK` or `NETWORK_RISK` as applicable.

## Improvement Chain

Dispatch failures feed:

```text
red_team_case -> red_team_result -> improvement_loop -> Codex handoff -> PR
```

Trusted/proven profitability remains the top priority.

