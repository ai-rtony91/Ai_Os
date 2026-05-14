# AI_OS Worker Packets

Worker packets define one bounded unit of AI_OS work.

Each packet should identify the objective, owner, allowed paths, blocked paths, mode, validation steps, expected files, approval needs, and next safe action.

## Folder Roles

- `active/`: packets currently assigned or under review.
- `completed/`: packets validated as complete.
- `blocked/`: packets needing operator review.
- `templates/`: packet templates for future worker assignments.

## Rules

- One active packet per worker.
- APPLY requires explicit approval.
- Commit and push require separate approval.
- Do not use packet files to authorize live trading, broker execution, API key collection, startup tasks, or scheduled tasks.
