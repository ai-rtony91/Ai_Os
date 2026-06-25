"""Local-only AIOS Forex Expectancy Strength Router V1.

This module classifies expectancy evidence for a strategy proof candidate. It
does not call brokers, read credentials, read .env files, use network access,
place orders, approve real money, approve compounding, or move money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Mapping

from automation.forex_engine.strategy_proof_engine_v1 import (
    StrategyProofCandidate,
    build_sample_all_blocked_strategy_evidence,
    build_sample_mixed_strategy_evidence,
    evaluate_strategy_proof_engine,
)


EXPECTANCY_STRENGTH_ROUTER_VERSION = "expectancy_strength_router_v1"

EXPECTANCY_STRONG = "EXPECTANCY_STRONG"
EXPECTANCY_PROMISING = "EXPECTANCY_PROMISING"
EXPECTANCY_WEAK = "EXPECTANCY_WEAK"
EXPECTANCY_BLOCKED = "EXPECTANCY_BLOCKED"
EXPECTANCY_UNKNOWN = "EXPECTANCY_UNKNOWN"

VALID_EXPECTANCY_CLASSIFICATIONS = {
    EXPECTANCY_STRONG,
    EXPECTANCY_PROMISING,
    EXPECTANCY_WEAK,
    EXPECTANCY_BLOCKED,
    EXPECTANCY_UNKNOWN,
}


@dataclass(frozen=True)
class ExpectancyStrengthConfig:
    strong_expectancy: Decimal | str | int | float = Decimal("0.45")
    promising_expectancy: Decimal | str | int | float = Decimal("0.20")
    weak_expectancy: Decimal | str | int | float = Decimal("0.01")
    strong_sample_size: int = 60
    minimum_sample_size: int = 30
    strong_profit_factor: Decimal | str | int | float = Decimal("1.70")
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_strong_drawdown: Decimal | str | int | float = Decimal("0.025")
    maximum_acceptable_drawdown: Decimal | str | int | float = Decimal("0.050")

    def __post_init__(self) -> None:
        object.__setattr__(self, "strong_expectancy", _to_decimal(self.strong_expectancy))
        object.__setattr__(
            self, "promising_expectancy", _to_decimal(self.promising_expectancy)
        )
        object.__setattr__(self, "weak_expectancy", _to_decimal(self.weak_expectancy))
        object.__setattr__(self, "strong_sample_size", int(self.strong_sample_size))
        object.__setattr__(self, "minimum_sample_size", int(self.minimum_sample_size))
        object.__setattr__(
            self, "strong_profit_factor", _to_decimal(self.strong_profit_factor)
        )
        object.__setattr__(
            self, "minimum_profit_factor", _to_decimal(self.minimum_profit_factor)
        )
        object.__setattr__(
            self, "maximum_strong_drawdown", _to_decimal(self.maximum_strong_drawdown)
        )
        object.__setattr__(
            self,
            "maximum_acceptable_drawdown",
            _to_decimal(self.maximum_acceptable_drawdown),
        )


@dataclass(frozen=True)
class ExpectancyStrengthInput:
    strategy_id: str = "UNKNOWN"
    strategy_name: str = "UNKNOWN"
    expectancy: Decimal | str | int | float | None = None
    total_trades: int | str | None = None
    profit_factor: Decimal | str | int | float | None = None
    max_drawdown: Decimal | str | int | float | None = None
    win_rate: Decimal | str | int | float | None = None
    proof_score: Decimal | str | int | float | None = None

    @classmethod
    def from_candidate(cls, candidate: StrategyProofCandidate) -> "ExpectancyStrengthInput":
        return cls(
            strategy_id=candidate.strategy_id,
            strategy_name=candidate.strategy_name,
            expectancy=candidate.expectancy,
            total_trades=candidate.total_trades,
            profit_factor=candidate.profit_factor,
            max_drawdown=candidate.max_drawdown,
            win_rate=candidate.win_rate,
            proof_score=candidate.proof_score,
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ExpectancyStrengthInput":
        return cls(
            strategy_id=str(raw.get("strategy_id", raw.get("candidate_id", "UNKNOWN"))),
            strategy_name=str(raw.get("strategy_name", "UNKNOWN")),
            expectancy=raw.get("expectancy"),
            total_trades=raw.get("total_trades"),
            profit_factor=raw.get("profit_factor"),
            max_drawdown=raw.get("max_drawdown"),
            win_rate=raw.get("win_rate"),
            proof_score=raw.get("proof_score"),
        )


@dataclass(frozen=True)
class ExpectancyStrengthResult:
    router_version: str
    expectancy_status: str
    strategy_id: str
    strategy_name: str
    expectancy: Decimal | None
    total_trades: int | None
    profit_factor: Decimal | None
    max_drawdown: Decimal | None
    win_rate: Decimal | None
    proof_score: Decimal | None
    money_path_signal: str
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    demo_trade_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    permissions: Mapping[str, bool]

    def __post_init__(self) -> None:
        if self.expectancy_status not in VALID_EXPECTANCY_CLASSIFICATIONS:
            raise ValueError(f"invalid expectancy status: {self.expectancy_status}")


def build_sample_mixed_expectancy_input() -> ExpectancyStrengthInput:
    result = evaluate_strategy_proof_engine(build_sample_mixed_strategy_evidence())
    if result.top_strategy is None:
        return ExpectancyStrengthInput()
    return ExpectancyStrengthInput.from_candidate(result.top_strategy)


def build_sample_blocked_expectancy_input() -> ExpectancyStrengthInput:
    result = evaluate_strategy_proof_engine(build_sample_all_blocked_strategy_evidence())
    if result.top_strategy is None:
        return ExpectancyStrengthInput()
    return ExpectancyStrengthInput.from_candidate(result.top_strategy)


def route_expectancy_strength(
    evidence: ExpectancyStrengthInput | StrategyProofCandidate | Mapping[str, Any] | None = None,
    config: ExpectancyStrengthConfig | Mapping[str, Any] | None = None,
) -> ExpectancyStrengthResult:
    active_config = _coerce_config(config)
    normalized = _normalize_input(_coerce_input(evidence), active_config)
    passed, failed = _check_expectancy_inputs(normalized, active_config)
    status = _classify_expectancy(normalized, active_config, failed)
    blockers = _blockers(status, failed)

    return ExpectancyStrengthResult(
        router_version=EXPECTANCY_STRENGTH_ROUTER_VERSION,
        expectancy_status=status,
        strategy_id=normalized["strategy_id"],
        strategy_name=normalized["strategy_name"],
        expectancy=normalized["expectancy"],
        total_trades=normalized["total_trades"],
        profit_factor=normalized["profit_factor"],
        max_drawdown=normalized["max_drawdown"],
        win_rate=normalized["win_rate"],
        proof_score=normalized["proof_score"],
        money_path_signal=_money_path_signal(status),
        passed_checks=tuple(passed),
        failed_checks=tuple(failed),
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(status),
        demo_trade_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        permissions=_permissions(),
    )


def result_to_operator_text(result: ExpectancyStrengthResult | None = None) -> str:
    active = result if result is not None else route_expectancy_strength()
    lines = [
        "AIOS Forex Expectancy Strength Router V1",
        f"expectancy_status: {active.expectancy_status}",
        f"strategy_id: {active.strategy_id}",
        f"expectancy: {_json_value(active.expectancy)}",
        f"profit_factor: {_json_value(active.profit_factor)}",
        f"max_drawdown: {_json_value(active.max_drawdown)}",
        f"sample_depth: {_json_value(active.total_trades)}",
        f"money_path_signal: {active.money_path_signal}",
        f"demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        "failed_checks:",
    ]
    lines.extend(f"- {item}" for item in active.failed_checks or ("none",))
    lines.append(f"next_safe_action: {active.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: ExpectancyStrengthResult | None = None) -> dict[str, Any]:
    active = result if result is not None else route_expectancy_strength()
    return {
        "router_version": active.router_version,
        "expectancy_status": active.expectancy_status,
        "strategy_id": active.strategy_id,
        "strategy_name": active.strategy_name,
        "expectancy": _json_value(active.expectancy),
        "total_trades": active.total_trades,
        "profit_factor": _json_value(active.profit_factor),
        "max_drawdown": _json_value(active.max_drawdown),
        "win_rate": _json_value(active.win_rate),
        "proof_score": _json_value(active.proof_score),
        "money_path_signal": active.money_path_signal,
        "passed_checks": list(active.passed_checks),
        "failed_checks": list(active.failed_checks),
        "blockers": list(active.blockers),
        "next_safe_action": active.next_safe_action,
        "permissions": dict(active.permissions),
        "demo_trade_allowed": active.demo_trade_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "safety": {
            "local_only": True,
            "broker_calls": False,
            "network_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "order_placement": False,
            "real_money_approval": False,
            "compounding_approval": False,
            "bank_movement_approval": False,
        },
    }


def expectancy_strength_to_markdown(result: ExpectancyStrengthResult | None = None) -> str:
    active = result if result is not None else route_expectancy_strength()
    lines = [
        "# AIOS Forex Expectancy Strength Router V1",
        "",
        "## Status",
        f"- expectancy_status: {active.expectancy_status}",
        f"- strategy_id: {active.strategy_id}",
        f"- expectancy: {_json_value(active.expectancy)}",
        f"- profit_factor: {_json_value(active.profit_factor)}",
        f"- max_drawdown: {_json_value(active.max_drawdown)}",
        f"- sample_depth: {_json_value(active.total_trades)}",
        f"- money_path_signal: {active.money_path_signal}",
        "",
        "## Failed Checks",
    ]
    lines.extend(f"- {item}" for item in active.failed_checks or ("none",))
    lines.extend(
        [
            "",
            "## Safety Locks",
            f"- demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
            f"- broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
            f"- real_money_allowed: {_bool_text(active.real_money_allowed)}",
            f"- compounding_allowed: {_bool_text(active.compounding_allowed)}",
            f"- bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
            "",
            "## Next Safe Action",
            active.next_safe_action,
            "",
        ]
    )
    return "\n".join(lines)


def _coerce_config(
    raw: ExpectancyStrengthConfig | Mapping[str, Any] | None,
) -> ExpectancyStrengthConfig:
    if isinstance(raw, ExpectancyStrengthConfig):
        return raw
    if raw is None:
        return ExpectancyStrengthConfig()
    if isinstance(raw, Mapping):
        return ExpectancyStrengthConfig(
            strong_expectancy=raw.get("strong_expectancy", "0.45"),
            promising_expectancy=raw.get("promising_expectancy", "0.20"),
            weak_expectancy=raw.get("weak_expectancy", "0.01"),
            strong_sample_size=raw.get("strong_sample_size", 60),
            minimum_sample_size=raw.get("minimum_sample_size", 30),
            strong_profit_factor=raw.get("strong_profit_factor", "1.70"),
            minimum_profit_factor=raw.get("minimum_profit_factor", "1.25"),
            maximum_strong_drawdown=raw.get("maximum_strong_drawdown", "0.025"),
            maximum_acceptable_drawdown=raw.get("maximum_acceptable_drawdown", "0.050"),
        )
    raise TypeError("unsupported expectancy strength config")


def _coerce_input(
    raw: ExpectancyStrengthInput | StrategyProofCandidate | Mapping[str, Any] | None,
) -> ExpectancyStrengthInput:
    if isinstance(raw, ExpectancyStrengthInput):
        return raw
    if isinstance(raw, StrategyProofCandidate):
        return ExpectancyStrengthInput.from_candidate(raw)
    if raw is None:
        return build_sample_mixed_expectancy_input()
    if isinstance(raw, Mapping):
        return ExpectancyStrengthInput.from_mapping(raw)
    raise TypeError("unsupported expectancy strength input")


def _normalize_input(
    raw: ExpectancyStrengthInput,
    config: ExpectancyStrengthConfig,
) -> dict[str, Any]:
    return {
        "strategy_id": raw.strategy_id or "UNKNOWN",
        "strategy_name": raw.strategy_name or raw.strategy_id or "UNKNOWN",
        "expectancy": _optional_decimal(raw.expectancy),
        "total_trades": _optional_int(raw.total_trades),
        "profit_factor": _optional_decimal(raw.profit_factor),
        "max_drawdown": _optional_decimal(raw.max_drawdown, absolute=True),
        "win_rate": _optional_decimal(raw.win_rate),
        "proof_score": _optional_decimal(raw.proof_score),
        "config": config,
    }


def _check_expectancy_inputs(
    normalized: Mapping[str, Any],
    config: ExpectancyStrengthConfig,
) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []
    checks = (
        (
            "expectancy_present",
            normalized["expectancy"] is not None,
        ),
        (
            "expectancy_positive",
            normalized["expectancy"] is not None and normalized["expectancy"] > 0,
        ),
        (
            "sample_depth_minimum",
            normalized["total_trades"] is not None
            and normalized["total_trades"] >= config.minimum_sample_size,
        ),
        (
            "profit_factor_minimum",
            normalized["profit_factor"] is not None
            and normalized["profit_factor"] >= config.minimum_profit_factor,
        ),
        (
            "drawdown_acceptable",
            normalized["max_drawdown"] is not None
            and normalized["max_drawdown"] <= config.maximum_acceptable_drawdown,
        ),
    )
    for name, ok in checks:
        if ok:
            passed.append(name)
        else:
            failed.append(name)
    return passed, failed


def _classify_expectancy(
    normalized: Mapping[str, Any],
    config: ExpectancyStrengthConfig,
    failed: tuple[str, ...] | list[str],
) -> str:
    expectancy = normalized["expectancy"]
    total_trades = normalized["total_trades"]
    profit_factor = normalized["profit_factor"]
    max_drawdown = normalized["max_drawdown"]
    if expectancy is None:
        return EXPECTANCY_UNKNOWN
    if expectancy <= Decimal("0"):
        return EXPECTANCY_BLOCKED
    if failed:
        return EXPECTANCY_WEAK
    if (
        expectancy >= config.strong_expectancy
        and total_trades is not None
        and total_trades >= config.strong_sample_size
        and profit_factor is not None
        and profit_factor >= config.strong_profit_factor
        and max_drawdown is not None
        and max_drawdown <= config.maximum_strong_drawdown
    ):
        return EXPECTANCY_STRONG
    if expectancy >= config.promising_expectancy:
        return EXPECTANCY_PROMISING
    return EXPECTANCY_WEAK


def _blockers(status: str, failed: tuple[str, ...] | list[str]) -> list[str]:
    blockers = list(failed)
    if status in {EXPECTANCY_BLOCKED, EXPECTANCY_UNKNOWN}:
        blockers.append(status)
    blockers.extend(
        (
            "demo trade remains locked",
            "broker action remains locked",
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
        )
    )
    return list(dict.fromkeys(blockers))


def _money_path_signal(status: str) -> str:
    return {
        EXPECTANCY_STRONG: "MONEY_PATH_STRONGER_FOR_PROOF_REVIEW_ONLY",
        EXPECTANCY_PROMISING: "MONEY_PATH_PROMISING_MORE_EVIDENCE_REQUIRED",
        EXPECTANCY_WEAK: "MONEY_PATH_WEAK_REPAIR_REQUIRED",
        EXPECTANCY_BLOCKED: "MONEY_PATH_BLOCKED_NEGATIVE_EXPECTANCY",
        EXPECTANCY_UNKNOWN: "MONEY_PATH_BLOCKED_UNKNOWN_EXPECTANCY",
    }[status]


def _next_safe_action(status: str) -> str:
    if status == EXPECTANCY_STRONG:
        return "Feed expectancy evidence into Real Evidence Depth Engine V1; do not approve execution."
    if status == EXPECTANCY_PROMISING:
        return "Collect deeper sample and drawdown evidence before promotion."
    if status == EXPECTANCY_WEAK:
        return "Repair weak expectancy inputs before any money-path review."
    if status == EXPECTANCY_BLOCKED:
        return "Reject or redesign this strategy until expectancy is positive."
    return "Provide known expectancy evidence before routing strength."


def _permissions() -> dict[str, bool]:
    return {
        "demo_trade_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def _optional_decimal(value: Any, *, absolute: bool = False) -> Decimal | None:
    if value is None or value == "UNKNOWN":
        return None
    parsed = _to_decimal(value)
    return abs(parsed) if absolute else parsed


def _optional_int(value: Any) -> int | None:
    if value is None or value == "UNKNOWN":
        return None
    return int(value)


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise ValueError("boolean is not valid decimal evidence")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal evidence: {value!r}") from exc


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
