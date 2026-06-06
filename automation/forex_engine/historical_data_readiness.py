"""Local PAPER_ONLY historical-data readiness scaffold for Sprint 13."""

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import REQUIRED_COLUMNS
from automation.forex_engine.models import (
    DatasetIssue,
    DatasetIssueSeverity,
    DatasetManifest,
    DatasetQualityScore,
    EngineMode,
    HistoricalDataReadinessStatus,
    HistoricalDatasetSummary,
    utc_now_iso,
)


READINESS_MODE = "HISTORICAL_DATA_READINESS_ONLY"
REQUIRED_FIELDS = tuple(REQUIRED_COLUMNS)
MINIMUM_ROWS_PER_SYMBOL_TIMEFRAME = 100


class HistoricalDataReadinessEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def inspect_dataset(self, path) -> HistoricalDatasetSummary:
        csv_path = self._local_path(path)
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            schema_fields = list(reader.fieldnames or [])
            rows = list(reader)

        schema_issues = self._validate_schema(schema_fields)
        row_issues = self.validate_rows(rows)
        duplicate_issues = self._duplicate_issues(rows)
        order_issues = self._timestamp_order_issues(rows)
        issues = schema_issues + row_issues + duplicate_issues + order_issues

        manifest = self.build_manifest(csv_path, rows, schema_fields=schema_fields)
        quality_score = self._score_from_rows(rows, issues)
        valid_rows = self._valid_row_count(rows, row_issues)
        invalid_rows = max(0, len(rows) - valid_rows)
        duplicate_count = len(duplicate_issues)
        missing_field_count = sum(
            1
            for issue in issues
            if issue.code in {"MISSING_REQUIRED_FIELD", "ROW_MISSING_FIELD", "EMPTY_REQUIRED_FIELD"}
        )
        readiness_status = quality_score.status
        recommendations = self._recommendations(readiness_status, issues)

        return HistoricalDatasetSummary(
            mode=EngineMode.PAPER_ONLY,
            manifest=manifest,
            quality_score=quality_score,
            readiness_status=readiness_status,
            valid_row_count=valid_rows,
            invalid_row_count=invalid_rows,
            duplicate_count=duplicate_count,
            missing_field_count=missing_field_count,
            symbol_count=len(manifest.symbols),
            timeframe_count=len(manifest.timeframes),
            recommendations=recommendations,
            metadata={
                "readiness_mode": READINESS_MODE,
                "minimum_rows_per_symbol_timeframe": MINIMUM_ROWS_PER_SYMBOL_TIMEFRAME,
                "issue_count": len(issues),
            },
        )

    def validate_rows(self, rows) -> list[DatasetIssue]:
        issues = []
        for index, row in enumerate(rows, start=2):
            for field in REQUIRED_FIELDS:
                if field not in row:
                    issues.append(
                        DatasetIssue(
                            code="ROW_MISSING_FIELD",
                            severity=DatasetIssueSeverity.ERROR,
                            message=f"Row is missing required field: {field}",
                            row_number=index,
                        )
                    )
                elif str(row.get(field, "")).strip() == "":
                    issues.append(
                        DatasetIssue(
                            code="EMPTY_REQUIRED_FIELD",
                            severity=DatasetIssueSeverity.ERROR,
                            message=f"Row has empty required field: {field}",
                            row_number=index,
                        )
                    )
            if any(issue.row_number == index and issue.severity == DatasetIssueSeverity.ERROR for issue in issues):
                continue

            symbol = row["symbol"]
            timeframe = row["timeframe"]
            if symbol not in self.config.symbols:
                issues.append(
                    DatasetIssue(
                        code="INVALID_SYMBOL",
                        severity=DatasetIssueSeverity.ERROR,
                        message=f"Symbol is not configured: {symbol}",
                        row_number=index,
                    )
                )
            if timeframe not in self.config.timeframes:
                issues.append(
                    DatasetIssue(
                        code="INVALID_TIMEFRAME",
                        severity=DatasetIssueSeverity.ERROR,
                        message=f"Timeframe is not configured: {timeframe}",
                        row_number=index,
                    )
                )

            parsed = {}
            for field in ("open", "high", "low", "close", "volume"):
                try:
                    parsed[field] = float(row[field])
                except (TypeError, ValueError):
                    issues.append(
                        DatasetIssue(
                            code="INVALID_NUMERIC_VALUE",
                            severity=DatasetIssueSeverity.ERROR,
                            message=f"{field} must parse as a number.",
                            row_number=index,
                        )
                    )
            if len(parsed) != 5:
                continue
            if min(parsed["open"], parsed["high"], parsed["low"], parsed["close"]) <= 0:
                issues.append(
                    DatasetIssue(
                        code="INVALID_PRICE",
                        severity=DatasetIssueSeverity.ERROR,
                        message="OHLC prices must be positive.",
                        row_number=index,
                    )
                )
            if parsed["volume"] < 0:
                issues.append(
                    DatasetIssue(
                        code="INVALID_VOLUME",
                        severity=DatasetIssueSeverity.ERROR,
                        message="Volume must be zero or positive.",
                        row_number=index,
                    )
                )
            if parsed["high"] < max(parsed["open"], parsed["low"], parsed["close"]):
                issues.append(
                    DatasetIssue(
                        code="INVALID_OHLC_RELATIONSHIP",
                        severity=DatasetIssueSeverity.ERROR,
                        message="High must be greater than or equal to open, low, and close.",
                        row_number=index,
                    )
                )
            if parsed["low"] > min(parsed["open"], parsed["high"], parsed["close"]):
                issues.append(
                    DatasetIssue(
                        code="INVALID_OHLC_RELATIONSHIP",
                        severity=DatasetIssueSeverity.ERROR,
                        message="Low must be less than or equal to open, high, and close.",
                        row_number=index,
                    )
                )
        return issues

    def score_dataset(self, summary_or_rows) -> DatasetQualityScore:
        if isinstance(summary_or_rows, HistoricalDatasetSummary):
            return summary_or_rows.quality_score
        rows = list(summary_or_rows)
        issues = self.validate_rows(rows) + self._duplicate_issues(rows) + self._timestamp_order_issues(rows)
        return self._score_from_rows(rows, issues)

    def validate_dataset(self, path) -> HistoricalDatasetSummary:
        return self.inspect_dataset(path)

    def build_manifest(self, path, rows, schema_fields=None) -> DatasetManifest:
        csv_path = Path(path)
        fields = list(schema_fields or REQUIRED_FIELDS)
        symbols = sorted({row.get("symbol", "") for row in rows if row.get("symbol")})
        timeframes = sorted({row.get("timeframe", "") for row in rows if row.get("timeframe")})
        timestamps = sorted(row.get("timestamp", "") for row in rows if row.get("timestamp"))
        return DatasetManifest(
            mode=EngineMode.PAPER_ONLY,
            dataset_name=csv_path.name,
            source_type="LOCAL_CSV",
            path=str(csv_path),
            row_count=len(rows),
            symbols=symbols,
            timeframes=timeframes,
            first_timestamp=timestamps[0] if timestamps else None,
            last_timestamp=timestamps[-1] if timestamps else None,
            schema_fields=fields,
            created_at=utc_now_iso(),
            metadata={"readiness_mode": READINESS_MODE},
        )

    def build_readiness_report(self, path) -> HistoricalDatasetSummary:
        return self.inspect_dataset(path)

    def generate_synthetic_dataset(self, path, row_count=1000) -> Path:
        output_path = Path(path)
        if output_path.suffix.lower() != ".csv":
            output_path = output_path / "historical_data_readiness_synthetic.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        symbols = list(self.config.symbols)
        start = datetime(2026, 1, 5, 0, 0, tzinfo=timezone.utc)
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED_FIELDS)
            writer.writeheader()
            for index in range(row_count):
                symbol = symbols[index % len(symbols)]
                step = index // len(symbols)
                timestamp = (start + timedelta(minutes=5 * step)).strftime("%Y-%m-%dT%H:%M:%SZ")
                base_price = self._base_price(symbol) + (step * self._price_step(symbol))
                writer.writerow(
                    {
                        "timestamp": timestamp,
                        "symbol": symbol,
                        "timeframe": "5m",
                        "open": f"{base_price:.5f}",
                        "high": f"{base_price + self._range_size(symbol):.5f}",
                        "low": f"{base_price - self._range_size(symbol):.5f}",
                        "close": f"{base_price + self._price_step(symbol):.5f}",
                        "volume": 1000 + index,
                    }
                )
        return output_path

    def format_readiness_summary(self, summary: HistoricalDatasetSummary) -> str:
        warnings = summary.quality_score.warnings or ["None"]
        lines = [
            "AI_OS Forex Engine v1 Sprint 13 Historical Data Readiness Report",
            f"Mode: {summary.mode}",
            f"Readiness mode: {summary.metadata.get('readiness_mode', READINESS_MODE)}",
            f"Dataset rows: {summary.manifest.row_count}",
            f"Symbols: {', '.join(summary.manifest.symbols)}",
            f"Timeframes: {', '.join(summary.manifest.timeframes)}",
            f"Quality score: {summary.quality_score.score}",
            f"Readiness status: {summary.readiness_status}",
            f"Duplicate count: {summary.duplicate_count}",
            f"Missing field count: {summary.missing_field_count}",
            f"Invalid row count: {summary.invalid_row_count}",
            f"Warnings: {'; '.join(warnings)}",
            f"Recommendations: {'; '.join(summary.recommendations)}",
            "Safety note: Local historical data readiness only; no broker/API/network/download/live execution path used.",
        ]
        return "\n".join(lines)

    def _local_path(self, path) -> Path:
        text = str(path)
        lowered = text.lower()
        if lowered.startswith("http://") or lowered.startswith("https://"):
            raise ValueError("Historical data readiness only accepts local file paths; URL paths are blocked.")
        csv_path = Path(path)
        if not csv_path.exists():
            raise ValueError(f"Local dataset not found: {csv_path}")
        if not csv_path.is_file():
            raise ValueError(f"Local dataset path must be a file: {csv_path}")
        return csv_path

    def _validate_schema(self, schema_fields) -> list[DatasetIssue]:
        issues = []
        field_set = set(schema_fields)
        for field in REQUIRED_FIELDS:
            if field not in field_set:
                issues.append(
                    DatasetIssue(
                        code="MISSING_REQUIRED_FIELD",
                        severity=DatasetIssueSeverity.ERROR,
                        message=f"CSV is missing required field: {field}",
                        row_number=None,
                    )
                )
        for field in schema_fields:
            if field not in REQUIRED_FIELDS:
                issues.append(
                    DatasetIssue(
                        code="EXTRA_FIELD",
                        severity=DatasetIssueSeverity.INFO,
                        message=f"CSV has extra field allowed by readiness scaffold: {field}",
                        row_number=None,
                    )
                )
        return issues

    def _duplicate_issues(self, rows) -> list[DatasetIssue]:
        seen = set()
        issues = []
        for index, row in enumerate(rows, start=2):
            key = (row.get("symbol"), row.get("timeframe"), row.get("timestamp"))
            if not all(key):
                continue
            if key in seen:
                issues.append(
                    DatasetIssue(
                        code="DUPLICATE_TIMESTAMP",
                        severity=DatasetIssueSeverity.WARNING,
                        message="Duplicate timestamp for symbol/timeframe.",
                        row_number=index,
                        metadata={"symbol": key[0], "timeframe": key[1], "timestamp": key[2]},
                    )
                )
            seen.add(key)
        return issues

    def _timestamp_order_issues(self, rows) -> list[DatasetIssue]:
        issues = []
        previous_by_key = {}
        for index, row in enumerate(rows, start=2):
            key = (row.get("symbol"), row.get("timeframe"))
            timestamp = row.get("timestamp")
            if not key[0] or not key[1] or not timestamp:
                continue
            previous = previous_by_key.get(key)
            if previous is not None and timestamp < previous:
                issues.append(
                    DatasetIssue(
                        code="UNSORTED_TIMESTAMP",
                        severity=DatasetIssueSeverity.WARNING,
                        message="Timestamps should be sorted ascending within each symbol/timeframe.",
                        row_number=index,
                        metadata={"symbol": key[0], "timeframe": key[1], "timestamp": timestamp},
                    )
                )
            previous_by_key[key] = timestamp
        return issues

    def _score_from_rows(self, rows, issues) -> DatasetQualityScore:
        score = 100
        error_count = sum(1 for issue in issues if issue.severity == DatasetIssueSeverity.ERROR)
        warning_count = sum(1 for issue in issues if issue.severity == DatasetIssueSeverity.WARNING)
        duplicate_count = sum(1 for issue in issues if issue.code == "DUPLICATE_TIMESTAMP")
        unsorted_count = sum(1 for issue in issues if issue.code == "UNSORTED_TIMESTAMP")
        invalid_symbol_or_timeframe = sum(
            1 for issue in issues if issue.code in {"INVALID_SYMBOL", "INVALID_TIMEFRAME"}
        )
        missing_required = sum(
            1 for issue in issues if issue.code in {"MISSING_REQUIRED_FIELD", "ROW_MISSING_FIELD"}
        )

        score -= missing_required * 35
        score -= invalid_symbol_or_timeframe * 25
        score -= error_count * 8
        score -= duplicate_count * 5
        score -= unsorted_count * 10
        score -= warning_count * 3
        minimum_rows = self._minimum_required_rows(rows)
        if len(rows) < minimum_rows:
            score -= 35

        clamped = max(0, min(100, int(score)))
        warnings = [issue.message for issue in issues if issue.severity == DatasetIssueSeverity.WARNING]
        if rows:
            warnings.append("Synthetic or local sample only; external market-data quality is not certified.")
            warnings.append("Weekend filtering not modeled by Sprint 13 readiness scaffold.")
        status = self._status_for_score(clamped, rows, issues)
        return DatasetQualityScore(
            mode=EngineMode.PAPER_ONLY,
            score=clamped,
            status=status,
            issues=list(issues),
            warnings=list(dict.fromkeys(warnings)),
            recommendations=self._recommendations(status, issues),
            metadata={"readiness_mode": READINESS_MODE, "minimum_required_rows": minimum_rows},
        )

    def _status_for_score(self, score, rows, issues) -> str:
        if any(issue.severity == DatasetIssueSeverity.ERROR for issue in issues):
            return HistoricalDataReadinessStatus.INVALID_DATASET if score < 80 else HistoricalDataReadinessStatus.NEEDS_CLEANING
        if len(rows) < self._minimum_required_rows(rows):
            return HistoricalDataReadinessStatus.INSUFFICIENT_DATA
        if score >= 80:
            return HistoricalDataReadinessStatus.READY_FOR_LOCAL_IMPORT
        if score >= 50:
            return HistoricalDataReadinessStatus.NEEDS_CLEANING
        return HistoricalDataReadinessStatus.INVALID_DATASET

    def _minimum_required_rows(self, rows) -> int:
        pairs = {(row.get("symbol"), row.get("timeframe")) for row in rows if row.get("symbol") and row.get("timeframe")}
        pair_count = max(1, len(pairs))
        return pair_count * MINIMUM_ROWS_PER_SYMBOL_TIMEFRAME

    def _valid_row_count(self, rows, row_issues) -> int:
        invalid_row_numbers = {
            issue.row_number
            for issue in row_issues
            if issue.row_number is not None and issue.severity == DatasetIssueSeverity.ERROR
        }
        return sum(1 for index, _row in enumerate(rows, start=2) if index not in invalid_row_numbers)

    def _recommendations(self, status, issues) -> list[str]:
        recommendations = []
        if status == HistoricalDataReadinessStatus.READY_FOR_LOCAL_IMPORT:
            recommendations.append("Dataset can move to local import testing; this is not live readiness.")
        if status == HistoricalDataReadinessStatus.INSUFFICIENT_DATA:
            recommendations.append("Use larger local historical datasets before backtesting.")
        if status == HistoricalDataReadinessStatus.NEEDS_CLEANING:
            recommendations.append("Clean warnings before using this dataset for broader PAPER_ONLY research.")
        if status == HistoricalDataReadinessStatus.INVALID_DATASET:
            recommendations.append("Fix schema or invalid row errors before local import.")
        if any(issue.code == "DUPLICATE_TIMESTAMP" for issue in issues):
            recommendations.append("Remove duplicate symbol/timeframe/timestamp rows.")
        if any(issue.code == "UNSORTED_TIMESTAMP" for issue in issues):
            recommendations.append("Sort timestamps ascending within each symbol/timeframe.")
        recommendations.append("Keep validation local; do not download market data in Sprint 13.")
        return list(dict.fromkeys(recommendations))

    def _base_price(self, symbol):
        return {"EURUSD": 1.0800, "GBPUSD": 1.2700, "USDJPY": 155.0, "XAUUSD": 2350.0}.get(symbol, 1.0)

    def _price_step(self, symbol):
        return 0.01 if symbol in {"USDJPY", "XAUUSD"} else 0.0001

    def _range_size(self, symbol):
        return 0.05 if symbol in {"USDJPY", "XAUUSD"} else 0.0005
