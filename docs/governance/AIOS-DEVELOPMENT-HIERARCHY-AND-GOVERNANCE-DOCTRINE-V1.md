# AIOS Development Hierarchy And Governance Doctrine V1

Doctrine ID: `AIOS-DEVELOPMENT-HIERARCHY-AND-GOVERNANCE-DOCTRINE-V1`

## Authority Relationship

`AGENTS.md` is the top AIOS repository authority for assistant conduct, packet governance, protected-action gates, and authority delegation.

This doctrine is delegated by `AGENTS.md`.

This doctrine governs hierarchy and identity only. It cannot override `AGENTS.md`, `RISK_POLICY.md`, security policy, protected paths, owner approval gates, or fail-closed rules.

If this doctrine conflicts with a higher authority, the higher authority wins.

## Official Hierarchy

```text
Mission
Program
Epic
Bucket
Packet
Apply
Validation
Report
Pull Request
Merge
Main
```

Operational flow:

```text
Mission -> Program -> Epic -> Bucket -> Packet -> Apply -> Validation -> Report -> Pull Request -> Merge -> Main
```

## Layer Meaning

| Level | Responsibility |
| --- | --- |
| Mission | Long-term objective. |
| Program | Full initiative. |
| Epic | Major capability. |
| Bucket | Related engineering work group. |
| Packet | Smallest approved engineering unit. |
| Apply | Implementation. |
| Validation | Correctness evidence. |
| Report | Durable evidence. |
| Pull Request | Repository review unit. |
| Merge | Integration into protected history. |
| Main | Protected source of truth. |

## Required Packet Identity Chain

Every governed AIOS packet must declare:

- Mission ID.
- Mission Name.
- Program ID.
- Program Name.
- Epic ID.
- Epic Name.
- Bucket ID.
- Bucket Name.
- Packet ID.
- Packet Name.

Packets missing this identity chain are incomplete unless `AGENTS.md` explicitly defines a lower-burden exception for the task type.

## ID Format

Use globally meaningful IDs that preserve lineage and avoid collisions across AIOS programs:

```text
MISSION-AIOS-001
PRG-FOREX-001
EPC-FOREX-001
BKT-FOREX-001
PKT-FOREX-001
PR-#####
MERGE-<commit-sha>
```

Program, Epic, Bucket, and Packet IDs should include a domain or program marker when practical.

## Governance Flow

Governance flows downward.

Evidence flows upward.

No child layer may violate a parent layer.

No packet may exceed its approved scope.

No delegated doctrine may override higher authority.

Programs govern Epics. Epics govern Buckets. Buckets govern Packets. Packets govern Apply work. Validation governs correctness evidence. Reports preserve evidence. Pull Requests govern repository review. Merge governs integration into protected history.

## Default PR Policy

The normal repository path is One Packet -> One PR.

Exceptions require owner approval and must be documented.

Exceptions may apply to tiny docs-only or maintenance bundles when repo policy permits.

Exceptions must not weaken risk, security, protected-path, validation, evidence, commit, push, PR, merge, or approval gates.

## Stop-Point Doctrine

Packets must declare a stop point.

Codex must stop at the stop point.

Commit, push, PR creation, merge, broker access, credential access, live execution, destructive action, scheduler creation, daemon creation, webhook creation, and financial action remain separate approvals unless explicitly included in the active packet and allowed by higher policy.

Validator success is evidence only. It does not approve protected actions.

## Future Packet Template Requirements

Every governed packet must include:

- Identity chain.
- Allowed paths.
- Forbidden paths.
- Validator chain.
- Final report format.
- Stop point.

The identity chain must include Mission ID, Mission Name, Program ID, Program Name, Epic ID, Epic Name, Bucket ID, Bucket Name, Packet ID, and Packet Name.

## Doctrine Boundary

This doctrine does not authorize implementation, commit, push, PR creation, merge, deployment, runtime mutation, broker access, OANDA access, credential access, `.env` reads, account ID access, live execution, autonomous execution, compounding execution, scheduler creation, daemon creation, webhook creation, SOS alert sending, notification sending, money movement, withdrawal, deposit, or Vacation Mode execution.
