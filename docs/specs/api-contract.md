# API Contract

## Orchestrator → Agents

### Request
- intent: string
- context: object
- permissions: object

### Response
- status: success | fail
- result: object
- logs: array

---

## Agents → Execution

### Request
- action: string
- parameters: object

### Response
- output: object
- audit_id: string

## Standardization

- All requests must include intent, context, permissions
- All responses must include status, result, logs
- Execution must return audit_id
- No agent runs without orchestrator approval.
