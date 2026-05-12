from __future__ import annotations

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from .backtest.engine import run_backtest
from .backtest.walk_forward import run_walk_forward
from .database import init_db, session_scope
from .ingest.csv_importer import import_market_file
from .models import BacktestRun, Candle, Signal, StrategyMetric


app = typer.Typer(help="AI_OS Trading Lab paper-only CLI.")
console = Console()


@app.command("init-db")
def init_database() -> None:
    init_db()
    console.print("[green]Trading Lab SQLite database initialized.[/green]")
    console.print("[yellow]Live broker execution remains BLOCKED.[/yellow]")


@app.command("import-file")
def import_file(path: str) -> None:
    init_db()
    result = import_market_file(path)
    console.print(result)


@app.command("backtest")
def backtest(symbol: str = "EUR_USD", timeframe: str = "M5", start_date: str | None = None, end_date: str | None = None) -> None:
    init_db()
    console.print(run_backtest(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date))


@app.command("walk-forward")
def walk_forward(symbol: str = "EUR_USD", timeframe: str = "M5", windows: int = 3) -> None:
    init_db()
    console.print(run_walk_forward(symbol=symbol, timeframe=timeframe, windows=windows))


@app.command("serve-webhooks")
def serve_webhooks(host: str = "127.0.0.1", port: int = 8765) -> None:
    init_db()
    console.print("[yellow]Serving paper-only webhooks. Live execution remains BLOCKED.[/yellow]")
    uvicorn.run("trading_lab.ingest.webhook_server:app", host=host, port=port, reload=False)


@app.command("report")
def report() -> None:
    init_db()
    with session_scope() as session:
        table = Table(title="AI_OS Trading Lab Paper Report")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Candles", str(session.query(Candle).count()))
        table.add_row("Signals", str(session.query(Signal).count()))
        table.add_row("Backtest runs", str(session.query(BacktestRun).count()))
        latest = session.query(StrategyMetric).order_by(StrategyMetric.created_at.desc()).first()
        table.add_row("Latest expectancy", str(latest.expectancy if latest else "N/A"))
        table.add_row("Live execution", "BLOCKED")
        console.print(table)


if __name__ == "__main__":
    app()
