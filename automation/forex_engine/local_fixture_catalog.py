from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


REQUIRED_FIXTURE_IDS = (
    "EURUSD_5M_TREND_SAMPLE",
    "EURUSD_5M_CHOP_SAMPLE",
    "EURUSD_5M_PULLBACK_SAMPLE",
    "EURUSD_5M_REVERSAL_SAMPLE",
    "EURUSD_5M_VOLATILE_SAMPLE",
    "EURUSD_5M_LOW_VOL_SAMPLE",
    "EURUSD_15M_TREND_SAMPLE",
    "GBPUSD_5M_TREND_SAMPLE",
    "USDJPY_5M_RANGE_SAMPLE",
)

LOCAL_FIXTURE_SOURCE = "deterministic_local_fixture"

FIXTURE_SPECS: dict[str, dict[str, Any]] = {
    "EURUSD_5M_TREND_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "trend",
        "rows": [
            ("2026-06-15T09:00:00Z", 1.1000, 1.1014, 1.0996, 1.1010, 1200),
            ("2026-06-15T09:05:00Z", 1.1010, 1.1028, 1.1008, 1.1024, 1220),
            ("2026-06-15T09:10:00Z", 1.1024, 1.1041, 1.1021, 1.1037, 1235),
            ("2026-06-15T09:15:00Z", 1.1037, 1.1052, 1.1032, 1.1048, 1245),
            ("2026-06-15T09:20:00Z", 1.1048, 1.1066, 1.1044, 1.1061, 1260),
            ("2026-06-15T09:25:00Z", 1.1061, 1.1078, 1.1059, 1.1073, 1275),
            ("2026-06-15T09:30:00Z", 1.1073, 1.1090, 1.1070, 1.1085, 1290),
            ("2026-06-15T09:35:00Z", 1.1085, 1.1101, 1.1081, 1.1096, 1305),
        ],
    },
    "EURUSD_5M_CHOP_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "chop",
        "rows": [
            ("2026-06-15T10:00:00Z", 1.1050, 1.1058, 1.1044, 1.1054, 1100),
            ("2026-06-15T10:05:00Z", 1.1054, 1.1057, 1.1042, 1.1048, 1110),
            ("2026-06-15T10:10:00Z", 1.1048, 1.1056, 1.1041, 1.1052, 1120),
            ("2026-06-15T10:15:00Z", 1.1052, 1.1055, 1.1040, 1.1046, 1115),
            ("2026-06-15T10:20:00Z", 1.1046, 1.1053, 1.1042, 1.1051, 1125),
            ("2026-06-15T10:25:00Z", 1.1051, 1.1056, 1.1043, 1.1047, 1130),
            ("2026-06-15T10:30:00Z", 1.1047, 1.1055, 1.1041, 1.1053, 1135),
            ("2026-06-15T10:35:00Z", 1.1053, 1.1058, 1.1045, 1.1049, 1140),
        ],
    },
    "EURUSD_5M_PULLBACK_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "pullback",
        "rows": [
            ("2026-06-15T11:00:00Z", 1.1010, 1.1025, 1.1007, 1.1020, 1300),
            ("2026-06-15T11:05:00Z", 1.1020, 1.1034, 1.1018, 1.1031, 1310),
            ("2026-06-15T11:10:00Z", 1.1031, 1.1037, 1.1020, 1.1024, 1320),
            ("2026-06-15T11:15:00Z", 1.1024, 1.1042, 1.1021, 1.1038, 1330),
            ("2026-06-15T11:20:00Z", 1.1038, 1.1046, 1.1028, 1.1032, 1325),
            ("2026-06-15T11:25:00Z", 1.1032, 1.1052, 1.1030, 1.1048, 1340),
            ("2026-06-15T11:30:00Z", 1.1048, 1.1061, 1.1045, 1.1056, 1350),
            ("2026-06-15T11:35:00Z", 1.1056, 1.1070, 1.1052, 1.1064, 1360),
        ],
    },
    "EURUSD_5M_REVERSAL_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "reversal",
        "rows": [
            ("2026-06-15T12:00:00Z", 1.1090, 1.1092, 1.1074, 1.1078, 1210),
            ("2026-06-15T12:05:00Z", 1.1078, 1.1081, 1.1062, 1.1066, 1220),
            ("2026-06-15T12:10:00Z", 1.1066, 1.1069, 1.1050, 1.1054, 1230),
            ("2026-06-15T12:15:00Z", 1.1054, 1.1060, 1.1049, 1.1057, 1240),
            ("2026-06-15T12:20:00Z", 1.1057, 1.1072, 1.1054, 1.1068, 1250),
            ("2026-06-15T12:25:00Z", 1.1068, 1.1084, 1.1065, 1.1080, 1260),
            ("2026-06-15T12:30:00Z", 1.1080, 1.1095, 1.1077, 1.1091, 1270),
            ("2026-06-15T12:35:00Z", 1.1091, 1.1107, 1.1088, 1.1102, 1280),
        ],
    },
    "EURUSD_5M_VOLATILE_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "volatile",
        "rows": [
            ("2026-06-15T13:00:00Z", 1.1000, 1.1035, 1.0988, 1.1028, 1800),
            ("2026-06-15T13:05:00Z", 1.1028, 1.1040, 1.0990, 1.0996, 1820),
            ("2026-06-15T13:10:00Z", 1.0996, 1.1038, 1.0989, 1.1032, 1840),
            ("2026-06-15T13:15:00Z", 1.1032, 1.1044, 1.0994, 1.1001, 1860),
            ("2026-06-15T13:20:00Z", 1.1001, 1.1048, 1.0997, 1.1040, 1880),
            ("2026-06-15T13:25:00Z", 1.1040, 1.1052, 1.1000, 1.1008, 1900),
            ("2026-06-15T13:30:00Z", 1.1008, 1.1051, 1.1002, 1.1046, 1920),
            ("2026-06-15T13:35:00Z", 1.1046, 1.1056, 1.1010, 1.1015, 1940),
        ],
    },
    "EURUSD_5M_LOW_VOL_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "regime": "low_vol",
        "rows": [
            ("2026-06-15T14:00:00Z", 1.1030, 1.1034, 1.1028, 1.1031, 900),
            ("2026-06-15T14:05:00Z", 1.1031, 1.1035, 1.1029, 1.1032, 905),
            ("2026-06-15T14:10:00Z", 1.1032, 1.1035, 1.1029, 1.1030, 910),
            ("2026-06-15T14:15:00Z", 1.1030, 1.1033, 1.1027, 1.1029, 915),
            ("2026-06-15T14:20:00Z", 1.1029, 1.1033, 1.1027, 1.1031, 920),
            ("2026-06-15T14:25:00Z", 1.1031, 1.1034, 1.1028, 1.1030, 925),
            ("2026-06-15T14:30:00Z", 1.1030, 1.1034, 1.1028, 1.1032, 930),
            ("2026-06-15T14:35:00Z", 1.1032, 1.1035, 1.1029, 1.1033, 935),
        ],
    },
    "EURUSD_15M_TREND_SAMPLE": {
        "symbol": "EURUSD",
        "timeframe": "15m",
        "regime": "trend",
        "rows": [
            ("2026-06-15T15:00:00Z", 1.0980, 1.1002, 1.0976, 1.0998, 1500),
            ("2026-06-15T15:15:00Z", 1.0998, 1.1020, 1.0995, 1.1014, 1520),
            ("2026-06-15T15:30:00Z", 1.1014, 1.1034, 1.1010, 1.1029, 1540),
            ("2026-06-15T15:45:00Z", 1.1029, 1.1052, 1.1026, 1.1047, 1560),
            ("2026-06-15T16:00:00Z", 1.1047, 1.1068, 1.1043, 1.1061, 1580),
            ("2026-06-15T16:15:00Z", 1.1061, 1.1084, 1.1058, 1.1079, 1600),
            ("2026-06-15T16:30:00Z", 1.1079, 1.1100, 1.1075, 1.1094, 1620),
            ("2026-06-15T16:45:00Z", 1.1094, 1.1117, 1.1090, 1.1111, 1640),
        ],
    },
    "GBPUSD_5M_TREND_SAMPLE": {
        "symbol": "GBPUSD",
        "timeframe": "5m",
        "regime": "trend",
        "rows": [
            ("2026-06-15T09:00:00Z", 1.2700, 1.2716, 1.2696, 1.2712, 1400),
            ("2026-06-15T09:05:00Z", 1.2712, 1.2730, 1.2709, 1.2725, 1420),
            ("2026-06-15T09:10:00Z", 1.2725, 1.2742, 1.2721, 1.2738, 1440),
            ("2026-06-15T09:15:00Z", 1.2738, 1.2754, 1.2734, 1.2750, 1460),
            ("2026-06-15T09:20:00Z", 1.2750, 1.2769, 1.2747, 1.2764, 1480),
            ("2026-06-15T09:25:00Z", 1.2764, 1.2781, 1.2760, 1.2776, 1500),
            ("2026-06-15T09:30:00Z", 1.2776, 1.2794, 1.2772, 1.2789, 1520),
            ("2026-06-15T09:35:00Z", 1.2789, 1.2806, 1.2785, 1.2801, 1540),
        ],
    },
    "USDJPY_5M_RANGE_SAMPLE": {
        "symbol": "USDJPY",
        "timeframe": "5m",
        "regime": "range",
        "rows": [
            ("2026-06-15T10:00:00Z", 155.20, 155.36, 155.12, 155.31, 1600),
            ("2026-06-15T10:05:00Z", 155.31, 155.38, 155.11, 155.18, 1610),
            ("2026-06-15T10:10:00Z", 155.18, 155.35, 155.10, 155.29, 1620),
            ("2026-06-15T10:15:00Z", 155.29, 155.37, 155.08, 155.14, 1630),
            ("2026-06-15T10:20:00Z", 155.14, 155.32, 155.06, 155.26, 1640),
            ("2026-06-15T10:25:00Z", 155.26, 155.34, 155.09, 155.16, 1650),
            ("2026-06-15T10:30:00Z", 155.16, 155.33, 155.07, 155.28, 1660),
            ("2026-06-15T10:35:00Z", 155.28, 155.39, 155.12, 155.19, 1670),
        ],
    },
}


