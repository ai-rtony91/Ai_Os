# Problem Classification Rules

Problem classification means naming what kind of issue this is before fixing it.

Common categories:

- UI-only: visual layout, labels, spacing, icons, clutter, mobile readability.
- Logic-only: state changes, button behavior, playback state, panel open/close behavior.
- Mock-data-only: fixture JSON, example data, fake status values.
- Trading-Lab-only: Trading Lab paper/simulation docs, mock signals, risk gates, scorecards, and broker-gate checks.
- Connector/API-only: planned connection to another app or service.
- Validator gap: missing or weak validation.
- Mixed scope: more than one unrelated area is touched.

Dock player examples:

- Icon says pause but playback is stopped: logic-only or UI state issue.
- Dock player labels are unclear: UI-only readability issue.
- Dock player overlaps on phone size: UI-only mobile readability issue.
- Dock player uses a fixture status that is wrong: mock-data-only issue.
- Dock player change also edits Trading Lab files: mixed scope and should be split.

If the category is unclear, mark it UNKNOWN and do not repair yet.
