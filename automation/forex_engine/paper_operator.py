"""Local PAPER_ONLY paper-operator reporting for Sprint 8 research."""

from datetime import date

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    AlertState,
    DailyOperatorReport,
    EngineMode,
    OperatorAlert,
    PaperOperatorStatus,
    PauseReason,
    RiskPosture,
    StrategyStatus,
    SupervisorSummary,
    WalkForwardStatus,
)


HARD_PAUSE_ALERTS = {
    AlertState.LOSS_STREAK_ALERT,
    AlertState.DAILY_DRAWDOWN_ALERT,
    AlertState.WEEKLY_DRAWDOWN_ALERT,
    AlertState.VALIDATION_HEALTH_ALERT,
}


class PaperOperator:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def build_daily_report(
        self,
        strategy_comparison=None,
        walk_forward_results=None,
        performance_summary=None,
        current_balance_usd=None,
        current_daily_pnl_usd=0.0,
        consecutive_losses=0,
        weekly_drawdown_pct=0.0,
        validation_passed=True,
        net_pnl_usd=None,
        report_date=None,
    ) -> DailyOperatorReport:
        current_balance = (
            current_balance_usd
            if current_balance_usd is not None
            else getattr(performance_summary, "current_balance_usd", self.config.starting_balance_usd)
        )
        net_pnl = (
            net_pnl_usd
            if net_pnl_usd is not None
            else getattr(performance_summary, "net_pnl_usd", current_balance - self.config.starting_balance_usd)
        )
        alerts = self.evaluate_alerts(
            strategy_comparison=strategy_comparison,
            walk_forward_results=walk_forward_results,
            net_pnl_usd=net_pnl,
            current_balance_usd=current_balance,
            current_daily_pnl_usd=current_daily_pnl_usd,
            consecutive_losses=consecutive_losses,
            weekly_drawdown_pct=weekly_drawdown_pct,
            validation_passed=validation_passed,
        )
        risk_posture = self.determine_risk_posture(alerts, strategy_comparison)
        pause_reason = self.determine_pause_reason(alerts, validation_passed)
        operator_status = self.determine_operator_status(alerts, risk_posture, validation_passed)
        summary = self._summary_for(operator_status)
        next_safe_action = self._next_action_for(operator_status)
        return DailyOperatorReport(
            mode=self.config.mode,
            report_date=report_date or date.today().isoformat(),
            starting_balance_usd=self.config.starting_balance_usd,
            current_balance_usd=current_balance,
            net_pnl_usd=net_pnl,
            risk_posture=risk_posture,
            operator_status=operator_status,
            pause_reason=pause_reason,
            alerts=alerts,
            summary=summary,
            next_safe_action=next_safe_action,
            metadata={
                "paper_operator_version": "sprint_8",
                "local_research_only": True,
                "promotion_ready": False,
            },
        )

    def build_supervisor_summary(self, daily_report) -> SupervisorSummary:
        active_alerts = [alert for alert in daily_report.alerts if alert.active]
        paper_boundary_ok = any(alert.name == AlertState.PAPER_ONLY_BOUNDARY_OK and alert.active for alert in active_alerts)
        research_ready = daily_report.operator_status in (
            PaperOperatorStatus.READY_FOR_PAPER_RESEARCH,
            PaperOperatorStatus.WATCHLIST,
        )
        summary = (
            f"Paper operator status is {daily_report.operator_status}. "
            "Live promotion is not available in Sprint 8."
        )
        if daily_report.operator_status == PaperOperatorStatus.PAUSED_FOR_INSUFFICIENT_DATA:
            summary = (
                "Research stack is healthy, but current fixture data is insufficient for strategy trust. "
                "Live promotion is not available in Sprint 8."
            )
        return SupervisorSummary(
            mode=daily_report.mode,
            status=daily_report.operator_status,
            risk_posture=daily_report.risk_posture,
            active_alert_count=len(active_alerts),
            paper_only_boundary_ok=paper_boundary_ok,
            research_ready=research_ready,
            promotion_ready=False,
            summary=summary,
            next_safe_action=daily_report.next_safe_action,
            metadata={"paper_operator_version": "sprint_8"},
        )

    def evaluate_alerts(
        self,
        strategy_comparison=None,
        walk_forward_results=None,
        net_pnl_usd=0.0,
        current_balance_usd=None,
        current_daily_pnl_usd=0.0,
        consecutive_losses=0,
        weekly_drawdown_pct=0.0,
        validation_passed=True,
        profit_milestones_usd=None,
    ):
        alerts = []
        if self.config.mode == EngineMode.PAPER_ONLY:
            alerts.append(
                OperatorAlert(
                    AlertState.PAPER_ONLY_BOUNDARY_OK,
                    True,
                    "INFO",
                    "Engine mode is PAPER_ONLY.",
                    "Continue local PAPER_ONLY research only.",
                )
            )
        else:
            alerts.append(
                OperatorAlert(
                    AlertState.PAPER_ONLY_BOUNDARY_OK,
                    False,
                    "CRITICAL",
                    "Engine mode is not PAPER_ONLY.",
                    "Block operator work until mode returns to PAPER_ONLY.",
                )
            )

        if self._insufficient_data(strategy_comparison, walk_forward_results):
            alerts.append(
                OperatorAlert(
                    AlertState.INSUFFICIENT_DATA_ALERT,
                    True,
                    "WARN",
                    "All current strategy or walk-forward research inputs are insufficient data.",
                    "Use larger historical datasets before trusting strategy results.",
                )
            )

        milestones = profit_milestones_usd or (25, 50, 100, 250, 500, 1000)
        reached = [milestone for milestone in milestones if net_pnl_usd >= milestone]
        if reached:
            alerts.append(
                OperatorAlert(
                    AlertState.PROFIT_MILESTONE_ALERT,
                    True,
                    "INFO",
                    f"Research PnL reached {max(reached):.2f} USD milestone.",
                    "Record milestone and continue PAPER_ONLY validation.",
                    metadata={"milestone_usd": max(reached)},
                )
            )

        if consecutive_losses >= self.config.pause_after_consecutive_losses:
            alerts.append(
                OperatorAlert(
                    AlertState.LOSS_STREAK_ALERT,
                    True,
                    "CRITICAL",
                    "Loss streak reached the configured pause threshold.",
                    "Pause PAPER_ONLY research and review setup quality.",
                )
            )

        balance = current_balance_usd if current_balance_usd is not None else self.config.starting_balance_usd
        daily_limit = balance * (self.config.max_daily_drawdown_pct / 100)
        if current_daily_pnl_usd <= -daily_limit:
            alerts.append(
                OperatorAlert(
                    AlertState.DAILY_DRAWDOWN_ALERT,
                    True,
                    "CRITICAL",
                    "Current daily PnL reached the configured drawdown limit.",
                    "Pause paper operator for the day.",
                    metadata={"daily_drawdown_limit_usd": round(daily_limit, 2)},
                )
            )

        if weekly_drawdown_pct >= 5.0:
            alerts.append(
                OperatorAlert(
                    AlertState.WEEKLY_DRAWDOWN_ALERT,
                    True,
                    "CRITICAL",
                    "Weekly drawdown reached the paper-operator pause threshold.",
                    "Pause paper operator and review risk model.",
                )
            )

        if not validation_passed:
            alerts.append(
                OperatorAlert(
                    AlertState.VALIDATION_HEALTH_ALERT,
                    True,
                    "CRITICAL",
                    "Validation is failing.",
                    "Fix validation before continuing.",
                )
            )
        return alerts

    def determine_risk_posture(self, alerts, strategy_comparison=None):
        active_names = self._active_names(alerts)
        if active_names & HARD_PAUSE_ALERTS:
            return RiskPosture.PAUSED
        if AlertState.INSUFFICIENT_DATA_ALERT in active_names:
            return RiskPosture.CONSERVATIVE
        if self._has_strong_research_candidate(strategy_comparison):
            return RiskPosture.AGGRESSIVE_RESEARCH_ONLY
        return RiskPosture.NORMAL

    def determine_operator_status(self, alerts, risk_posture=None, validation_passed=True):
        active_names = self._active_names(alerts)
        if self.config.mode != EngineMode.PAPER_ONLY or not validation_passed:
            return PaperOperatorStatus.BLOCKED
        if AlertState.DAILY_DRAWDOWN_ALERT in active_names or AlertState.WEEKLY_DRAWDOWN_ALERT in active_names:
            return PaperOperatorStatus.PAUSED_FOR_RISK_LIMIT
        if AlertState.LOSS_STREAK_ALERT in active_names:
            return PaperOperatorStatus.PAUSED_FOR_LOSS_STREAK
        if AlertState.INSUFFICIENT_DATA_ALERT in active_names:
            return PaperOperatorStatus.PAUSED_FOR_INSUFFICIENT_DATA
        if risk_posture == RiskPosture.CONSERVATIVE:
            return PaperOperatorStatus.WATCHLIST
        return PaperOperatorStatus.READY_FOR_PAPER_RESEARCH

    def determine_pause_reason(self, alerts, validation_passed=True):
        active_names = self._active_names(alerts)
        if not validation_passed or AlertState.VALIDATION_HEALTH_ALERT in active_names:
            return PauseReason.VALIDATION_FAILURE
        if AlertState.DAILY_DRAWDOWN_ALERT in active_names:
            return PauseReason.DAILY_DRAWDOWN_LIMIT
        if AlertState.WEEKLY_DRAWDOWN_ALERT in active_names:
            return PauseReason.WEEKLY_DRAWDOWN_LIMIT
        if AlertState.LOSS_STREAK_ALERT in active_names:
            return PauseReason.LOSS_STREAK
        if AlertState.INSUFFICIENT_DATA_ALERT in active_names:
            return PauseReason.INSUFFICIENT_DATA
        return PauseReason.NONE

    def format_operator_report(self, report) -> str:
        active_alerts = [alert.name for alert in report.alerts if alert.active]
        alert_text = ", ".join(active_alerts) if active_alerts else AlertState.NO_ALERTS
        return "\n".join(
            [
                "AI_OS Forex Engine v1 Sprint 8 Paper Operator Report",
                f"Mode: {report.mode}",
                f"Report date: {report.report_date}",
                f"Starting balance: {report.starting_balance_usd:.2f} USD",
                f"Current balance: {report.current_balance_usd:.2f} USD",
                f"Research PnL: {report.net_pnl_usd:.2f} USD",
                f"Risk posture: {report.risk_posture}",
                f"Operator status: {report.operator_status}",
                f"Pause reason: {report.pause_reason}",
                f"Active alerts: {alert_text}",
                f"Summary: {report.summary}",
                f"Next safe action: {report.next_safe_action}",
            ]
        )

    def format_supervisor_summary(self, summary) -> str:
        return "\n".join(
            [
                "Supervisor summary:",
                f"Mode: {summary.mode}",
                f"Status: {summary.status}",
                f"Risk posture: {summary.risk_posture}",
                f"Active alert count: {summary.active_alert_count}",
                f"Paper-only boundary ok: {summary.paper_only_boundary_ok}",
                f"Research ready: {summary.research_ready}",
                f"Promotion ready: {summary.promotion_ready}",
                f"Summary: {summary.summary}",
                f"Next safe action: {summary.next_safe_action}",
            ]
        )

    def _insufficient_data(self, strategy_comparison, walk_forward_results):
        scorecards = getattr(strategy_comparison, "scorecards", None)
        if scorecards and all(item.status == StrategyStatus.INSUFFICIENT_DATA for item in scorecards):
            return True
        results = walk_forward_results or []
        if results and all(item.status == WalkForwardStatus.INSUFFICIENT_DATA for item in results):
            return True
        return False

    def _has_strong_research_candidate(self, strategy_comparison):
        scorecards = getattr(strategy_comparison, "scorecards", None) or []
        return any(
            item.status == StrategyStatus.RESEARCH_CANDIDATE and item.score >= 85 and item.trades >= 20
            for item in scorecards
        )

    def _active_names(self, alerts):
        return {alert.name for alert in alerts if alert.active}

    def _summary_for(self, status):
        if status == PaperOperatorStatus.PAUSED_FOR_INSUFFICIENT_DATA:
            return "Research stack is healthy, but current fixture data is insufficient for strategy trust."
        if status == PaperOperatorStatus.PAUSED_FOR_RISK_LIMIT:
            return "Paper operator is paused because a risk limit alert is active."
        if status == PaperOperatorStatus.PAUSED_FOR_LOSS_STREAK:
            return "Paper operator is paused because the configured loss streak threshold was reached."
        if status == PaperOperatorStatus.BLOCKED:
            return "Paper operator is blocked until PAPER_ONLY mode and validation health are restored."
        if status == PaperOperatorStatus.WATCHLIST:
            return "Paper operator can continue only under conservative watchlist review."
        return "Paper operator can continue local PAPER_ONLY research."

    def _next_action_for(self, status):
        if status == PaperOperatorStatus.PAUSED_FOR_INSUFFICIENT_DATA:
            return "Use larger historical datasets before promotion or strategy trust."
        if status == PaperOperatorStatus.PAUSED_FOR_RISK_LIMIT:
            return "Pause paper operator and review risk controls."
        if status == PaperOperatorStatus.PAUSED_FOR_LOSS_STREAK:
            return "Pause PAPER_ONLY research and review setup quality."
        if status == PaperOperatorStatus.BLOCKED:
            return "Fix PAPER_ONLY mode or validation before continuing."
        return "Continue local PAPER_ONLY research; do not promote to live trading."
