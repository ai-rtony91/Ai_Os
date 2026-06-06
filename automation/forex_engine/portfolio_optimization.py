"""Local PAPER_ONLY portfolio allocation scaffold for Sprint 12 research."""

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    AllocationMethod,
    ConcentrationStatus,
    PortfolioAllocation,
    PortfolioMode,
    PortfolioOptimizationResult,
    PortfolioOptimizationStatus,
    PortfolioRiskSummary,
    RiskPosture,
)


MAX_SYMBOL_ALLOCATION_PCT = 35.0
XAUUSD_MAX_ALLOCATION_PCT = 25.0
MIN_SYMBOLS_REQUIRED = 2
PORTFOLIO_MODE = PortfolioMode.PORTFOLIO_MODEL_ONLY


class PortfolioOptimizationEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def build_equal_weight_allocation(self, starting_capital_usd=None) -> PortfolioOptimizationResult:
        capital = self._capital(starting_capital_usd)
        symbols = list(self.config.symbols)
        allocation_pct = round(100 / len(symbols), 4)
        allocation_usd = round(capital / len(symbols), 2)
        allocations = [
            self._allocation(
                symbol=symbol,
                allocation_usd=allocation_usd,
                allocation_pct=allocation_pct,
                capital=capital,
                confidence_score=None,
                warnings=[],
            )
            for symbol in symbols
        ]
        return self._build_result(
            AllocationMethod.EQUAL_WEIGHT,
            capital,
            allocations,
            warnings=["Equal-weight allocation is a conservative modeling baseline."],
        )

    def build_risk_capped_allocation(self, symbol_scores=None, starting_capital_usd=None) -> PortfolioOptimizationResult:
        capital = self._capital(starting_capital_usd)
        if not symbol_scores:
            result = self.build_equal_weight_allocation(capital)
            result.allocation_method = AllocationMethod.RISK_CAPPED
            result.warnings.append("Missing symbol scores; risk-capped allocation used equal-weight fallback.")
            result.recommendations = self.build_recommendations(result)
            return result
        raw_allocations = self._weighted_allocations(symbol_scores, capital)
        allocations = []
        for symbol in self.config.symbols:
            raw_usd = raw_allocations.get(symbol, 0.0)
            cap_pct = self._cap_pct(symbol)
            cap_usd = round(capital * (cap_pct / 100), 2)
            allocation_usd = round(min(raw_usd, cap_usd), 2)
            allocation_pct = round((allocation_usd / capital) * 100, 4)
            warnings = []
            if raw_usd > cap_usd:
                warnings.append(f"{symbol} allocation capped at {cap_pct:.2f} percent.")
            allocations.append(
                self._allocation(symbol, allocation_usd, allocation_pct, capital, symbol_scores.get(symbol), warnings)
            )
        return self._build_result(AllocationMethod.RISK_CAPPED, capital, allocations)

    def build_confidence_weighted_placeholder(self, symbol_scores, starting_capital_usd=None) -> PortfolioOptimizationResult:
        capital = self._capital(starting_capital_usd)
        if not symbol_scores:
            result = self.build_equal_weight_allocation(capital)
            result.allocation_method = AllocationMethod.CONFIDENCE_WEIGHTED_PLACEHOLDER
            result.warnings.append("Missing confidence scores; fell back to equal-weight allocation.")
            result.recommendations = self.build_recommendations(result)
            return result
        result = self.build_risk_capped_allocation(symbol_scores, capital)
        result.allocation_method = AllocationMethod.CONFIDENCE_WEIGHTED_PLACEHOLDER
        result.warnings.append("Confidence-weighted allocation is a placeholder model only.")
        result.recommendations = self.build_recommendations(result)
        return result

    def evaluate_concentration(self, allocations) -> PortfolioRiskSummary:
        if not allocations:
            return PortfolioRiskSummary(
                mode=PORTFOLIO_MODE,
                symbol_count=0,
                max_symbol_allocation_pct=0.0,
                max_symbol_allocation_usd=0.0,
                xauusd_allocation_pct=0.0,
                total_allocated_pct=0.0,
                concentration_status=ConcentrationStatus.INSUFFICIENT_DATA,
                warnings=["No allocations supplied."],
                metadata={"max_symbol_cap_pct": MAX_SYMBOL_ALLOCATION_PCT, "xauusd_cap_pct": XAUUSD_MAX_ALLOCATION_PCT},
            )
        max_allocation = max(allocations, key=lambda item: item.allocation_pct)
        xau_pct = next((item.allocation_pct for item in allocations if item.symbol == "XAUUSD"), 0.0)
        total_pct = round(sum(item.allocation_pct for item in allocations), 4)
        warnings = []
        status = ConcentrationStatus.OK
        if max_allocation.allocation_pct > MAX_SYMBOL_ALLOCATION_PCT:
            status = ConcentrationStatus.TOO_CONCENTRATED
            warnings.append("A symbol exceeds the max allocation cap.")
        if xau_pct > XAUUSD_MAX_ALLOCATION_PCT:
            status = ConcentrationStatus.TOO_CONCENTRATED
            warnings.append("XAUUSD exceeds the allocation cap.")
        if len(allocations) < MIN_SYMBOLS_REQUIRED:
            status = ConcentrationStatus.CAUTION
            warnings.append("Portfolio has fewer than the minimum required symbols.")
        if total_pct < 90:
            status = ConcentrationStatus.CAUTION if status == ConcentrationStatus.OK else status
            warnings.append("Less than 90 percent of paper capital is allocated.")
        if any("placeholder" in " ".join(item.warnings).lower() for item in allocations):
            status = ConcentrationStatus.CAUTION if status == ConcentrationStatus.OK else status
            warnings.append("Allocation relies on placeholder confidence data.")
        return PortfolioRiskSummary(
            mode=PORTFOLIO_MODE,
            symbol_count=len(allocations),
            max_symbol_allocation_pct=max_allocation.allocation_pct,
            max_symbol_allocation_usd=max_allocation.allocation_usd,
            xauusd_allocation_pct=xau_pct,
            total_allocated_pct=total_pct,
            concentration_status=status,
            warnings=warnings,
            metadata={"max_symbol_cap_pct": MAX_SYMBOL_ALLOCATION_PCT, "xauusd_cap_pct": XAUUSD_MAX_ALLOCATION_PCT},
        )

    def build_recommendations(self, result):
        recommendations = ["Use larger historical datasets before trusting allocation."]
        if any(item.symbol == "XAUUSD" and item.warnings for item in result.allocations):
            recommendations.append("Keep XAUUSD allocation capped until tick-value and volatility modeling improve.")
        if result.concentration_status == ConcentrationStatus.TOO_CONCENTRATED:
            recommendations.append("Reduce concentration before portfolio promotion.")
        if result.unallocated_capital_usd > 0:
            recommendations.append("Leave unallocated capital in reserve until allocation evidence improves.")
        if result.allocation_method == AllocationMethod.EQUAL_WEIGHT:
            recommendations.append("Equal-weight allocation is a conservative modeling baseline, not an optimized portfolio.")
        return recommendations

    def format_portfolio_result(self, result) -> str:
        lines = [
            "AI_OS Forex Engine v1 Sprint 12 Portfolio Optimization Report",
            f"Mode: {result.mode}",
            f"Portfolio mode: {result.metadata.get('portfolio_mode', PORTFOLIO_MODE)}",
            f"Allocation method: {result.allocation_method}",
            f"Starting capital: {result.starting_capital_usd:.2f} USD",
            f"Concentration status: {result.concentration_status}",
            f"Optimization status: {result.optimization_status}",
        ]
        for allocation in result.allocations:
            lines.append(f"{allocation.symbol}: {allocation.allocation_usd:.2f} USD ({allocation.allocation_pct:.2f}%)")
        return "\n".join(lines)

    def _build_result(self, method, capital, allocations, warnings=None):
        allocated = round(sum(item.allocation_usd for item in allocations), 2)
        risk_summary = self.evaluate_concentration(allocations)
        result_warnings = list(warnings or []) + risk_summary.warnings
        result = PortfolioOptimizationResult(
            mode="PAPER_ONLY",
            allocation_method=method,
            starting_capital_usd=capital,
            allocated_capital_usd=allocated,
            unallocated_capital_usd=round(max(0.0, capital - allocated), 2),
            allocations=allocations,
            concentration_status=risk_summary.concentration_status,
            optimization_status=PortfolioOptimizationStatus.INSUFFICIENT_DATA,
            risk_posture=RiskPosture.CONSERVATIVE,
            warnings=result_warnings,
            summary_note="Local PORTFOLIO_MODEL_ONLY scaffold. Allocation is not real capital movement.",
            metadata={"portfolio_mode": PORTFOLIO_MODE, "risk_summary": risk_summary},
        )
        result.recommendations = self.build_recommendations(result)
        return result

    def _allocation(self, symbol, allocation_usd, allocation_pct, capital, confidence_score, warnings):
        return PortfolioAllocation(
            symbol=symbol,
            allocation_usd=round(allocation_usd, 2),
            allocation_pct=round(allocation_pct, 4),
            risk_cap_usd=round(capital * (self._cap_pct(symbol) / 100), 2),
            confidence_score=confidence_score,
            status=ConcentrationStatus.CAUTION if warnings else ConcentrationStatus.OK,
            warnings=list(warnings),
            metadata={"portfolio_mode": PORTFOLIO_MODE},
        )

    def _weighted_allocations(self, symbol_scores, capital):
        scores = {symbol: max(0.0, float(symbol_scores.get(symbol, 0.0))) for symbol in self.config.symbols}
        total = sum(scores.values())
        if total <= 0:
            return {symbol: capital / len(self.config.symbols) for symbol in self.config.symbols}
        return {symbol: capital * (score / total) for symbol, score in scores.items()}

    def _cap_pct(self, symbol):
        return XAUUSD_MAX_ALLOCATION_PCT if symbol == "XAUUSD" else MAX_SYMBOL_ALLOCATION_PCT

    def _capital(self, starting_capital_usd):
        capital = self.config.starting_balance_usd if starting_capital_usd is None else float(starting_capital_usd)
        if capital <= 0:
            raise ValueError("starting_capital_usd must be positive.")
        return capital
