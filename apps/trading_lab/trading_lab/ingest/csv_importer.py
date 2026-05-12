from __future__ import annotations

from hashlib import sha256
from pathlib import Path

import pandas as pd
from sqlalchemy.dialects.sqlite import insert

from ..database import session_scope
from ..models import Candle, ImportedFile


COLUMN_ALIASES = {
    "time": "timestamp",
    "date": "timestamp",
    "datetime": "timestamp",
    "ticker": "symbol",
    "pair": "symbol",
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "vol": "volume",
}

REQUIRED_COLUMNS = ["timestamp", "symbol", "timeframe", "open", "high", "low", "close", "volume"]


def file_hash(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_market_file(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        frame = pd.read_csv(file_path)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        frame = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported import type: {suffix}")
    return normalize_candles(frame)


def normalize_candles(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for column in frame.columns:
        normalized = str(column).strip().lower().replace(" ", "_")
        renamed[column] = COLUMN_ALIASES.get(normalized, normalized)
    frame = frame.rename(columns=renamed)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required candle columns: {', '.join(missing)}")
    frame = frame[REQUIRED_COLUMNS].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True).dt.tz_localize(None)
    frame["symbol"] = frame["symbol"].astype(str)
    frame["timeframe"] = frame["timeframe"].astype(str)
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame.sort_values(["symbol", "timeframe", "timestamp"])


def import_market_file(path: str | Path) -> dict:
    file_path = Path(path)
    digest = file_hash(file_path)
    frame = read_market_file(file_path)

    with session_scope() as session:
        existing = session.query(ImportedFile).filter_by(file_hash=digest).one_or_none()
        if existing:
            return {"status": "duplicate", "file_hash": digest, "rows": existing.row_count}
        imported = ImportedFile(file_path=str(file_path), file_hash=digest, row_count=len(frame))
        session.add(imported)
        session.flush()
        rows = [
            {
                "timestamp": row.timestamp,
                "symbol": row.symbol,
                "timeframe": row.timeframe,
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": float(row.volume),
                "imported_file_id": imported.id,
            }
            for row in frame.itertuples(index=False)
        ]
        if rows:
            statement = insert(Candle).values(rows)
            statement = statement.on_conflict_do_nothing(
                index_elements=["timestamp", "symbol", "timeframe"]
            )
            session.execute(statement)
        return {"status": "imported", "file_hash": digest, "rows": len(frame)}
