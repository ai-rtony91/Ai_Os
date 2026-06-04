# AI_OS Handoff vs Tools Rules

Purpose:
Define when AI_OS uses specialists as tools and when it transfers ownership by handoff.

## Default Pattern

Agents as tools is the default pattern.

Use a tool when:

- AI_OS Manager should own the final answer
- task is bounded
- output can be returned as JSON, markdown, or a checklist
- specialist does not need to own branch state
- specialist does not need to continue the conversation
- safety gates remain with Manager

## Handoff Pattern

Handoff is only for branch ownership transfer.

Use handoff when:

- the specialist must own the next response
- the specialist must own a scoped branch or lane
- the workflow needs a different worker identity
- state must continue under another lane
- human approval and stop point are explicit

## Examples

- Guardrail Judge should usually be a tool.
- Validator Dispatcher should usually be a tool.
- Packet Generator should usually be a tool.
- Pi Car Voice Agent may own a voice session, but not motor actions.
- Trading Lab evaluator may own paper-analysis lane, but not live execution.
- Merge lane can be handed off only after validation and human approval.

## Blocked Transfers

No handoff may transfer authority to:

- commit without approval
- push without approval
- merge without approval
- call OpenAI without separate approval
- write runtime telemetry
- write approval inbox runtime state
- move Pi motors
- place live orders
- call broker or OANDA APIs

