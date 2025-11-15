"""Ethereum chain data provider."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
from typing import Optional

from ..config import get_config

try:  # pragma: no cover - optional dependency
    from web3 import HTTPProvider, Web3
except Exception:  # pragma: no cover
    HTTPProvider = Web3 = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ProviderStats:
    """Wrapper around provider metadata."""

    mock_mode: bool
    rpc_url: str | None


class EthereumProvider:
    """Simple provider that fetches wallet metrics from Ethereum."""

    def __init__(
        self,
        *,
        rpc_url: str | None = None,
        mock_mode: Optional[bool] = None,
    ) -> None:
        config = get_config()
        self.rpc_url = rpc_url or config.eth_rpc_url
        derived_mock = config.mock_mode or not self.rpc_url
        self.mock_mode = mock_mode if mock_mode is not None else derived_mock
        self.web3: Web3 | None = None
        if not self.mock_mode and Web3 is not None and self.rpc_url:
            try:
                self.web3 = Web3(HTTPProvider(self.rpc_url, request_kwargs={"timeout": 10}))
            except Exception as exc:  # pragma: no cover - network setup
                logger.warning("Failed to initialize Web3 provider, falling back to mock mode: %s", exc)
                self.web3 = None
                self.mock_mode = True
        else:
            if not self.mock_mode:
                logger.warning("Web3 not available, enabling mock mode")
            self.mock_mode = True

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def stats(self) -> ProviderStats:
        """Return current provider metadata."""

        return ProviderStats(mock_mode=self.mock_mode, rpc_url=self.rpc_url)

    def get_wallet_age_days(self, address: str) -> float:
        """Return approximate wallet age in days."""

        if self.mock_mode or not self.web3:
            return self._mock_value(address, "age", 30.0, 800.0)

        try:
            tx_count = self.web3.eth.get_transaction_count(address)
            if tx_count == 0:
                return 0.0
            latest_block = self.web3.eth.block_number
            first_block = self._estimate_first_tx_block(address, latest_block)
            latest_ts = int(self.web3.eth.get_block(latest_block)["timestamp"])
            first_ts = int(self.web3.eth.get_block(first_block)["timestamp"])
            return max(0.0, (latest_ts - first_ts) / 86400)
        except Exception as exc:  # pragma: no cover - network variability
            logger.warning("Failed to determine wallet age: %s", exc)
            return 0.0

    def get_transaction_count(self, address: str) -> int:
        """Return the number of transactions sent by the address."""

        if self.mock_mode or not self.web3:
            return int(self._mock_value(address, "tx", 0, 1500))

        try:
            return int(self.web3.eth.get_transaction_count(address))
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to get transaction count: %s", exc)
            return 0

    def get_total_volume_eth(self, address: str) -> float:
        """Return an approximate total ETH volume moved by the address."""

        if self.mock_mode or not self.web3:
            return self._mock_value(address, "volume", 0.5, 120.0)

        try:
            balance_wei = self.web3.eth.get_balance(address)
            tx_count = max(1, self.get_transaction_count(address))
            balance_eth = balance_wei / 10**18
            return balance_eth + tx_count * 0.01
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to get total volume: %s", exc)
            return 0.0

    def get_unique_contracts_interacted(self, address: str) -> int:
        """Return a heuristic for contract diversity."""

        if self.mock_mode or not self.web3:
            return int(self._mock_value(address, "contracts", 1, 60))

        try:
            tx_count = self.get_transaction_count(address)
            return int(min(100, tx_count // 2))
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to get contract diversity: %s", exc)
            return 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _mock_value(self, address: str, namespace: str, min_value: float, max_value: float) -> float:
        seed = f"{namespace}:{address.lower()}".encode()
        digest = hashlib.sha256(seed).hexdigest()
        value = int(digest[:8], 16) / 0xFFFFFFFF
        return min_value + (max_value - min_value) * value

    def _estimate_first_tx_block(self, address: str, latest_block: int) -> int:
        """Approximate the block number of the first transaction."""

        assert self.web3 is not None
        low = 0
        high = latest_block
        first_nonzero = latest_block
        while low <= high:
            mid = (low + high) // 2
            count = self.web3.eth.get_transaction_count(address, mid)
            if count > 0:
                first_nonzero = mid
                high = mid - 1
            else:
                low = mid + 1
        return first_nonzero


__all__ = ["EthereumProvider", "ProviderStats"]