def build_deterministic_fixture_catalog() -> dict[str, schemas.MarketDataFixture]:
    catalog = {
        fixture_id: _fixture(
            fixture_id=fixture_id,
            symbol=str(spec["symbol"]),
            timeframe=str(spec["timeframe"]),
            rows=list(spec["rows"]),
        )
        for fixture_id, spec in FIXTURE_SPECS.items()
    }
    for fixture in catalog.values():
        schemas.validate_market_fixture_schema(fixture)
    return catalog


def get_fixture_by_id(fixture_id: str) -> schemas.MarketDataFixture:
    catalog = build_deterministic_fixture_catalog()
    try:
        return catalog[fixture_id]
    except KeyError as exc:
        available = ", ".join(list_fixture_ids())
        raise KeyError(f"Unknown local fixture {fixture_id!r}; available fixtures: {available}") from exc


def list_fixture_ids() -> list[str]:
    return list(build_deterministic_fixture_catalog().keys())


def fixture_catalog_summary() -> dict[str, Any]:
    catalog = build_deterministic_fixture_catalog()
    return {
        "schema": "AIOS_FOREX_LOCAL_FIXTURE_CATALOG.v1",
        "fixture_ids": list(catalog.keys()),
        "fixture_count": len(catalog),
        "required_fixture_ids": list(REQUIRED_FIXTURE_IDS),
        "required_fixture_count": len(REQUIRED_FIXTURE_IDS),
        "symbols": sorted({fixture.symbol for fixture in catalog.values()}),
        "timeframes": sorted({fixture.timeframe for fixture in catalog.values()}),
        "regimes": sorted({fixture_regime(fixture.fixture_id) for fixture in catalog.values()}),
        "regime_summary": fixture_regime_summary(),
        "mode": schemas.LOCAL_ONLY,
        "local_python_data_only": True,
        "csv_ingestion": False,
        "file_reads": False,
        "network_allowed": False,
        "broker_allowed": False,
        "live_ready": False,
        "reports_written": False,
        "fixtures": {
            fixture_id: {
                "symbol": fixture.symbol,
                "timeframe": fixture.timeframe,
                "regime": fixture_regime(fixture_id),
                "source": fixture.source,
                "candles": len(fixture.candles),
                "network_allowed": fixture.network_allowed,
                "mode": fixture.mode,
            }
            for fixture_id, fixture in catalog.items()
        },
        "next_safe_action": "Use these deterministic local fixtures for PAPER_ONLY demos; do not infer live readiness.",
    }


