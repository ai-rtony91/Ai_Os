"""Run the AI_OS Forex Engine v1 Sprint 13 historical-data readiness demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.historical_data_readiness import READINESS_MODE, HistoricalDataReadinessEngine


def build_demo_summary(config=None):
    config = config or ForexEngineConfig()
    validate_config(config)
    engine = HistoricalDataReadinessEngine(config)
    output_dir = Path("automation/forex_engine/runtime/historical_data_demo")
    dataset_path = engine.generate_synthetic_dataset(output_dir, row_count=1000)
    return engine.inspect_dataset(dataset_path)


def main() -> int:
    config = ForexEngineConfig()
    summary = build_demo_summary(config)

    print("AI_OS Forex Engine v1 Sprint 13 Historical Data Readiness Demo")
    print(f"Mode: {config.mode}")
    print(f"Readiness mode: {READINESS_MODE}")
    print("Data source: generated local synthetic dataset only")
    print(f"Dataset rows: {summary.manifest.row_count}")
    print(f"Symbols: {', '.join(summary.manifest.symbols)}")
    print(f"Timeframes: {', '.join(summary.manifest.timeframes)}")
    print(f"Schema status: {'VALID' if summary.missing_field_count == 0 else 'INVALID'}")
    print(
        "Timestamp status: "
        f"{'SORTED' if not any(issue.code == 'UNSORTED_TIMESTAMP' for issue in summary.quality_score.issues) else 'NEEDS_CLEANING'}"
    )
    print(f"Duplicate status: {'NONE' if summary.duplicate_count == 0 else summary.duplicate_count}")
    print(f"Missing field status: {'NONE' if summary.missing_field_count == 0 else summary.missing_field_count}")
    print(f"Quality score: {summary.quality_score.score}")
    print(f"Readiness status: {summary.readiness_status}")
    print(f"Duplicate count: {summary.duplicate_count}")
    print(f"Missing field count: {summary.missing_field_count}")
    print(f"Invalid row count: {summary.invalid_row_count}")
    print(f"Warnings: {'; '.join(summary.quality_score.warnings)}")
    print(f"Recommendations: {'; '.join(summary.recommendations)}")
    print("Safety note: Local historical data readiness only; no broker/API/network/download/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
