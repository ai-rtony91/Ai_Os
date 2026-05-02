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
