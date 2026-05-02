# Automation Pipeline

## Flow

1. User Input
2. Intent Parsing
3. Orchestrator Routing
4. Planner Agent
5. Security Validation
6. Execution Agent
7. Plugin Execution
8. Result Generation
9. Audit Logging
10. UI Feedback

---

## Rules

- No execution without security approval
- All actions logged
- Fail-safe on any error
- Retry logic controlled by orchestrator

## Standardization

- Pipeline stages must follow exact order (no skipping)
- Each stage must log output
- Failures stop pipeline (fail-safe)
- Orchestrator controls retries only
- Security approval required before execution stage
