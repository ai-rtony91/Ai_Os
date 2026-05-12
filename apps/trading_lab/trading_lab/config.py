from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PACKAGE_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "trading_lab.db"


class Settings(BaseModel):
    mode: str = Field(default="paper")
    db_url: str = Field(default=f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
    risk_fraction: float = Field(default=0.01)
    reward_risk: float = Field(default=2.0)
    live_broker_enabled: bool = Field(default=False)

    def assert_paper_mode(self) -> None:
        if self.mode.lower() != "paper" or self.live_broker_enabled:
            raise RuntimeError("LIVE_BROKER_DISABLED: paper mode only")


def load_settings() -> Settings:
    load_dotenv(PACKAGE_ROOT / ".env")
    settings = Settings(
        mode=os.getenv("TRADING_LAB_MODE", "paper"),
        db_url=os.getenv("TRADING_LAB_DB_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"),
        risk_fraction=float(os.getenv("TRADING_LAB_RISK_FRACTION", "0.01")),
        reward_risk=float(os.getenv("TRADING_LAB_REWARD_RISK", "2.0")),
        live_broker_enabled=os.getenv("LIVE_BROKER_ENABLED", "false").lower() == "true",
    )
    settings.assert_paper_mode()
    return settings
