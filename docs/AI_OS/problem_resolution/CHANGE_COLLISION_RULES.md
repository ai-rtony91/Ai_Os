# Change Collision Rules

A collision happens when one repair package mixes unrelated work.

Examples:

- Dock player fix also edits Trading Lab strategy files.
- Mobile spacing fix also changes product brochure docs.
- Mock-data fix also edits dashboard CSS.
- Connector/API planning also adds real tokens.
- Validator patch also changes UI layout.

Collision result:

- Stop.
- Mark the package as mixed scope.
- Split into smaller repair requests.
- Send each request through change control.

Dock player safe package:

- One dock player UI-only repair.
- Exact dashboard files named.
- No Trading Lab files.
- No product docs.
- No connector/API activation.
- No secrets.
- One commit package.
