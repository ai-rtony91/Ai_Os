# AI_OS Resumable State Strategy

Purpose:
Define allowed state strategies for pausable and resumable AI_OS runs.

## Rule

Pick one state strategy per run. Do not duplicate context by mixing strategies.

## Allowed Strategies

### local_replay_state

Stored in repo docs/fixtures only for now.

Best for:

- DRY_RUN previews
- deterministic local validation
- reproducible examples
- no-write runner tests

### session_state

Future AI_OS-controlled storage.

Best for:

- resumable approval flows
- long-running local work
- operator-directed pause/resume
- multi-step repo workflows

### previous_response_id

Future Responses API continuation.

Best for:

- lightweight OpenAI run continuation
- short model-turn follow-up
- minimizing repeated context

### conversation_id

Future shared server-managed state.

Use only when:

- multiple workers or services must share the same conversation
- reconciliation rules are explicit
- human approval allows server-managed state

## Reconciliation

If a run intentionally reconciles local replay with server-managed continuation, the final report must state:

- original strategy
- target strategy
- reason for reconciliation
- source of truth
- state fields copied
- state fields discarded
- safety review result

