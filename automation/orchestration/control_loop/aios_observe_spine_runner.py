from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_OBSERVE_SPINE_RUNNER.v1"
MODE = "DRY_RUN_PREVIEW_ONLY"

READY = "OBSERVE_LOOP_READY"
BLOCKED = "OBSERVE_LOOP_BLOCKED"
INVALID = "OBSERVE_LOOP_INVALID"
LAYER_INVALID = "INVALID"
LAYER_BLOCKED = "BLOCKED"
LAYER_READY_PREFIX = "READY_FOR_"

READY_LAYER_STATUSES = (LAYER_READY_PREFIX,)

REPORT_DIR = Path("Reports") / "control_loop_observe"
REPORT_JSON_NAME = "observe_spine_runner_report.json"
REPORT_MD_NAME = "observe_spine_runner_summary.md"

CLOSURE_DIR = Path("Reports") / "autonomy_closure"
CLOSURE_JSON_NAME = "autonomy_closure_report.json"
CLOSURE_MD_NAME = "autonomy_closure_summary.md"

P2_BRIDGE_PATH = Path("automation/orchestration/runtime_closure/aios_p2_enqueue_bridge.py")
QUEUE_GATE_PATH = Path("automation/orchestration/work_packets/aios_queue_mutation_gate.py")
RUNTIME_APPLY_PATH = Path("automation/orchestration/runtime_closure/aios_runtime_apply_lane_preview.py")
SOS_PREVIEW_PATH = Path("automation/orchestration/notifications/aios_sos_arming_preview.py")
SCHEDULER_PREVIEW_PATH = Path("automation/orchestration/scheduler/aios_scheduler_registration_preview.py")

