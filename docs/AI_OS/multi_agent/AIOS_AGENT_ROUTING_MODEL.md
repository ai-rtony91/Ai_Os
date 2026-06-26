# AI_OS Agent Routing Model

Status: APPLY scaffold
Mode: local-first planning only

## Purpose

Define how AI_OS should route future work between ChatGPT, Codex, Claude, validators, and the human operator.

## Routing Chain

```text
user goal
-> ChatGPT planning
-> AI_OS task packet
-> safety and ownership check
-> Codex DRY_RUN
-> human APPLY approval
-> Codex implementation
-> validator chain
-> optional Claude review
-> human final review
-> separate commit approval
-> separate push approval
```

## Routing Rules

- Simple user tasks stay in Basic mode.
- Agent internals stay hidden unless Advanced is opened.
- Any file-changing work starts with DRY_RUN.
- APPLY requires explicit human approval.
- Claude can review, summarize, and challenge reasoning only.
- Codex can edit files only inside the approved scope.
- ChatGPT cannot bypass human approval.
- Validators must run before commit planning.

## Task Classes

Planning tasks route to ChatGPT.

Implementation tasks route to Codex after DRY_RUN.

Review tasks may route to Claude later.

Safety tasks route to the risk gate and validators.

Trading Lab tasks route through default paper/simulation checks and broker-gate checks.

## Blocked Routes

The router must block tasks that request:

- secrets or API keys
- Anthropic integration
- OpenAI integration changes
- installs
- deployment
- live trading
- broker connection
- OANDA
- real webhooks
- real orders
- autonomous commit
- autonomous push

## Next Safe Action Labels

Allowed next actions:

- exact Codex DRY_RUN prompt
- exact Codex APPLY prompt after approval
- exact PowerShell validation command
- exact review instruction
- exact checkpoint instruction

Blocked next actions:

- connect account
- enter API key
- enable webhook
- enable broker
- place order
- commit without approval
- push without approval
