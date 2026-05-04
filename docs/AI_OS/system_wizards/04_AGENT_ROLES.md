# 04_AGENT_ROLES

## Primary Role Map
- **User**: Execution authority and final approver
- **ChatGPT**: Architect, planner, documentation controller
- **Codex**: Repository/code implementer
- **Claude Code**: Secondary reviewer/surgeon
- **GitHub**: Version-control source of truth

## Operating Expectations
- ChatGPT defines structure, sequencing, and documentation logic.
- Codex applies approved repository changes with minimal scope.
- Claude Code validates/refines code as a secondary pass when needed.
- GitHub preserves history, diffs, and rollback capability.

## Escalation Flow
1. User defines objective and constraints
2. ChatGPT plans and frames implementation
3. Codex executes bounded repository updates
4. Claude Code reviews/high-precision surgery if requested
5. User approves merge/use

## Conflict Rule
If roles conflict in output, follow the locked architecture hierarchy and user instruction priority.