def fixture_as_dict(fixture: schemas.MarketDataFixture | dict[str, Any]) -> dict[str, Any]:
    payload = asdict(fixture) if isinstance(fixture, schemas.MarketDataFixture) else dict(fixture)
    schemas.validate_market_fixture_schema(payload)
    return payload


def validate_fixture_catalog() -> dict[str, Any]:
    catalog = build_deterministic_fixture_catalog()
    quality = {
        fixture_id: fixture_quality_summary(fixture)
        for fixture_id, fixture in catalog.items()
    }
    blockers = [
        f"{fixture_id}:{blocker}"
        for fixture_id, item in quality.items()
        for blocker in item["blockers"]
    ]
    missing_required = [
        fixture_id for fixture_id in REQUIRED_FIXTURE_IDS if fixture_id not in catalog
    ]
    blockers.extend([f"missing_required_fixture:{fixture_id}" for fixture_id in missing_required])
    result = {
        "schema": "AIOS_FOREX_LOCAL_FIXTURE_CATALOG_VALIDATION.v1",
        "valid": not blockers,
        "fixture_count": len(catalog),
        "required_fixture_count": len(REQUIRED_FIXTURE_IDS),
        "quality": quality,
        "regime_summary": fixture_regime_summary(),
        "blockers": blockers,
        "local_only": True,
        "network_allowed": False,
        "broker_allowed": False,
        "reports_written": False,
        "files_written": [],
    }
    schemas.assert_no_live_permissions(result)
    return result


