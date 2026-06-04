# AI_OS Provider Runtime Boundaries

Purpose:
Define the AI_OS boundary between provider APIs, runtime paths, and future orchestration layers.

## Runtime Paths

Responses API path:
Text, tools, planner loops, packet generation, guardrail judging, validator suggestions, approval summaries, and structured reasoning.

Realtime API path:
Live voice and speech-to-speech for the future Pi car voice lane.

Agents SDK path:
Later orchestration layer for multi-agent crews after local doctrine, validation, approval, and safety gates mature.

ChatKit path:
Later UI or chat embed lane. It is not a current execution priority.

Agent Builder path:
Later visual workflow design and reference lane. It is not required for current AI_OS execution.

## Separate Gates

The real OpenAI API adapter remains separately gated. This pack does not implement API calls, credentials, network behavior, package installation, realtime sessions, tool calls, or agent runtime workers.

## Pi Car Boundary

The Pi car voice agent may speak, listen, summarize, and propose actions in a future approved voice session. It must not directly move motors, write GPIO control files, or execute physical actions.

## Trading Boundary

Trading Lab remains paper-only until validation gates prove trust. Broker execution, OANDA, live trading, and real orders remain blocked.

