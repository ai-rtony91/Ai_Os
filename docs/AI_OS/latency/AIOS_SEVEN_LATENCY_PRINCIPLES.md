# AI_OS Seven Latency Principles

Purpose:
Map the seven latency principles to AI_OS execution surfaces.

## Exact Principles

1. Process tokens faster.
2. Generate fewer tokens.
3. Use fewer input tokens.
4. Make fewer requests.
5. Parallelize.
6. Make your users wait less.
7. Don’t default to an LLM.

## Mapping

| Principle | AI_OS packet generation | Codex validation | Night Supervisor | OpenAI Responses adapter | Trading Lab latency | Pi car voice | Dashboard/operator experience |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Process tokens faster. | Use explicit schemas and short packet sections. | Prefer focused validators over broad scans. | Keep previews concise and structured. | Select model intentionally for the task. | Keep paper-signal checks deterministic. | Use low-latency speech path only after safety gates. | Show compact status and next action. |
| Generate fewer tokens. | Avoid bloated packets and repeated background. | Report high-signal findings only. | Summarize blocker state without long narration. | Request structured JSON, not essays. | Keep latency reports concise. | Keep spoken responses short. | Avoid walls of text unless requested. |
| Use fewer input tokens. | Read only approved context needed for the lane. | Validate changed files, not the whole repo, unless needed. | Read scoped summaries and safe fixtures. | Send minimal source-of-truth context. | Use compact signal evidence. | Keep voice session context lean. | Use structured handoffs over transcripts. |
| Make fewer requests. | Batch related planning fields into one packet. | Run validators in purposeful groups. | Avoid repeated state checks without state change. | Combine packet draft request with safety classification when safe. | Avoid duplicate paper-signal analysis. | Avoid back-and-forth for obvious local state. | Cache known state in reports. |
| Parallelize. | Parallelize read-only planning checks. | Parallelize non-overlapping read-only validators. | Parallelize preview-only classification when no runtime write occurs. | Parallelize independent context reads before adapter calls. | Parallelize paper-only analysis that does not mutate shared files. | Parallelize wake/listen prep only when motor control is blocked. | Show multiple independent checks together. |
| Make your users wait less. | Provide current lane, blocker, and next safe action. | Explain failed validation immediately. | Emit report-only progress without starting runtime loops. | Use timeouts and fail-closed errors. | Prioritize latency evidence over feature polish. | Keep voice turn response short and interruptible. | Surface status without requiring screenshots. |
| Don’t default to an LLM. | Use templates and schemas for mechanical packets. | Use scripts for JSON, path, and git checks. | Use deterministic classification where possible. | Use LLM only when reasoning or generation is needed. | Use deterministic latency metrics before model analysis. | Use local deterministic controls for safety checks. | Use rules, validators, and status files before AI narration. |

## Priority Processing Rule

Priority processing is a future option for high-value user-facing latency-sensitive requests only. It must not be used for evals, batch jobs, ETL, nightly reports, telemetry bulk work, or routine background processing. Priority processing must never bypass approval gates, Trading Lab paper-only rules, broker/OANDA blocks, live-trading blocks, Pi GPIO/motor blocks, validator requirements, or clean-state checks.

