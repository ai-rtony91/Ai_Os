"""End-to-end orchestrator for the Forex owner evidence return lane."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from . import forex_closure_gap_router_v1 as gap_router
from . import forex_final_owner_review_packet_composer_v1 as packet_composer
from . import forex_missing_evidence_catalog_v1 as catalog_lib
from . import forex_owner_evidence_return_intake_v1 as intake_lib
from . import forex_owner_evidence_return_validator_v1 as validator_lib
from . import forex_readiness_checkpoint_ledger_v1 as ledger_lib


def _repo_root_from_path(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        return Path(repo_root).resolve()
    return Path(__file__).resolve().parents[2]


def _fixture_base(repo_root: Path) -> Path:
    return repo_root / "tests\\fixtures\\forex_delivery\\owner_evidence_return_v1"


def _default_evidence_paths(repo_root: Path) -> list[Path]:
    base = _fixture_base(repo_root)
    if not base.exists():
        return []
    selected = sorted(base.glob("*.md"))[:10]
    return [path.resolve() for path in selected]


def orchestrate_owner_evidence_return(
    *,
    repo_root: str | Path | None = None,
    catalog_paths: Iterable[str | Path] | None = None,
    evidence_paths: Iterable[str | Path] | None = None,
    strict: bool = False,
    include_already_present: bool = False,
) -> dict[str, Any]:
    root = _repo_root_from_path(repo_root)
    fixture_path = _fixture_base(root)

    catalog_payload = catalog_lib.build_missing_evidence_catalog(
        report_paths=tuple(catalog_paths) if catalog_paths is not None else None,
    )
    intake_payload = intake_lib.build_owner_evidence_return_intake(
        catalog_payload,
        include_already_present=include_already_present,
        strict=strict,
    )

    evidence_inputs = list(evidence_paths) if evidence_paths is not None else _default_evidence_paths(root)
    payloads = intake_lib.load_owner_evidence_payloads(evidence_inputs)
    intake_payload = intake_lib.apply_owner_payloads_to_intake(intake_payload, payloads)

    validator_payload = validator_lib.validate_owner_evidence_return_files(
        evidence_inputs,
        strict=strict,
        min_sample=30,
    )
    route_payload = gap_router.route_owner_evidence_closure(
        intake_payload,
        validator_payload,
        strict=strict,
    )
    packet_payload = packet_composer.compose_final_owner_review_packet(
        intake_payload,
        validator_payload,
        route_payload,
        strict=strict,
    )

    ledger = ledger_lib.build_readiness_checkpoint_ledger(
        packet_id=packet_payload["packet_id"],
        branch="lane/forex-owner-evidence-return-orchestration-v1",
        worktree=str(root),
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="intake",
        status=intake_payload.get("status", intake_lib.INTAKE_INVALID),
        route=None,
        blockers=[],
        notes=["intake completed"],
        metadata={
            "requested": intake_payload.get("summary", {}).get("requested_items"),
            "missing": intake_payload.get("summary", {}).get("missing_items"),
        },
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="validator",
        status=validator_payload.get("status", validator_lib.OWNER_RETURN_INVALID),
        route=None,
        blockers=validator_payload.get("blockers", []),
        notes=[f"fixture_path_count={len(list(evidence_inputs))}"],
        metadata={"path_count": validator_payload.get("path_count", 0)},
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="router",
        status=route_payload.get("route"),
        route=route_payload.get("route"),
        blockers=route_payload.get("status_blockers", []),
        notes=["route decision completed"],
        metadata={"owner_gaps": len(route_payload.get("owner_gap_families", []))},
    )
    ledger = ledger_lib.append_checkpoint_event(
        ledger,
        stage="packet_composer",
        status=packet_payload.get("status"),
        blockers=[],
        notes=["packet composed"],
        metadata={
            "owner_action_count": len(packet_payload.get("owner_actions", [])),
            "local_action_count": len(packet_payload.get("local_actions", [])),
        },
    )

    return {
        "orchestrator_version": "1.0",
        "generated_at": packet_payload.get("generated_at"),
        "strict_mode": strict,
        "branch": "lane/forex-owner-evidence-return-orchestration-v1",
        "worktree": str(root),
        "repo_root": str(root),
        "fixture_count": len(list(fixture_path.glob("*"))) if fixture_path.exists() else 0,
        "intake_payload": intake_payload,
        "validator_payload": validator_payload,
        "route_payload": route_payload,
        "packet_payload": packet_payload,
        "checkpoint_ledger": ledger,
        "safety": {
            "repo_mutation": False,
            "broker_api_calls": False,
            "trading_calls": False,
            "money_movement": False,
            "production_activation": False,
            "env_reads": False,
            "github_or_git_commands": False,
        },
    }


def orchestrate_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Owner Evidence Return Orchestration V1",
        f"Generated: {result.get('generated_at')}",
        f"Strict mode: {result.get('strict_mode', False)}",
        f"- Packet: {result.get('packet_payload', {}).get('packet_id')}",
        f"- Route: {result.get('route_payload', {}).get('route')}",
        f"- Packet status: {result.get('packet_payload', {}).get('status')}",
        f"- fixture_count: {result.get('fixture_count', 0)}",
        f"- Branch: {result.get('branch')}",
    ]
    lines.extend(["", "## Safety Flags"])
    for key, value in result.get("safety", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def orchestrate_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "orchestrator_version": result.get("orchestrator_version", "1.0"),
        "generated_at": result.get("generated_at"),
        "strict_mode": bool(result.get("strict_mode", False)),
        "branch": result.get("branch"),
        "worktree": result.get("worktree"),
        "repo_root": result.get("repo_root"),
        "fixture_count": int(result.get("fixture_count", 0)),
        "intake_payload": dict(result.get("intake_payload", {})),
        "validator_payload": dict(result.get("validator_payload", {})),
        "route_payload": dict(result.get("route_payload", {})),
        "packet_payload": dict(result.get("packet_payload", {})),
        "checkpoint_ledger": dict(result.get("checkpoint_ledger", {})),
        "safety": dict(result.get("safety", {})),
    }


__all__ = [
    "orchestrate_owner_evidence_return",
    "orchestrate_to_jsonable_dict",
    "orchestrate_to_markdown",
]
