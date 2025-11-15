"""Configuration helpers for OCRO."""
from __future__ import annotations

from dataclasses import dataclass
import os
from functools import lru_cache


@dataclass(frozen=True)
class Config:
    """Runtime configuration for the application."""

    eth_rpc_url: str | None
    mock_mode: bool


def _str_to_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Return the cached configuration populated from environment variables."""

    eth_rpc_url = os.getenv("OCRO_ETH_RPC_URL")
    mock_mode = _str_to_bool(os.getenv("OCRO_MOCK_MODE"))
    return Config(eth_rpc_url=eth_rpc_url, mock_mode=mock_mode)


__all__ = ["Config", "get_config"]
