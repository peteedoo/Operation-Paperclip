"""Paperclip-adjacent adapter sketches (not a fork of paperclipai/paperclip)."""

from __future__ import annotations

from typing import Any

__all__ = [
    "CompanyTemplate",
    "build_company_template",
    "heartbeat_tick",
    "run_heartbeats",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from adapter import heartbeat

        return getattr(heartbeat, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
