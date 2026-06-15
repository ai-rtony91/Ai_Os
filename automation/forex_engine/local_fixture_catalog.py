from __future__ import annotations

from dataclasses import asdict
from typing import Any

from automation.forex_engine import schema_contracts as schemas


REQUIRED_FIXTURE_IDS = (
    "EURUSD_5M_TREND_SAMPLE",
    "EURUSD_5M_CHOP_SAMPLE",
    "EURUSD_5M_PULLBACK_SAMPLE",
)


def build_deterministic_fixture_catalog() -> dict[str, schemas.MarketDataFixture]:
    catalog = {
        "EURUSD_5M_TREND_SAMPLE": _fixture(
            "EURUSD_5M_TREND_SAMPLE",
            [
                ("2026-06-15T09:00:00Z", 1.1000, 1.1014, 1.0996, 1.1010, 1200),
                ("2026-06-15T09:05:00Z", 1.1010, 1.1028, 1.1008, 1.1024, 1220),
                ("2026-06-15T09:10:00Z", 1.1024, 1.1041, 1.1021, 1.1037, 1235),
                ("2026-06-15T09:15:00Z", 1.1037, 1.1052, 1.1032, 1.1048, 1245),
                ("2026-06-15T09:20:00Z", 1.1048, 1.1066, 1.1044, 1.1061, 1260),
                ("2026-06-15T09:25:00Z", 1.1061, 1.1078, 1.1059, 1.1073, 1275),
                ("2026-06-15T09:30:00Z", 1.1073, 1.1090, 1.1070, 1.1085, 1290),
                ("2026-06-15T09:35:00Z", 1.1085, 1.1101, 1.1081, 1.1096, 1305),
            ],
        ),
        "EURUSD_5M_CHOP_SAMPLE": _fixture(
            "EURUSD_5M_CHOP_SAMPLE",
            [
                ("2026-06-15T10:00:00Z", 1.1050, 1.1058, 1.1044, 1.1054, 1100),
                ("2026-06-15T10:05:00Z", 1.1054, 1.1057, 1.1042, 1.1048, 1110),
                ("2026-06-15T10:10:00Z", 1.1048, 1.1056, 1.1041, 1.1052, 1120),
                ("2026-06-15T10:15:00Z", 1.1052, 1.1055, 1.1040, 1.1046, 1115),
                ("2026-06-15T10:20:00Z", 1.1046, 1.1053, 1.1042, 1.1051, 1125),
                ("2026-06-15T10:25:00Z", 1.1051, 1.1056, 1.1043, 1.1047, 1130),
                ("2026-06-15T10:30:00Z", 1.1047, 1.1055, 1.1041, 1.1053, 1135),
                ("2026-06-15T10:35:00Z", 1.1053, 1.1058, 1.1045, 1.1049, 1140),
            ],
        ),
        "EURUSD_5M_PULLBACK_SAMPLE": _fixture(
            "EURUSD_5M_PULLBACK_SAMPLE",
            [
                ("2026-06-15T11:00:00Z", 1.1010, 1.1025, 1.1007, 1.1020, 1300),
                ("2026-06-15T11:05:00Z", 1.1020, 1.1034, 1.1018, 1.1031, 1310),
                ("2026-06-15T11:10:00Z", 1.1031, 1.1037, 1.1020, 1.1024, 1320),
                ("2026-06-15T11:15:00Z", 1.1024, 1.1042, 1.1021, 1.1038, 1330),
                ("2026-06-15T11:20:00Z", 1.1038, 1.1046, 1.1028, 1.1032, 1325),
                ("2026-06-15T11:25:00Z", 1.1032, 1.1052, 1.1030, 1.1048, 1340),
                ("2026-06-15T11:30:00Z", 1.1048, 1.1061, 1.1045, 1.1056, 1350),
                ("2026-06-15T11:35:00Z", 1.1056, 1.1070, 1.1052, 1.1064, 1360),
            ],
        ),
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
        "symbols": sorted({fixture.symbol for fixture in catalog.values()}),
        "timeframes": sorted({fixture.timeframe for fixture in catalog.values()}),
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


def _fixture(fixture_id: str, rows: list[tuple[str, float, float, float, float, int]]) -> schemas.MarketDataFixture:
    fixture = schemas.MarketDataFixture(
        fixture_id=fixture_id,
        symbol="EURUSD",
        timeframe="5m",
        source="deterministic_python_fixture_catalog",
        candles=[
            schemas.Candle(
                timestamp=timestamp,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                source="deterministic_python_fixture_catalog",
            )
            for timestamp, open_price, high, low, close, volume in rows
        ],
        mode=schemas.LOCAL_ONLY,
        network_allowed=False,
    )
    schemas.validate_market_fixture_schema(fixture)
    return fixture
