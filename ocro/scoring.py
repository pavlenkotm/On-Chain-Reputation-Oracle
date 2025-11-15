"""Reputation scoring logic."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Tuple

from .chains import EthereumProvider
from .metrics import MetricResult, aggregate_metrics, normalize_value

logger = logging.getLogger(__name__)

AGE_WEIGHT = 0.25
TX_WEIGHT = 0.25
VOLUME_WEIGHT = 0.30
DIVERSITY_WEIGHT = 0.20


@dataclass
class ScoreDetails:
    """Detailed breakdown of a score calculation."""

    score: int
    metrics: Tuple[MetricResult, ...]

    def to_dict(self) -> Dict[str, float]:
        """Serialize the metric breakdown."""

        return {metric.name: metric.value for metric in self.metrics}


class ScoringEngine:
    """Engine that calculates wallet reputation scores."""

    def __init__(self, provider: EthereumProvider | None = None) -> None:
        self.provider = provider or EthereumProvider()

    def calculate(self, address: str) -> ScoreDetails:
        """Calculate the score and return detailed results."""

        provider = self.provider
        wallet_age_days = provider.get_wallet_age_days(address)
        tx_count = provider.get_transaction_count(address)
        total_volume_eth = provider.get_total_volume_eth(address)
        contract_diversity = provider.get_unique_contracts_interacted(address)

        metrics = (
            MetricResult(
                name="wallet_age_days",
                value=wallet_age_days,
                weight=AGE_WEIGHT,
                normalized_value=normalize_value(wallet_age_days, 365.0),
            ),
            MetricResult(
                name="transaction_count",
                value=tx_count,
                weight=TX_WEIGHT,
                normalized_value=normalize_value(tx_count, 1000.0),
            ),
            MetricResult(
                name="total_volume_eth",
                value=total_volume_eth,
                weight=VOLUME_WEIGHT,
                normalized_value=normalize_value(total_volume_eth, 100.0),
            ),
            MetricResult(
                name="unique_contracts",
                value=contract_diversity,
                weight=DIVERSITY_WEIGHT,
                normalized_value=normalize_value(contract_diversity, 50.0),
            ),
        )

        normalized_score = aggregate_metrics(metrics)
        final_score = int(normalized_score * 1000)
        logger.debug("Score for %s: %s", address, final_score)
        return ScoreDetails(score=final_score, metrics=metrics)


def calculate_reputation_score(address: str) -> int:
    """Public helper that returns the reputation score for an address."""

    engine = ScoringEngine()
    return engine.calculate(address).score


__all__ = ["calculate_reputation_score", "ScoringEngine", "ScoreDetails"]
