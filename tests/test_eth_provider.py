from __future__ import annotations

import os

import pytest

from ocro.chains.eth import EthereumProvider
from ocro import config

ADDRESS = "0x000000000000000000000000000000000000dEaD"


@pytest.fixture(autouse=True)
def reset_config(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("OCRO_ETH_RPC_URL", raising=False)
    monkeypatch.delenv("OCRO_MOCK_MODE", raising=False)
    config.get_config.cache_clear()
    yield
    config.get_config.cache_clear()


def test_mock_mode_returns_values():
    provider = EthereumProvider(mock_mode=True)
    assert provider.stats().mock_mode
    assert provider.get_transaction_count(ADDRESS) >= 0
    assert provider.get_wallet_age_days(ADDRESS) >= 0
    assert provider.get_total_volume_eth(ADDRESS) >= 0


def test_mock_mode_without_rpc(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OCRO_MOCK_MODE", "true")
    provider = EthereumProvider()
    assert provider.mock_mode
    assert provider.get_unique_contracts_interacted(ADDRESS) >= 0
