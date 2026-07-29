# AI_OS Orchestration Platform V1 migration

## Canonical public API

New integrations import `OrchestrationPlatform` or `create_platform` from
`automation.orchestration.platform`. The facade provides one stable surface for
queue planning, read-only dispatch planning, packet building and generation,
execution-packet resolution, canonical-spine assembly, validation, reporting,
and engineering countdowns.

```python
from automation.orchestration.platform import create_platform

platform = create_platform(repo_root)
spine = platform.spine()
validation = platform.validate(spine)
report = platform.report(spine)
```

## Component mapping

| V1 method | Reused canonical implementation |
| --- | --- |
| `queue` | `aios_packet_queue_planner.build_packet_queue_planner` |
| `dispatch` | `runtime_queue.aios_development_dispatcher.build_dispatch_plan` |
| `build_packet` | `aios_codex_packet_builder.build_repository_aligned_apply_packet` |
| `generate_packet` | `aios_codex_packet_from_queue.build_codex_packet_from_queue_item` |
| `resolve_packet` | `runtime_queue.aios_execution_packet_resolver.resolve_execution_packet` |
| `spine` | `aios_canonical_orchestration_spine_v1.build_orchestration_spine` |
| `report` | `aios_canonical_orchestration_spine_v1.render_orchestration_report` |
| `countdown` | `aios_work_countdown_v1.build_work_countdown` |

## Backward compatibility

Existing module imports and command-line entry points remain supported. No
runtime state files, schemas, PowerShell launchers, or governance authorities
move in V1. Migrate callers incrementally to the facade; do not copy underlying
component logic into new integrations. The earlier modules become compatibility
surfaces, not competing orchestration platforms.

## Safety and governance

The platform is composition-only and does not mutate queues, launch workers,
grant approvals, access brokers or credentials, place orders, or perform Git
operations. It preserves each reused component's fail-closed decisions. The V1
validator additionally blocks a spine if any permission or protected-action flag
is enabled, and validator PASS remains evidence rather than approval.

## Migration sequence

1. Replace multi-module imports with `automation.orchestration.platform`.
2. Instantiate one platform per repository root.
3. Compare old and facade outputs in existing tests.
4. Remove caller-local composition glue after parity is established.
5. Keep protected actions behind their existing approval and execution gates.

Do not delete compatibility modules until repository-wide reference checks show
that no supported caller uses them. This avoids a flag-day migration while
preventing future duplicate orchestration implementations.
