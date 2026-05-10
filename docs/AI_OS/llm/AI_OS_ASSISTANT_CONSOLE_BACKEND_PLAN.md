# AI_OS Assistant Console Backend Plan

## Status

DRY_RUN / planning scaffold only. The dashboard Assistant Console is mock-only until a backend is explicitly approved.

## Decision

AI_OS should use one unified Assistant Console with multiple modes instead of multiple disconnected chat widgets.

Modes:
- Tour Guide
- Work Table Builder
- Research / Chat
- System Engineer
- Trading Lab

Each mode may use its own context intake packet. Work Table Builder uses the full project/work packet intake. Other modes use lighter, mode-specific packets.

## Projects Model

The Work Rail should expose Projects as a primary folder. Active projects live under Projects instead of becoming many unrelated rail items.

Initial project folders:
- AI_OS
- Trading Bot
- App Builder
- Web Dev
- Future Project

Each project can show static/mock-only sections:
- Project Brief
- Work Packets
- Telemetry
- Reports
- Validation
- Files / Paths
- Risks / Safety
- Next Actions

Project telemetry stays mock-only until a backend is approved. No broker, trading execution, API call, file writer, or execution-state persistence is allowed from the dashboard.

## Future Endpoint

Use one chat endpoint:

```text
/api/assistant/chat
```

Future request shape:

```json
{
  "mode": "tour-guide",
  "workspace": "active workspace/detail id",
  "selectedRailItem": "active rail/detail item",
  "project": "active project or user-selected project",
  "message": "user message",
  "userGoal": "plain-language user goal",
  "project": "project identity",
  "filesOrArea": "files, folders, app, or dashboard area",
  "desiredOutput": "expected result",
  "constraints": "special constraints or safety notes",
  "contextPacket": {
    "assistantMode": "tour-guide",
    "currentWorkspace": "active workspace",
    "selectedRailItem": "active detail",
    "safetyRules": [],
    "allowedActions": [],
    "blockedActions": [],
    "requiredApprovals": [],
    "knownUnknowns": [],
    "nextSafeAction": "recommended next step"
  }
}
```

Mode-specific context packets may include:
- Tour Guide: screen, target button/rail, explanation level, desired output.
- Work Table Builder: user goal, project, files/app area, desired output, constraints, evidence, approval state.
- Research / Chat: research topic, freshness requirement, depth level, output format, notes, citation requirement.
- System Engineer: device/OS area, app/tool, error/log output, desired fix, risk level, permission needed.
- Trading Lab: market/instrument, timeframe, strategy idea, indicators/rules, risk rule, backtest evidence, broker/execution status.

## Backend Options

Local development option:

```text
services/orchestrator/
```

Cloudflare Worker option, if approved later:

```text
services/assistant-worker/
```

## Security Rules

- The OpenAI API key must live only server-side as a secret.
- Do not place OpenAI keys in dashboard HTML, CSS, JS, localStorage, mock data, or Git.
- Do not store social passwords, OneDrive tokens, broker credentials, recovery codes, or private keys.
- Trading Lab mode is planning only. It must not place trades or enable broker execution.
- Voice mode is future-only and requires separate approval.

## Current Frontend Behavior

- Message sending is mock-only.
- No backend request is made.
- The console may show `/api/assistant/chat` as a planned endpoint only.
- Mode selection changes helper text and placeholder behavior only.
- Context Intake Packet generation is mock-only and runs in the dashboard UI.
- Context packets must not persist secrets, approvals, credentials, tokens, or execution state.
- Server-side context packet generation may be considered later after backend approval.