PROTECTED_PATHS = (
    Path("automation/orchestration/work_packets/active"),
    Path("automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
    Path("automation/orchestration/approval_inbox"),
    Path("automation/orchestration/command_queue"),
    Path("automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"),
    Path("services"),
    Path("services/runtime"),
    Path("telemetry"),
)

STALENESS_MARKERS = (
    "allowed_paths is required",
    "forbidden_paths is required",
    "evidence is required",
    "invalid evidence",
    "invalid contract",
    "source was not found",
    "stale evidence",
)

GOVERNANCE_MARKERS = (
    "approval",
    "human gate",
    "explicit approval",
    "approval evidence",
    "human approval",
)

CODE_MARKERS = (
    "missing required evidence",
    "required evidence",
    "queue gate evidence was not found",
    "proposed queue item source was not found",
    "missing runtime proof",
    "runtime proof gate preview missing",
    "invalid evidence path",
)


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_status(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_")


def _is_ready_status(status: str) -> bool:
    return any(status.startswith(prefix) for prefix in READY_LAYER_STATUSES)


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _maybe_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict) and value:
        return value
    return None


def _compact_dict(**items: Any) -> dict[str, Any]:
    return {key: value for key, value in items.items() if value is not None}


def _ensure_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_fingerprint(path: Path) -> dict[str, Any]:
    if path.is_file():
        return {
            "kind": "file",
            "path": path.as_posix(),
            "exists": True,
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
    if path.is_dir():
        entries = sorted(str(item.relative_to(path).as_posix()) for item in path.rglob("*") if item.is_file())
        return {
            "kind": "dir",
            "path": path.as_posix(),
            "exists": True,
            "entries": entries,
            "sha256": None,
        }
    if not path.exists():
        return {"kind": "missing", "path": path.as_posix()}
    return {"kind": "other", "path": path.as_posix(), "exists": True}


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect_invalid_and_blockers(layer: dict[str, Any], *, status: str) -> tuple[list[str], list[str]]:
    invalid = _ensure_list(layer.get("invalid_reasons"))
    blockers = _ensure_list(layer.get("blockers"))
    validation = _ensure_dict(layer.get("validation"))
    invalid.extend(_ensure_list(validation.get("invalid_reasons")))
    blockers.extend(_ensure_list(validation.get("blockers")))

    blockers.extend(
        [
            str(value).strip()
            for key, value in layer.items()
            if isinstance(key, str)
            and "status_reason" in key.lower()
            and isinstance(value, str)
            and str(value).strip()
        ]
    )
    return invalid, blockers


def _classify_layer(name: str, status: str, layer: dict[str, Any]) -> dict[str, Any]:
    invalid, blockers = _collect_invalid_and_blockers(layer, status=status)
    text = " ".join(invalid + blockers).lower()

    stale = status == LAYER_INVALID and any(marker in text for marker in STALENESS_MARKERS)
    governance = any(marker in text for marker in GOVERNANCE_MARKERS)
    code = any(marker in text for marker in CODE_MARKERS)

    real_blocker = False
    if status == LAYER_BLOCKED:
        real_blocker = not stale
    elif status == LAYER_INVALID:
        real_blocker = not stale

    return {
        "name": name,
        "status": status,
        "stale": stale,
        "real_blocker": real_blocker,
        "governance_blocker": governance,
        "code_blocker": code,
        "invalid_reasons": invalid,
        "blockers": blockers,
    }


def _collect_layer_statuses(layers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "stale_layers": [name for name, payload in layers.items() if payload.get("stale")],
        "real_blockers": [name for name, payload in layers.items() if payload.get("real_blocker")],
        "governance_blockers": [name for name, payload in layers.items() if payload.get("governance_blocker")],
        "code_blockers": [name for name, payload in layers.items() if payload.get("code_blocker")],
    }


def _merge_path_fingerprints(paths: tuple[Path, ...]) -> list[dict[str, Any]]:
    return [_path_fingerprint(path) for path in paths]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _build_observe_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# AI_OS Observe Spine Runner",
        "",
        f"- observe_loop_status: `{summary.get('observe_loop_status')}`",
        f"- p2_bridge_status: `{summary.get('p2_bridge_status')}`",
        f"- queue_gate_status: `{summary.get('queue_gate_status')}`",
        f"- runtime_apply_status: `{summary.get('runtime_apply_status')}`",
        f"- sos_status: `{summary.get('sos_status')}`",
        f"- scheduler_status: `{summary.get('scheduler_status')}`",
        "",
        "## Layer status",
    ]

    for name, payload in report.get("layers", {}).items():
        lines.append(
            f"- {name}: status={payload.get('status')} "
            f"stale={payload.get('stale')} real={payload.get('real_blocker')} "
            f"governance={payload.get('governance_blocker')} code={payload.get('code_blocker')}"
        )

    lines.extend(
        [
            "",
            "## Mutation boundaries",
            "- queue_mutation: false",
            "- worker_inbox_mutation: false",
            "- approval_inbox_mutation: false",
            "- command_queue_mutation: false",
            "- runtime_launch: false",
            "- runtime_execution: false",
            "- scheduler_registration: false",
            "- sos_notification: false",
            "- trading_execution: false",
            f"- safe_next_action: {summary.get('safe_next_action')}",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_closure_markdown(closure_report: dict[str, Any], layers: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# AI_OS Autonomy Closure Report",
        "",
        f"- observe_loop_status: `{closure_report.get('observe_loop_status')}`",
        f"- stale_layers: `{closure_report.get('stale_layers', [])}`",
        f"- real_blockers: `{closure_report.get('real_blockers', [])}`",
        f"- governance_blockers: `{closure_report.get('governance_blockers', [])}`",
        f"- code_blockers: `{closure_report.get('code_blockers', [])}`",
        "",
        "## Layer status",
    ]

    for name, status in closure_report.get("layer_statuses", {}).items():
        payload = layers.get(name, {})
        lines.append(
            f"- {name}: status={status} "
            f"stale={payload.get('stale')} real={payload.get('real_blocker')} "
            f"governance={payload.get('governance_blocker')} code={payload.get('code_blocker')}"
        )
    return "\n".join(lines) + "\n"


def _build_observe_spine_report(
    *,
    repo_root: str | Path = ".",
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    now_value = _now(now)
    supplied = evidence or {}

    p2_mod = _load_module("aios_p2_enqueue_bridge", root / P2_BRIDGE_PATH)
    queue_mod = _load_module("aios_queue_mutation_gate", root / QUEUE_GATE_PATH)
    runtime_mod = _load_module("aios_runtime_apply_lane_preview", root / RUNTIME_APPLY_PATH)
    sos_mod = _load_module("aios_sos_arming_preview", root / SOS_PREVIEW_PATH)
    scheduler_mod = _load_module("aios_scheduler_registration_preview", root / SCHEDULER_PREVIEW_PATH)

    p2_report = _maybe_dict(supplied.get("p2_bridge") or supplied.get("p2_bridge_report"))
    if not p2_report:
        p2_report = p2_mod.build_p2_enqueue_bridge_report(
            repo_root=root,
            now=now_value,
            evidence=_compact_dict(
                human_gate_report=_maybe_dict(supplied.get("human_gate") or supplied.get("human_gate_report")),
                autonomy_gap_report=_maybe_dict(supplied.get("autonomy_gap") or supplied.get("autonomy_gap_report")),
            ),
        )

    queue_report = _maybe_dict(supplied.get("queue_mutation_gate") or supplied.get("queue_mutation_gate_report"))
    if not queue_report:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as handle:
            handle.write(json.dumps(p2_report, indent=2, sort_keys=True))
            temp_p2_path = Path(handle.name)
        try:
            queue_report = queue_mod.build_queue_mutation_gate_preview(
                repo_root=root,
                proposed_item_path=temp_p2_path,
                now=now_value,
            )
        finally:
            if temp_p2_path.exists():
                temp_p2_path.unlink()

    runtime_report = _maybe_dict(supplied.get("runtime_apply") or supplied.get("runtime_apply_report"))
    if not runtime_report:
        runtime_report = runtime_mod.build_runtime_apply_lane_report(
            repo_root=root,
            p2_preview=p2_report,
            queue_mutation_gate_preview=queue_report,
            runtime_proof_gate=_maybe_dict(supplied.get("runtime_proof_gate") or supplied.get("runtime_proof_gate_report")),
            now=now_value,
        )

    sos_report = _maybe_dict(supplied.get("sos_arming") or supplied.get("sos_preview") or supplied.get("sos_arming_report"))
    if not sos_report:
        sos_report = sos_mod.build_sos_arming_preview(
            repo_root=root,
            now=now_value,
            evidence=_compact_dict(
                p2_bridge_report=p2_report,
                queue_mutation_report=queue_report,
                human_gate_report=_maybe_dict(supplied.get("human_gate") or supplied.get("human_gate_report")),
                autonomy_gap_report=_maybe_dict(supplied.get("autonomy_gap") or supplied.get("autonomy_gap_report")),
                runtime_apply_report=runtime_report,
            ),
        )

    scheduler_report = _maybe_dict(supplied.get("scheduler_registration") or supplied.get("scheduler_registration_report"))
    if not scheduler_report:
        scheduler_report = scheduler_mod.build_scheduler_registration_preview(
            repo_root=root,
            now=now_value,
            evidence=_compact_dict(
                queue_mutation_gate=queue_report,
                runtime_apply=runtime_report,
                sos_preview=sos_report,
                human_gate=_maybe_dict(supplied.get("human_gate") or supplied.get("human_gate_report")),
                autonomy_gap=_maybe_dict(supplied.get("autonomy_gap") or supplied.get("autonomy_gap_report")),
            ),
        )

    p2_status = _normalize_status(p2_report.get("bridge_status"))
    queue_status = _normalize_status(queue_report.get("gate_status"))
    runtime_status = _normalize_status(runtime_report.get("apply_status"))
    sos_status = _normalize_status(sos_report.get("sos_status"))
    scheduler_status = _normalize_status(scheduler_report.get("scheduler_status"))

    layers = {
        "p2_bridge": _classify_layer("p2_bridge", p2_status, p2_report),
        "queue_mutation_gate": _classify_layer("queue_mutation_gate", queue_status, queue_report),
        "runtime_apply_lane": _classify_layer("runtime_apply_lane", runtime_status, runtime_report),
        "sos_arming": _classify_layer("sos_arming", sos_status, sos_report),
        "scheduler_registration": _classify_layer("scheduler_registration", scheduler_status, scheduler_report),
    }

    closure = _collect_layer_statuses(layers)
    closure["p2_bridge_status"] = p2_status
    closure["queue_mutation_gate_status"] = queue_status
    closure["runtime_apply_status"] = runtime_status
    closure["sos_status"] = sos_status
    closure["scheduler_status"] = scheduler_status
    closure["layer_statuses"] = {
        "p2_bridge": p2_status,
        "queue_mutation_gate": queue_status,
        "runtime_apply_lane": runtime_status,
        "sos_arming": sos_status,
        "scheduler_registration": scheduler_status,
    }

    if any(status == LAYER_INVALID for status in closure["layer_statuses"].values()):
        observe_loop_status = INVALID
    elif any(status == LAYER_BLOCKED for status in closure["layer_statuses"].values()):
        observe_loop_status = BLOCKED
    elif all(_is_ready_status(status) for status in closure["layer_statuses"].values()):
        observe_loop_status = READY
    else:
        observe_loop_status = BLOCKED

    safe_next_action = {
        INVALID: "Resolve stale/invalid evidence and rerun observe-spine runner.",
        BLOCKED: "Resolve real/gateway blockers and rerun observe-spine runner.",
        READY: "Continue observe-only loop checks with current evidence.",
    }.get(observe_loop_status, "Continue observe-only loop checks.")

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at_utc": now_value,
        "repo_root": root.as_posix(),
        "observe_loop_status": observe_loop_status,
        "evidence": {
            "p2_bridge": p2_report,
            "queue_mutation_gate": queue_report,
            "runtime_apply": runtime_report,
            "sos_arming": sos_report,
            "scheduler_registration": scheduler_report,
        },
        "path_fingerprints": {
            "snapshot": _merge_path_fingerprints(PROTECTED_PATHS),
        },
        "layers": layers,
        "mutation_projection": {
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "runtime_launch": False,
            "runtime_execution": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
        },
        "validate_mutation_boundaries": {
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "runtime_launch": False,
            "runtime_execution": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
        },
        "closure": closure,
        "safe_next_action": safe_next_action,
        "summary": {
            "observe_loop_status": observe_loop_status,
            "p2_bridge_status": p2_status,
            "queue_gate_status": queue_status,
            "runtime_apply_status": runtime_status,
            "sos_status": sos_status,
            "scheduler_status": scheduler_status,
            "stale_layers": closure["stale_layers"],
            "real_blockers": closure["real_blockers"],
            "governance_blockers": closure["governance_blockers"],
            "code_blockers": closure["code_blockers"],
            "safe_next_action": safe_next_action,
        },
    }


def _write_autonomy_closure_report(report: dict[str, Any], output_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(report.get("repo_root", "."))
    out_dir = Path(output_dir) if output_dir is not None else root / CLOSURE_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    closure = build_autonomy_closure_report(report=report)
    json_path = out_dir / CLOSURE_JSON_NAME
    md_path = out_dir / CLOSURE_MD_NAME
    _write_json(json_path, closure)
    _write_text(md_path, _build_closure_markdown(closure, _ensure_dict(report.get("layers"))))
    closure["report_paths"] = [json_path.as_posix(), md_path.as_posix()]
    closure["observe_loop_report_path"] = report.get("report_paths", [None])[0]
    return closure


def build_autonomy_closure_report(*, report: dict[str, Any]) -> dict[str, Any]:
    closure = _ensure_dict(report.get("closure"))
    layers = _ensure_dict(report.get("layers"))

    return {
        "schema": "AIOS_AUTONOMY_CLOSURE_REPORT.v1",
        "mode": MODE,
        "generated_at_utc": _now(),
        "observe_loop_status": report.get("observe_loop_status"),
        "ready_layers": [name for name, payload in layers.items() if _is_ready_status(payload.get("status", ""))],
        "blocked_layers": [name for name, payload in layers.items() if payload.get("status") in {BLOCKED, INVALID}],
        "stale_layers": closure.get("stale_layers", []),
        "real_blockers": closure.get("real_blockers", []),
        "governance_blockers": closure.get("governance_blockers", []),
        "code_blockers": closure.get("code_blockers", []),
        "safe_next_action": report.get("safe_next_action"),
        "validate_mutation_boundaries": {
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "runtime_launch": False,
            "runtime_execution": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
        },
        "closure_layer_statuses": closure.get("layer_statuses", {}),
    }


def build_observe_spine_report(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = _build_observe_spine_report(repo_root=repo_root, now=now, evidence=evidence)
    out_dir = Path(output_dir) if output_dir is not None else Path(repo_root) / REPORT_DIR
    if not out_dir.is_absolute():
        out_dir = Path(repo_root) / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / REPORT_JSON_NAME
    md_path = out_dir / REPORT_MD_NAME
    _write_json(report_path, report)
    _write_text(md_path, _build_observe_markdown(report))
    report["report_paths"] = [report_path.as_posix(), md_path.as_posix()]
    report["autonomy_closure"] = _write_autonomy_closure_report(report=report, output_dir=None)
    report["autonomy_closure"]["observe_loop_report_path"] = report["report_paths"][0]
    return report


def run_observe_spine_runner(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    closure_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
    write_reports: bool = True,
) -> dict[str, Any]:
    report = _build_observe_spine_report(repo_root=repo_root, now=now, evidence=evidence)
    if write_reports:
        report_root = Path(repo_root)
        out_dir = Path(output_dir) if output_dir is not None else report_root / REPORT_DIR
        if not out_dir.is_absolute():
            out_dir = report_root / out_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path = out_dir / REPORT_JSON_NAME
        md_path = out_dir / REPORT_MD_NAME
        _write_json(report_path, report)
        _write_text(md_path, _build_observe_markdown(report))
        report["report_paths"] = [report_path.as_posix(), md_path.as_posix()]

        report["autonomy_closure"] = _write_autonomy_closure_report(report=report, output_dir=closure_dir)
        report["autonomy_closure"]["observe_loop_report_path"] = report["report_paths"][0]
    return report


def _cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a DRY_RUN observe-only control loop report.")
    parser.add_argument("--repo-root", default=".", help="Repository root to read evidence from.")
    parser.add_argument("--output-dir", default=None, help="Output directory for observe-loop report.")
    parser.add_argument("--closure-dir", default=None, help="Output directory for autonomy closure report.")
    parser.add_argument("--now", default=None, help="Optional UTC timestamp override.")
    parser.add_argument("--no-write", action="store_true", help="Build report without writing files.")
    return parser.parse_args()


def main() -> int:
    args = _cli()
    report = run_observe_spine_runner(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        closure_dir=args.closure_dir,
        now=args.now,
        write_reports=not args.no_write,
    )
    print(json.dumps(report.get("summary", {}), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
