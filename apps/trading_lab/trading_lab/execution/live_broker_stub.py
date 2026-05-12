from __future__ import annotations


def place_order(*args, **kwargs):
    raise RuntimeError("LIVE_BROKER_DISABLED: paper mode only")


def cancel_order(*args, **kwargs):
    raise RuntimeError("LIVE_BROKER_DISABLED: paper mode only")


def connect(*args, **kwargs):
    raise RuntimeError("LIVE_BROKER_DISABLED: paper mode only")
