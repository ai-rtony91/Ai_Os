# AI_OS Skill Candidate Backlog

Purpose:
List candidate AI_OS skills for future reviewed implementation.

## Candidates

| Skill | Workflow | Initial Risk | Boundary |
| --- | --- | --- | --- |
| `repo-precheck` | Verify branch, worktree, clean state, and locks. | LOW | Read-only local checks. |
| `codex-packet-validator` | Validate token, lane, allowed paths, forbidden paths, stop point, and final report format. | LOW | Docs/schema only first. |
| `guardrail-truth-eval` | Score packet/report claims against source-of-truth rules. | MEDIUM | Fixture-only first. |
| `trading-lab-latency-review` | Review paper-only latency signals and doctrine compliance. | HIGH | Paper-only; no broker/OANDA/live trading. |
| `night-supervisor-runtime-precheck` | Verify runtime context before any future supervisor run. | HIGH | Read-only first; no runtime script modification. |
| `openai-cli-readiness` | Check local OpenAI CLI readiness without printing secrets or making API calls. | HIGH | No API call; no `.env`; no key printing. |
| `responses-smoke-test-review` | Review future one-call Responses API smoke-test evidence. | HIGH | Review-only; smoke test separately gated. |
| `pi-car-voice-prompt` | Prepare safe Pi car voice prompts and refusal boundaries. | HIGH | No GPIO/motor action. |
| `dashboard-visual-qa` | Check dashboard screenshots and operator-visible layout issues. | MEDIUM | Read-only visual QA first. |
| `file-policy-checker` | Validate changed files against allowed/forbidden path policy. | LOW | Read-only path checks. |

## Backlog Rule

Candidate status is not approval. Each candidate needs a separate APPLY packet, review, validation, and PR before becoming an active local AI_OS skill.
