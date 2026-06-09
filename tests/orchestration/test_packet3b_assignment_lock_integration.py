from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ASSIGN_SCRIPT = REPO_ROOT / "automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1"
CLAIM_SCRIPT = REPO_ROOT / "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1"


def packet_runtime_payload(*, assigned_worker_id: str | None = None, allowed_paths: list[str] | None = None) -> dict[str, object]:
    return {
        "generated_at": "2026-06-08T00:00:00Z",
        "packets": [
            {
                "packet_id": "packet-3b-test",
                "status": "QUEUED",
                "mode": "DRY_RUN",
                "approval_required": True,
                "apply_allowed": False,
                "assigned_worker_id": assigned_worker_id,
                "allowed_paths": allowed_paths if allowed_paths is not None else ["automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1"],
                "lane": "packet3b-test",
            }
        ],
    }


def registry_payload(*, locks: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schema": "AIOS_FILE_LOCK_REGISTRY.v1",
        "system": "AI_OS",
        "mode": "DRY_RUN",
        "global_blocked_paths": [".git/", "bro" + "ker/", "oa" + "nda/", "sec" + "rets/", "web" + "hooks/", "." + "env"],
        "recommended_blocked_files": ["AGENTS.md", "README.md"],
        "locks": locks or [],
    }


