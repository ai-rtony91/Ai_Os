# AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE

## PURPOSE
Defines how to start a clean ChatGPT session after memory reset.

## BOOTSTRAP ORDER
1. Upload or reference this file first.
2. Provide README.md, WHITEPAPER.md, ARCHITECTURE.md, AGENTS.md, and RISK_POLICY.md.
3. Provide AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md.
4. Provide AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md.
5. Provide AIOS_PROJECT_ASSUMPTIONS_AND_DEFAULTS.md.
6. Ask the assistant to summarize current safe operating rules before issuing commands.

## FIRST USER PROMPT
“Use these AI_OS context files as the source of truth. Do not assume. Give only the next safe actionable step.”

## EXPECTED ASSISTANT BEHAVIOR
- Identify active repo.
- Confirm DRY_RUN default.
- Preserve protected files.
- Ask for output verification after commands.
- Avoid live automation activation.
