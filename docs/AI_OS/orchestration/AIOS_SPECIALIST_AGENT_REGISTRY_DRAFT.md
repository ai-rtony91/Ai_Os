# AI_OS Specialist Agent Registry Draft

Purpose:
Provide a doctrine-only draft registry for future specialist roles. This is not a runtime registry and does not create live agents.

| Specialist | Default pattern | May own branch/session? | Blocked authority |
| --- | --- | --- | --- |
| Packet Generator | Tool | Only with explicit handoff | Commit, push, merge, runtime writes |
| Guardrail Judge | Tool | No by default | Approval, merge, runtime writes |
| Validator Dispatcher | Tool | No by default | Treating validator PASS as approval |
| Approval Summarizer | Tool | No by default | Writing real approval inbox state |
| Clean-State Verifier | Tool | No by default | Reset, clean, delete |
| Pi Car Voice Agent | Session owner only after approval | Voice session only | GPIO, motor movement, physical action |
| Trading Lab Evaluator | Paper-analysis lane after approval | Paper lane only | Broker, OANDA, live trading, real orders |
| Merge Lane Worker | Handoff after approval | Merge lane only | Merge without validation and human approval |

## Manager Rule

AI_OS Manager owns final answer, packet safety, validator chain, approval gate, profitability priority, and next action unless a handoff explicitly transfers a bounded lane.