def active_lock(path: str, *, expires_at_utc: str = "2099-01-01T00:00:00.0000000Z") -> dict[str, object]:
    return {
        "schema": "AIOS_PACKET_LOCK.v1",
        "schema_version": "1.0.0",
        "lock_id": "existing-lock",
        "worker_id": "other-worker",
        "packet_id": "other-packet",
        "lane": "test",
        "status": "ACTIVE",
        "claimed_paths": [path],
        "created_at_utc": "2026-06-08T00:00:00.0000000Z",
        "updated_at_utc": "2026-06-08T00:00:00.0000000Z",
        "expires_at_utc": expires_at_utc,
        "release_condition": "test",
        "approval_packet_id": "approval",
        "notes": "test fixture",
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def build_runtime_fixture(tmp_path: Path, *, assigned_worker_id: str | None = None, allowed_paths: list[str] | None = None) -> tuple[Path, Path, Path]:
    packet_root = tmp_path / "packets"
    worker_root = tmp_path / "workers"
    registry = tmp_path / "locks" / "FILE_LOCK_REGISTRY.json"
    packet = packet_runtime_payload(assigned_worker_id=assigned_worker_id, allowed_paths=allowed_paths)
    write_json(packet_root / "packet_queue.json", packet)
    write_json(packet_root / "packet_runtime_table.json", packet_runtime_payload(assigned_worker_id=assigned_worker_id, allowed_paths=allowed_paths))
    write_json(packet_root / "packet_assignment_ledger.json", {"generated_at": "2026-06-08T00:00:00Z", "assignments": []})
    write_json(packet_root / "packet_status_history.json", {"generated_at": "2026-06-08T00:00:00Z", "status_events": []})
    write_json(
        worker_root / "active_worker_table.json",
        {
            "generated_at": "2026-06-08T00:00:00Z",
            "workers": [{"worker_id": "worker-3b", "current_state": "IDLE", "assigned_packet_id": None}],
        },
    )
    write_json(
        worker_root / "worker_heartbeat_table.json",
        {
            "generated_at": "2026-06-08T00:00:00Z",
            "heartbeats": [
                {
                    "worker_id": "worker-3b",
                    "current_state": "IDLE",
                    "stale_status": "CURRENT",
                    "assigned_packet_id": None,
                    "heartbeat_time": "2099-01-01T00:00:00Z",
                    "stale_after_seconds": 600,
                }
            ],
        },
    )
    write_json(registry, registry_payload())
    return packet_root, worker_root, registry


def snapshot_runtime(packet_root: Path, registry: Path) -> dict[str, str]:
    paths = [
        packet_root / "packet_queue.json",
        packet_root / "packet_runtime_table.json",
        packet_root / "packet_assignment_ledger.json",
        packet_root / "packet_status_history.json",
        registry,
    ]
    return {path.name: path.read_text(encoding="utf-8") for path in paths}


def run_assign(packet_root: Path, worker_root: Path, registry: Path, *, claim_script: Path = CLAIM_SCRIPT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ASSIGN_SCRIPT),
            "-PacketId",
            "packet-3b-test",
            "-WorkerId",
            "worker-3b",
            "-PacketRuntimeRoot",
            str(packet_root),
            "-WorkerRuntimeRoot",
            str(worker_root),
            "-LockRegistryPath",
            str(registry),
            "-ClaimScriptPath",
            str(claim_script),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_claim_stub(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_lock_claim_is_required_before_assignment_mutation(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path, allowed_paths=[])
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "allowed_paths are" in result.stderr
    assert snapshot_runtime(packet_root, registry) == before


def test_blocked_claim_leaves_assignment_files_unchanged(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path, allowed_paths=["bro" + "ker/live.json"])
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "claim_status=BLOCKED" in result.stderr
    assert snapshot_runtime(packet_root, registry) == before


def test_review_required_claim_leaves_assignment_files_unchanged(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path)
    write_json(registry, registry_payload(locks=[active_lock("automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1")]))
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "claim_status=REVIEW_REQUIRED" in result.stderr
    assert snapshot_runtime(packet_root, registry) == before


def test_malformed_and_nonzero_claim_fail_closed(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path)
    malformed = write_claim_stub(tmp_path / "malformed-claim.ps1", 'Write-Host "not-json"\n')
    nonzero = write_claim_stub(tmp_path / "nonzero-claim.ps1", 'Write-Error "claim failed"\nexit 7\n')

    before_malformed = snapshot_runtime(packet_root, registry)
    malformed_result = run_assign(packet_root, worker_root, registry, claim_script=malformed)

    assert malformed_result.returncode != 0
    assert "malformed JSON" in malformed_result.stderr
    assert snapshot_runtime(packet_root, registry) == before_malformed

    before_nonzero = snapshot_runtime(packet_root, registry)
    nonzero_result = run_assign(packet_root, worker_root, registry, claim_script=nonzero)

    assert nonzero_result.returncode != 0
    assert "exited 7" in nonzero_result.stderr
    assert snapshot_runtime(packet_root, registry) == before_nonzero


def test_successful_claim_records_exact_lock_id_in_assignment_ledger_and_status_history(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode == 0, result.stdout + result.stderr
    persisted_registry = json.loads(registry.read_text(encoding="utf-8"))
    lock_id = persisted_registry["locks"][0]["lock_id"]
    ledger = read_json(packet_root / "packet_assignment_ledger.json")
    history = read_json(packet_root / "packet_status_history.json")
    runtime = read_json(packet_root / "packet_runtime_table.json")

    assert ledger["assignments"][0]["lock_ids"] == [lock_id]
    assert history["status_events"][0]["lock_ids"] == [lock_id]
    assert runtime["packets"][0]["status"] == "ASSIGNED"
    assert f"LockId: {lock_id}" in result.stdout


def test_existing_assigned_worker_checks_still_block_before_lock_claim(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path, assigned_worker_id="worker-other")
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "already assigned" in result.stderr
    assert snapshot_runtime(packet_root, registry) == before


def test_active_lock_overlap_blocks_double_assignment(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path)
    write_json(registry, registry_payload(locks=[active_lock("automation/dispatcher/runtime/packets")]))
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "claim_status=REVIEW_REQUIRED" in result.stderr
    assert snapshot_runtime(packet_root, registry) == before


def test_stale_locks_are_review_required_and_not_auto_cleared(tmp_path: Path) -> None:
    packet_root, worker_root, registry = build_runtime_fixture(tmp_path)
    stale = active_lock("automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1", expires_at_utc="2000-01-01T00:00:00.0000000Z")
    write_json(registry, registry_payload(locks=[stale]))
    before = snapshot_runtime(packet_root, registry)

    result = run_assign(packet_root, worker_root, registry)

    assert result.returncode != 0
    assert "claim_status=REVIEW_REQUIRED" in result.stderr
    assert json.loads(registry.read_text(encoding="utf-8"))["locks"][0]["lock_id"] == "existing-lock"
    assert snapshot_runtime(packet_root, registry) == before


def test_no_out_of_scope_runtime_activation_terms_appear_in_assignment_script() -> None:
    lowered = ASSIGN_SCRIPT.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "start-" + "sched" + "uler",
        "invoke-aiosnightcycle",
        "send-" + "s" + "os",
        "ad" + "b ",
        "tele" + "gram",
        "oa" + "nda",
        "live " + "trading enabled",
        "web" + "hook",
        "print " + "sec" + "ret",
        "." + "env",
    ]
    for term in forbidden_terms:
        assert term not in lowered