def fixture_regime_summary() -> dict[str, Any]:
    catalog = build_deterministic_fixture_catalog()
    regimes: dict[str, dict[str, Any]] = {}
    for fixture_id, fixture in catalog.items():
        regime = fixture_regime(fixture_id)
        item = regimes.setdefault(
            regime,
            {
                "fixture_count": 0,
                "fixture_ids": [],
                "symbols": [],
                "timeframes": [],
            },
        )
        item["fixture_count"] += 1
        item["fixture_ids"].append(fixture_id)
        if fixture.symbol not in item["symbols"]:
            item["symbols"].append(fixture.symbol)
        if fixture.timeframe not in item["timeframes"]:
            item["timeframes"].append(fixture.timeframe)

    return {
        "schema": "AIOS_FOREX_LOCAL_FIXTURE_REGIME_SUMMARY.v1",
        "total_regimes": len(regimes),
        "regimes": regimes,
        "local_only": True,
        "network_allowed": False,
        "broker_allowed": False,
    }


def fixture_quality_summary(fixture: schemas.MarketDataFixture | dict[str, Any]) -> dict[str, Any]:
    active_fixture = _coerce_fixture(fixture)
    blockers: list[str] = []
    try:
        schemas.validate_market_fixture_schema(active_fixture)
    except ValueError as exc:
        blockers.append(f"schema_invalid:{exc}")
    if active_fixture.mode not in {schemas.LOCAL_ONLY, schemas.PAPER_ONLY}:
        blockers.append("mode_not_local_or_paper")
    if active_fixture.network_allowed is not False:
        blockers.append("network_allowed_true")
    if "broker" in active_fixture.source.lower():
        blockers.append("broker_source_detected")
    if active_fixture.source != LOCAL_FIXTURE_SOURCE:
        blockers.append("source_not_deterministic_local_fixture")
    if len(active_fixture.candles) < 8:
        blockers.append("too_few_candles_for_demo")
    if not _valid_ohlc_sequence(active_fixture):
        blockers.append("invalid_ohlc_sequence")

    summary = {
        "schema": "AIOS_FOREX_LOCAL_FIXTURE_QUALITY.v1",
        "fixture_id": active_fixture.fixture_id,
        "symbol": active_fixture.symbol,
        "timeframe": active_fixture.timeframe,
        "source": active_fixture.source,
        "regime": fixture_regime(active_fixture.fixture_id),
        "candle_count": len(active_fixture.candles),
        "local_only": active_fixture.mode in {schemas.LOCAL_ONLY, schemas.PAPER_ONLY}
        and active_fixture.network_allowed is False,
        "valid_ohlc_sequence": _valid_ohlc_sequence(active_fixture),
        "network_allowed": active_fixture.network_allowed,
        "broker_source": "broker" in active_fixture.source.lower(),
        "mode": active_fixture.mode,
        "valid": not blockers,
        "blockers": blockers,
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def assert_fixture_is_local_only(fixture: schemas.MarketDataFixture | dict[str, Any]) -> None:
    quality = fixture_quality_summary(fixture)
    if not quality["valid"]:
        raise ValueError(f"Fixture is not valid local-only evidence: {quality['blockers']}")


def fixture_regime(fixture_id: str) -> str:
    return str(FIXTURE_SPECS.get(fixture_id, {}).get("regime") or "unknown")


def _fixture(
    fixture_id: str,
    symbol: str,
    timeframe: str,
    rows: list[tuple[str, float, float, float, float, int]],
) -> schemas.MarketDataFixture:
    fixture = schemas.MarketDataFixture(
        fixture_id=fixture_id,
        symbol=symbol,
        timeframe=timeframe,
        source=LOCAL_FIXTURE_SOURCE,
        candles=[
            schemas.Candle(
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                source=LOCAL_FIXTURE_SOURCE,
            )
            for timestamp, open_price, high, low, close, volume in rows
        ],
        mode=schemas.LOCAL_ONLY,
        network_allowed=False,
    )
    schemas.validate_market_fixture_schema(fixture)
    return fixture


def _coerce_fixture(value: schemas.MarketDataFixture | dict[str, Any]) -> schemas.MarketDataFixture:
    if isinstance(value, schemas.MarketDataFixture):
        return value
    payload = asdict(value) if is_dataclass(value) else dict(value)
    candles = [
        candle if isinstance(candle, schemas.Candle) else schemas.Candle(**dict(candle))
        for candle in payload.get("candles", [])
    ]
    return schemas.MarketDataFixture(
        fixture_id=str(payload["fixture_id"]),
        symbol=str(payload["symbol"]),
        timeframe=str(payload["timeframe"]),
        source=str(payload["source"]),
        candles=candles,
        mode=str(payload.get("mode", schemas.LOCAL_ONLY)),
        network_allowed=bool(payload.get("network_allowed", False)),
    )


def _valid_ohlc_sequence(fixture: schemas.MarketDataFixture) -> bool:
    return all(
        candle.low <= candle.open <= candle.high
        and candle.low <= candle.close <= candle.high
        and candle.high >= candle.low
        for candle in fixture.candles
    )
