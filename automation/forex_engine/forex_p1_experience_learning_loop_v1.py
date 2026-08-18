"""Governed PAPER/shadow experience ledger and transparent learning summaries.

Analysis-only: it never edits production configuration, calls a broker, opens
positions, or credits shadow outcomes to canonical PAPER evidence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA = "AIOS_FOREX_P1_EXPERIENCE_EVENT.v1"
LEDGER_FILENAME = "AIOS_FOREX_P1_EXPERIENCE_LEDGER.jsonl"
CSV_FILENAME = "AIOS_FOREX_P1_EXPERIENCE_LEDGER.csv"
SAFETY = {"paper_only": True, "shadow_not_executed": True, "production_mutation_allowed": False,
          "broker_write_performed": False, "practice_order_performed": False,
          "live_trade_performed": False, "money_movement_performed": False}
_SECRET_PARTS = ("token", "credential", "account", "password", "secret", "payload", "order", "transaction")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def config_hash(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(stable_json(dict(config)).encode()).hexdigest()


def dataset_hash(identity: Mapping[str, Any] | str) -> str:
    value = identity if isinstance(identity, str) else stable_json(dict(identity))
    return hashlib.sha256(value.encode()).hexdigest()


def _sanitize(value: Any, key: str = "") -> Any:
    if any(part in key.lower() for part in _SECRET_PARTS):
        return None
    if isinstance(value, Mapping):
        return {str(k): _sanitize(v, str(k)) for k, v in value.items()
                if not any(part in str(k).lower() for part in _SECRET_PARTS)}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def classify_experience(*, production_decision: str, outcome_r: float | None) -> str:
    if outcome_r is None:
        return "UNRESOLVED"
    if outcome_r == 0:
        return "BREAKEVEN"
    accepted = production_decision in {"ACCEPTED", "PAPER_ELIGIBLE", "PAPER_SESSION_OPEN"}
    return ("TRUE_POSITIVE" if outcome_r > 0 else "FALSE_POSITIVE") if accepted else ("FALSE_NEGATIVE" if outcome_r > 0 else "TRUE_NEGATIVE")


def build_experience_event(*, experience_id: str, event_type: str, strategy_name: str,
                           strategy_config: Mapping[str, Any], git_commit: str,
                           dataset_identity: Mapping[str, Any] | str, decision_utc: str,
                           production_decision: str, shadow_classification: str,
                           outcome_r: float | None = None, instrument: str = "EUR_USD",
                           timeframe: str = "M5", features: Mapping[str, Any] | None = None,
                           outcome: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if shadow_classification not in {"ACTUAL_PAPER", "SHADOW_COUNTERFACTUAL"}:
        raise ValueError("experience_source_invalid")
    return _sanitize({
        "schema": SCHEMA, "experience_id": str(experience_id), "event_type": event_type,
        "strategy_name": strategy_name, "strategy_config": dict(strategy_config),
        "strategy_config_hash": config_hash(strategy_config), "git_commit": git_commit,
        "dataset_hash": dataset_hash(dataset_identity), "instrument": instrument,
        "timeframe": timeframe, "decision_utc": decision_utc,
        "production_decision": production_decision, "shadow_classification": shadow_classification,
        "outcome_classification": classify_experience(production_decision=production_decision, outcome_r=outcome_r),
        "features": dict(features or {}), "outcome": dict(outcome or {}), "outcome_r": outcome_r,
        "safety": dict(SAFETY),
    })


def experience_from_shadow_candidate(candidate: Mapping[str, Any], *, strategy_config: Mapping[str, Any], git_commit: str,
                                     dataset_identity: Mapping[str, Any] | str, decision_utc: str) -> dict[str, Any]:
    """Adapt the existing shadow audit output without changing its accounting."""
    counterfactual = candidate.get("counterfactual") if isinstance(candidate.get("counterfactual"), Mapping) else {}
    return build_experience_event(
        experience_id=str(candidate.get("shadow_candidate_id", "shadow-unknown")), event_type="SHADOW_OUTCOME",
        strategy_name=str(candidate.get("strategy_name", "supertrend_pullback_v1")), strategy_config=strategy_config,
        git_commit=git_commit, dataset_identity=dataset_identity, decision_utc=decision_utc,
        production_decision="REJECTED", shadow_classification="SHADOW_COUNTERFACTUAL",
        outcome_r=counterfactual.get("hypothetical_r"), features={"first_failed_gate": candidate.get("first_failed_gate"), **dict(candidate.get("features") or {})},
        outcome=dict(counterfactual),
    )


def append_experience_event(path: Path, event: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(_sanitize(dict(event)), sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8", newline="") as stream:
        stream.write(line); stream.flush(); os.fsync(stream.fileno())


def read_experience_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or value.get("schema") != SCHEMA:
            raise ValueError(f"experience_ledger_line_invalid_{number}")
        records.append(value)
    return records


def export_csv(records: Iterable[Mapping[str, Any]], path: Path) -> None:
    rows = [{key: record.get(key) for key in ("experience_id", "decision_utc", "shadow_classification", "production_decision", "outcome_classification", "outcome_r", "strategy_config_hash", "dataset_hash")} for record in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["experience_id"])
        writer.writeheader(); writer.writerows(rows)


def filter_value_scorecard(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("shadow_classification") == "SHADOW_COUNTERFACTUAL":
            groups[str(record.get("features", {}).get("first_failed_gate") or "unattributed")].append(record)
    result = {}
    for gate, items in sorted(groups.items()):
        resolved = [item for item in items if item.get("outcome_r") is not None]
        wins = [item for item in resolved if float(item["outcome_r"]) > 0]
        losses = [item for item in resolved if float(item["outcome_r"]) < 0]
        result[gate] = {"total_rejections": len(items), "resolved": len(resolved), "would_win": len(wins), "would_lose": len(losses),
                        "ambiguous_or_unresolved": len(items) - len(resolved), "false_negative_rate": round(len(wins) / len(resolved), 8) if resolved else None,
                        "shadow_expectancy_r": round(sum(float(item["outcome_r"]) for item in resolved) / len(resolved), 8) if resolved else None,
                        "saved_loss_r": round(-sum(float(item["outcome_r"]) for item in losses), 8), "regret_r": round(sum(float(item["outcome_r"]) for item in wins), 8)}
    return result


def near_threshold_bucket(distance_percent: float | None) -> str:
    if distance_percent is None:
        return "NOT_EVALUATED"
    value = abs(float(distance_percent))
    return "0_5_PERCENT" if value <= 5 else "5_10_PERCENT" if value <= 10 else "10_20_PERCENT" if value <= 20 else "OVER_20_PERCENT"


def walk_forward_scorecard(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(records, key=lambda item: str(item.get("decision_utc", "")))
    first, second = int(len(ordered) * .6), int(len(ordered) * .8)
    result = {}
    for name, segment in (("TRAIN", ordered[:first]), ("VALIDATION", ordered[first:second]), ("TEST", ordered[second:])):
        values = [float(item["outcome_r"]) for item in segment if item.get("outcome_r") is not None]
        result[name] = {"count": len(segment), "resolved": len(values), "expectancy_r": round(sum(values) / len(values), 8) if values else None}
    return {"split": "chronological_60_20_20", "segments": result, "selection_uses_test": False}


def similarity_bucket(features: Mapping[str, Any]) -> str:
    return "|".join(str(features.get(key, "UNKNOWN")) for key in ("volatility_regime", "session_bucket", "supertrend_age_bucket", "spread_risk_bucket"))


def postmortem_learning_summary(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Keep actual PAPER and counterfactual metrics explicitly separate."""
    actual = [dict(r) for r in records if r.get("shadow_classification") == "ACTUAL_PAPER"]
    shadow = [dict(r) for r in records if r.get("shadow_classification") == "SHADOW_COUNTERFACTUAL"]
    return {"ACTUAL_PAPER": {"count": len(actual), "events": actual}, "COUNTERFACTUAL": {"count": len(shadow), "events": shadow}, "mixed_accounting": False}
