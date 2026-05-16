# AI_OS Phase 3 Stateful Orchestration

Phase 3 adds a DRY_RUN-only stateful orchestration foundation on top of the existing queue and dispatcher flow.

## Files

- `work_packets/state/aios_queue_state.example.json`
- `work_packets/approvals/aios_approval_inbox.example.json`
- `work_packets/lifecycle.schema.json`
- `automation/operator/Invoke-AiOsApprovalGate.ps1`
- `automation/operator/Invoke-AiOsStatefulDispatcher.ps1`
- `automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1`

## Boundary

The Phase 3 foundation previews queue state, approval state, lifecycle state, lane state, and next routing action. It does not mutate queue files, auto-launch Codex, create startup tasks, create scheduled tasks, connect brokers, use OANDA, call APIs, receive webhooks, enable live trading, commit, or push.

## Validation

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1
```
