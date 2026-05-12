"""AIOS Trader Module v0.1.

Local paper-only trading kernel. No live broker integration is provided here.
"""

from aios.modules.trader.config import TraderConfig
from aios.modules.trader.trader import TraderEngine

__all__ = ["TraderConfig", "TraderEngine"]
