"""AI_OS packet and task risk classifier for DRY_RUN synthesis.

This module classifies text, mode, and path signals only. It performs no file
writes, child process launches, network calls, runtime mutation, packet state
movement, approval mutation, worker launch, scheduling, or repository actions.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from decision_vocabulary import normalize_status


REPORT_ONLY = "report_only"
LOW_RISK = "low_risk"
PROTECTED = "protected"
RUNTIME_SENSITIVE = "runtime_sensitive"
GOVERNANCE_SENSITIVE = "governance_sensitive"
MUTATION_SENSITIVE = "mutation_sensitive"
OVERNIGHT_SAFE = "overnight_safe"
BLOCKED = "blocked"

RISK_CLASSES = (
    REPORT_ONLY,
    LOW_RISK,
    PROTECTED,
    RUNTIME_SENSITIVE,
    GOVERNANCE_SENSITIVE,
    MUTATION_SENSITIVE,
    OVERNIGHT_SAFE,
    BLOCKED,
)

BLOCKED_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "api key",
    "api keys",
    "private key",
    "broker",
    "oanda",
    "live trading",
    "real order",
    "real orders",
    "force push",
    "runtime mutation",
    "scheduler mutation without approval",
    "packet movement without approval",
    "approval mutation without approval",
)

RUNTIME_PATHS = (
    "services/runtime",
    "services/dispatcher",
    "automation/orchestration/runtime",
)

GOVERNANCE_PATHS = (
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "docs/governance",
    "docs/workflows",
    "RISK_POLICY.md",
    "ARCHITECTURE.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "AAR.md",
    "DAILY_REPORT.md",
)

MUTATION_TERMS = (
    "apply",
    "file write",
    "file writes",
    "commit",
    "push",
    "merge",
    "stage files",
    "packet movement",
    "move packet",
    "approval mutation",
    "update approval",
    "worker launch",
    "launch worker",
)

OVERNIGHT_SAFE_TERMS = (
    "dry_run",
    "dry run",
    "report only",
    "read-only",
    "read only",
    "no mutation",
    "no scheduler change",
    "no runtime change",
    "no packet movement",
    "no commit",
    "no push",
)

LOW_RISK_PATH_PREFIXES = (
    "docs/",
    "schemas/aios/orchestration/",
    "services/python_supervisor/",
)


def _normalize_path(path: str) -> str:
    return str(path).replace("\\", "/").strip()


def _contains_any(text: str, signals: tuple[str, ...]) -> list[str]:
    return [signal for signal in signals if signal.lower() in text]


def _is_negated_signal(text: str, signal: str) -> bool:
    safe_prefixes = ("no ", "without ", "do not ", "don't ")
    lowered_signal = signal.lower()
    return any(f"{prefix}{lowered_signal}" in text for prefix in safe_prefixes)


def _contains_unnegated_any(text: str, signals: tuple[str, ...]) -> list[str]:
    return [
        signal
        for signal in signals
        if signal.lower() in text and not _is_negated_signal(text, signal)
    ]


def _path_starts_with(path: str, prefix: str) -> bool:
    normalized_path = _normalize_path(path).lower()
    normalized_prefix = _normalize_path(prefix).lower().rstrip("/")
    return normalized_path == normalized_prefix or normalized_path.startswith(f"{normalized_prefix}/")


def _collect_path_matches(paths: list[str], prefixes: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for path in paths:
        for prefix in prefixes:
            if _path_starts_with(path, prefix):
                matches.append(path)
                break
    return sorted(set(matches))


def classify_packet_risk(
    text: str = "",
    paths: list[str] | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    path_list = [_normalize_path(path) for path in (paths or [])]
    combined_text = " ".join([text or "", mode or "", " ".join(path_list)]).lower()
    normalized_mode = str(mode or "").strip().upper()

    blocked_signals = _contains_any(combined_text, BLOCKED_TERMS)
    runtime_paths = _collect_path_matches(path_list, RUNTIME_PATHS)
    governance_paths = _collect_path_matches(path_list, GOVERNANCE_PATHS)
    mutation_signals = _contains_unnegated_any(combined_text, MUTATION_TERMS)
    overnight_safe_signals = _contains_any(combined_text, OVERNIGHT_SAFE_TERMS)
    low_risk_paths = _collect_path_matches(path_list, LOW_RISK_PATH_PREFIXES)

    classes: list[str] = []
    if blocked_signals:
        classes.append(BLOCKED)
    if runtime_paths:
        classes.append(RUNTIME_SENSITIVE)
    if governance_paths:
        classes.append(GOVERNANCE_SENSITIVE)
    if mutation_signals or normalized_mode == "APPLY":
        classes.append(MUTATION_SENSITIVE)
    if overnight_safe_signals and not blocked_signals and normalized_mode != "APPLY":
        classes.append(OVERNIGHT_SAFE)
    if "report only" in combined_text or "read-only" in combined_text or "read only" in combined_text:
        classes.append(REPORT_ONLY)
    if low_risk_paths and not runtime_paths and not governance_paths and not blocked_signals:
        classes.append(LOW_RISK)
    if governance_paths or runtime_paths:
        classes.append(PROTECTED)

    if not classes:
        classes.append(REPORT_ONLY if normalized_mode == "DRY_RUN" else LOW_RISK)

    classes = sorted(set(classes), key=RISK_CLASSES.index)
    primary_class = BLOCKED if BLOCKED in classes else classes[-1]
    approval_required = any(
        item in classes
        for item in (
            PROTECTED,
            RUNTIME_SENSITIVE,
            GOVERNANCE_SENSITIVE,
            MUTATION_SENSITIVE,
            BLOCKED,
        )
    )
    safe_unattended = (
        BLOCKED not in classes
        and MUTATION_SENSITIVE not in classes
        and RUNTIME_SENSITIVE not in classes
        and normalized_mode != "APPLY"
        and (OVERNIGHT_SAFE in classes or REPORT_ONLY in classes)
    )

    return {
        "schema": "AIOS_PACKET_RISK_CLASSIFICATION.v1",
        "status": normalize_status("BLOCKED" if BLOCKED in classes else ("REVIEW" if approval_required else "PASS")),
        "primary_class": primary_class,
        "classes": classes,
        "safe_for_unattended_dry_run": safe_unattended,
        "requires_human_approval": approval_required,
        "signals": {
            "blocked": blocked_signals,
            "runtime_paths": runtime_paths,
            "governance_paths": governance_paths,
            "mutation": mutation_signals,
            "overnight_safe": overnight_safe_signals,
            "low_risk_paths": low_risk_paths,
        },
        "blocked_capabilities": [
            "autonomous_apply",
            "packet_movement",
            "approval_mutation",
            "worker_launch",
            "runtime_mutation",
            "scheduler_mutation",
        ],
    }


def is_safe_for_unattended_dry_run(classification: dict[str, Any]) -> bool:
    return bool(classification.get("safe_for_unattended_dry_run"))


def requires_human_approval(classification: dict[str, Any]) -> bool:
    return bool(classification.get("requires_human_approval"))


def summarize_risk_classes(items: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {risk_class: 0 for risk_class in RISK_CLASSES}
    safe_count = 0
    approval_count = 0
    for item in items:
        for risk_class in item.get("classes", []):
            counts[risk_class] = counts.get(risk_class, 0) + 1
        if is_safe_for_unattended_dry_run(item):
            safe_count += 1
        if requires_human_approval(item):
            approval_count += 1

    return {
        "schema": "AIOS_PACKET_RISK_SUMMARY.v1",
        "item_count": len(items),
        "class_counts": counts,
        "safe_for_unattended_dry_run_count": safe_count,
        "human_approval_required_count": approval_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a sample AI_OS packet risk classification.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = [
        classify_packet_risk(
            text="DRY_RUN report only, no mutation, no packet movement, no commit, no push",
            paths=["services/python_supervisor/evidence_manifest.py"],
            mode="DRY_RUN",
        ),
        classify_packet_risk(
            text="APPLY runtime mutation request",
            paths=["services/runtime/runtimeBootstrap.js"],
            mode="APPLY",
        ),
    ]
    output = {
        "schema": "AIOS_PACKET_RISK_CLASSIFIER_PREVIEW.v1",
        "risk_classes": list(RISK_CLASSES),
        "samples": samples,
        "summary": summarize_risk_classes(samples),
    }
    print(json.dumps(output, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
