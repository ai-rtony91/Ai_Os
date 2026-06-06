"""Local PAPER_ONLY risk management and kill-switch modeling for Sprint 10."""

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    EngineMode,
    KillSwitchReport,
    KillSwitchState,
    RiskAction,
    RiskBreachType,
    RiskDecisionReport,
    RiskManagementScenario,
    RiskPosture,
)


WEEKLY_DRAWDOWN_THRESHOLD_PCT = 5.0
NEAR_DRAWDOWN_FRACTION = 0.5

ACTION_PRIORITY = {
    RiskAction.CONTINUE: 0,
    RiskAction.REDUCE_RISK: 1,
    RiskAction.BLOCK_ORDER: 2,
    RiskAction.PAUSE_TRADING: 3,
    RiskAction.KILL_SWITCH: 4,
}

BREACH_ACTIONS = {
    RiskBreachType.NON_PAPER_MODE: RiskAction.KILL_SWITCH,
    RiskBreachType.DAILY_DRAWDOWN: RiskAction.KILL_SWITCH,
    RiskBreachType.WEEKLY_DRAWDOWN: RiskAction.KILL_SWITCH,
    RiskBreachType.VALIDATION_FAILED: RiskAction.PAUSE_TRADING,
    RiskBreachType.LOSS_STREAK: RiskAction.PAUSE_TRADING,
    RiskBreachType.EXPOSURE_TOO_HIGH: RiskAction.BLOCK_ORDER,
    RiskBreachType.MAX_OPEN_TRADES: RiskAction.BLOCK_ORDER,
    RiskBreachType.ORDER_RISK_TOO_HIGH: RiskAction.BLOCK_ORDER,
}

KILL_SWITCH_BREACHES = {
    RiskBreachType.NON_PAPER_MODE,
    RiskBreachType.DAILY_DRAWDOWN,
    RiskBreachType.WEEKLY_DRAWDOWN,
}


class RiskManagementEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def evaluate_scenario(self, scenario: RiskManagementScenario) -> RiskDecisionReport:
        breaches = []
        reasons = []

        if scenario.mode != EngineMode.PAPER_ONLY:
            breaches.append(RiskBreachType.NON_PAPER_MODE)
            reasons.append("Mode is not PAPER_ONLY.")
        if self.evaluate_validation_health(scenario):
            breaches.append(RiskBreachType.VALIDATION_FAILED)
            reasons.append("Validation is failing.")
        if self.evaluate_daily_drawdown(scenario):
            breaches.append(RiskBreachType.DAILY_DRAWDOWN)
            reasons.append("Daily drawdown limit is breached.")
        if self.evaluate_weekly_drawdown(scenario):
            breaches.append(RiskBreachType.WEEKLY_DRAWDOWN)
            reasons.append("Weekly drawdown threshold is breached.")
        if self.evaluate_loss_streak(scenario):
            breaches.append(RiskBreachType.LOSS_STREAK)
            reasons.append("Loss streak reached pause threshold.")
        if self.evaluate_open_trade_limit(scenario):
            breaches.append(RiskBreachType.MAX_OPEN_TRADES)
            reasons.append("Open trade count reached configured limit.")
        if self.evaluate_exposure(scenario):
            breaches.append(RiskBreachType.EXPOSURE_TOO_HIGH)
            reasons.append("Open trade count exceeds configured exposure limit.")
        if self.evaluate_order_risk(scenario):
            breaches.append(RiskBreachType.ORDER_RISK_TOO_HIGH)
            reasons.append("Proposed order risk exceeds allowed paper risk.")

        action = self._highest_priority_action(breaches)
        if not breaches and self._near_threshold(scenario):
            action = RiskAction.REDUCE_RISK
            reasons.append("Risk conditions are near a configured threshold.")
        elif not breaches:
            action = RiskAction.CONTINUE
            reasons.append("No risk breaches detected.")

        kill_state = KillSwitchState.TRIGGERED if any(item in KILL_SWITCH_BREACHES for item in breaches) else KillSwitchState.INACTIVE
        if action == RiskAction.PAUSE_TRADING and RiskBreachType.VALIDATION_FAILED in breaches:
            kill_state = KillSwitchState.ACTIVE

        recommended_position_risk = self._recommended_position_risk_pct(action)
        return RiskDecisionReport(
            mode=scenario.mode,
            scenario_name=scenario.name,
            risk_action=action,
            kill_switch_state=kill_state,
            breaches=breaches or [RiskBreachType.NONE],
            allowed=action in (RiskAction.CONTINUE, RiskAction.REDUCE_RISK),
            risk_posture=self._risk_posture_for(action),
            recommended_position_risk_pct=recommended_position_risk,
            recommended_action=self._recommended_action(action, breaches),
            reasons=reasons,
            metadata={
                "risk_model": "RISK_MODEL_ONLY",
                "allowed_order_risk_usd": self._allowed_order_risk(scenario.current_balance_usd),
                "daily_drawdown_limit_usd": self._daily_drawdown_limit(scenario.current_balance_usd),
                "weekly_drawdown_threshold_pct": WEEKLY_DRAWDOWN_THRESHOLD_PCT,
            },
        )

    def evaluate_daily_drawdown(self, scenario) -> bool:
        return scenario.current_daily_pnl_usd <= -self._daily_drawdown_limit(scenario.current_balance_usd)

    def evaluate_weekly_drawdown(self, scenario) -> bool:
        return scenario.weekly_drawdown_pct >= WEEKLY_DRAWDOWN_THRESHOLD_PCT

    def evaluate_loss_streak(self, scenario) -> bool:
        return scenario.consecutive_losses >= self.config.pause_after_consecutive_losses

    def evaluate_open_trade_limit(self, scenario) -> bool:
        return scenario.open_trade_count >= self.config.max_open_trades_paper

    def evaluate_exposure(self, scenario) -> bool:
        return scenario.open_trade_count > self.config.max_open_trades_paper

    def evaluate_order_risk(self, scenario) -> bool:
        return scenario.proposed_order_risk_usd > self._allowed_order_risk(scenario.current_balance_usd)

    def evaluate_validation_health(self, scenario) -> bool:
        return not scenario.validation_passed

    def build_kill_switch_report(self, report: RiskDecisionReport) -> KillSwitchReport:
        triggered_by = [breach for breach in report.breaches if breach in KILL_SWITCH_BREACHES]
        if not triggered_by and RiskBreachType.VALIDATION_FAILED in report.breaches:
            return KillSwitchReport(
                mode=report.mode,
                state=KillSwitchState.ACTIVE,
                triggered_by=[RiskBreachType.VALIDATION_FAILED],
                reset_required=True,
                reason="Validation failure pauses the local risk model.",
                next_safe_action="Fix validation before continuing.",
                metadata={"risk_model": "RISK_MODEL_ONLY"},
            )
        if not triggered_by:
            return KillSwitchReport(
                mode=report.mode,
                state=KillSwitchState.INACTIVE,
                triggered_by=[],
                reset_required=False,
                reason="No kill-switch breach is active.",
                next_safe_action="Continue local PAPER_ONLY risk monitoring.",
                metadata={"risk_model": "RISK_MODEL_ONLY"},
            )
        return KillSwitchReport(
            mode=report.mode,
            state=KillSwitchState.TRIGGERED,
            triggered_by=triggered_by,
            reset_required=True,
            reason=self._kill_switch_reason(triggered_by),
            next_safe_action=self._kill_switch_next_action(triggered_by),
            metadata={"risk_model": "RISK_MODEL_ONLY"},
        )

    def format_risk_report(self, report: RiskDecisionReport) -> str:
        return "\n".join(
            [
                f"Scenario: {report.scenario_name}",
                f"Mode: {report.mode}",
                f"Risk action: {report.risk_action}",
                f"Kill switch: {report.kill_switch_state}",
                f"Breaches: {', '.join(report.breaches)}",
                f"Recommended action: {report.recommended_action}",
            ]
        )

    def format_kill_switch_report(self, report: KillSwitchReport) -> str:
        triggered = ", ".join(report.triggered_by) if report.triggered_by else RiskBreachType.NONE
        return "\n".join(
            [
                f"Kill switch state: {report.state}",
                f"Triggered by: {triggered}",
                f"Reset required: {report.reset_required}",
                f"Reason: {report.reason}",
                f"Next safe action: {report.next_safe_action}",
            ]
        )

    def _highest_priority_action(self, breaches):
        action = RiskAction.CONTINUE
        for breach in breaches:
            candidate = BREACH_ACTIONS[breach]
            if ACTION_PRIORITY[candidate] > ACTION_PRIORITY[action]:
                action = candidate
        return action

    def _near_threshold(self, scenario):
        near_loss_streak = scenario.consecutive_losses == self.config.pause_after_consecutive_losses - 1
        near_daily_drawdown = scenario.current_daily_pnl_usd <= -(
            self._daily_drawdown_limit(scenario.current_balance_usd) * NEAR_DRAWDOWN_FRACTION
        )
        return near_loss_streak or near_daily_drawdown

    def _allowed_order_risk(self, balance_usd):
        return round(balance_usd * (self.config.paper_risk_per_trade_pct / 100), 2)

    def _daily_drawdown_limit(self, balance_usd):
        return round(balance_usd * (self.config.max_daily_drawdown_pct / 100), 2)

    def _recommended_position_risk_pct(self, action):
        if action == RiskAction.REDUCE_RISK:
            return round(self.config.paper_risk_per_trade_pct / 2, 3)
        if action == RiskAction.CONTINUE:
            return self.config.paper_risk_per_trade_pct
        return 0.0

    def _risk_posture_for(self, action):
        if action == RiskAction.KILL_SWITCH:
            return RiskPosture.PAUSED
        if action == RiskAction.PAUSE_TRADING:
            return RiskPosture.PAUSED
        if action in (RiskAction.BLOCK_ORDER, RiskAction.REDUCE_RISK):
            return RiskPosture.CONSERVATIVE
        return RiskPosture.NORMAL

    def _recommended_action(self, action, breaches):
        if action == RiskAction.KILL_SWITCH:
            if RiskBreachType.NON_PAPER_MODE in breaches:
                return "Block execution. Return to PAPER_ONLY mode."
            if RiskBreachType.WEEKLY_DRAWDOWN in breaches:
                return "Stop paper trading and review risk model before continuing."
            return "Stop paper trading for the day and review loss causes."
        if action == RiskAction.PAUSE_TRADING:
            if RiskBreachType.VALIDATION_FAILED in breaches:
                return "Fix validation before continuing."
            return "Pause PAPER_ONLY trading and review loss streak causes."
        if action == RiskAction.BLOCK_ORDER:
            return "Block this paper order and reduce exposure or risk."
        if action == RiskAction.REDUCE_RISK:
            return "Reduce paper risk and continue monitoring."
        return "Continue local PAPER_ONLY risk monitoring."

    def _kill_switch_reason(self, triggered_by):
        if RiskBreachType.NON_PAPER_MODE in triggered_by:
            return "Non-PAPER mode triggered the local kill-switch model."
        if RiskBreachType.WEEKLY_DRAWDOWN in triggered_by:
            return "Weekly drawdown threshold triggered the local kill-switch model."
        return "Daily drawdown limit triggered the local kill-switch model."

    def _kill_switch_next_action(self, triggered_by):
        if RiskBreachType.NON_PAPER_MODE in triggered_by:
            return "Block execution. Return to PAPER_ONLY mode."
        if RiskBreachType.WEEKLY_DRAWDOWN in triggered_by:
            return "Stop paper trading and review risk model before continuing."
        return "Stop paper trading for the day and review loss causes."
