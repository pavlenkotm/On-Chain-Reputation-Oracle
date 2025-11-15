from __future__ import annotations

from ocro.scoring import ScoringEngine, calculate_reputation_score


class DummyProvider:
    def __init__(self, age: float, tx: int, volume: float, contracts: int) -> None:
        self.age = age
        self.tx = tx
        self.volume = volume
        self.contracts = contracts

    def get_wallet_age_days(self, address: str) -> float:  # pragma: no cover - trivial
        return self.age

    def get_transaction_count(self, address: str) -> int:  # pragma: no cover
        return self.tx

    def get_total_volume_eth(self, address: str) -> float:  # pragma: no cover
        return self.volume

    def get_unique_contracts_interacted(self, address: str) -> int:  # pragma: no cover
        return self.contracts


SAMPLE_ADDRESS = "0x000000000000000000000000000000000000dEaD"


def test_calculate_reputation_score_bounds():
    score = calculate_reputation_score(SAMPLE_ADDRESS)
    assert isinstance(score, int)
    assert 0 <= score <= 1000


def test_scoring_weights_applied_correctly():
    provider = DummyProvider(age=365, tx=0, volume=0, contracts=0)
    engine = ScoringEngine(provider=provider)  # only age contributes -> 0.25
    result = engine.calculate(SAMPLE_ADDRESS)
    assert result.score == 250

    provider = DummyProvider(age=365, tx=1000, volume=100, contracts=50)
    engine = ScoringEngine(provider=provider)
    result = engine.calculate(SAMPLE_ADDRESS)
    assert result.score == 1000
