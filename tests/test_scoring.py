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


def test_batch_calculation_deduplicates_addresses():
    class TrackingProvider(DummyProvider):
        def __init__(self):
            super().__init__(age=365, tx=1000, volume=100, contracts=50)
            self.age_calls = 0

        def get_wallet_age_days(self, address: str) -> float:  # pragma: no cover - simple
            self.age_calls += 1
            return super().get_wallet_age_days(address)

    provider = TrackingProvider()
    engine = ScoringEngine(provider=provider)
    addresses = [SAMPLE_ADDRESS, SAMPLE_ADDRESS, "0x1111111111111111111111111111111111111111"]

    results = engine.calculate_many(addresses)

    assert len(results) == 2
    assert provider.age_calls == 2  # only two unique addresses should be fetched


def test_rank_addresses_orders_by_score():
    low = DummyProvider(age=10, tx=1, volume=0.1, contracts=1)
    mid = DummyProvider(age=100, tx=100, volume=10, contracts=10)
    high = DummyProvider(age=365, tx=1000, volume=100, contracts=50)

    class SequencedProvider(DummyProvider):
        def __init__(self):
            super().__init__(age=0, tx=0, volume=0, contracts=0)
            self.calls = []

        def configure(self, other: DummyProvider) -> None:
            self.age = other.age
            self.tx = other.tx
            self.volume = other.volume
            self.contracts = other.contracts

        def get_wallet_age_days(self, address: str) -> float:  # pragma: no cover - simple
            provider = providers[address]
            return provider.get_wallet_age_days(address)

        def get_transaction_count(self, address: str) -> int:  # pragma: no cover - simple
            provider = providers[address]
            return provider.get_transaction_count(address)

        def get_total_volume_eth(self, address: str) -> float:  # pragma: no cover - simple
            provider = providers[address]
            return provider.get_total_volume_eth(address)

        def get_unique_contracts_interacted(self, address: str) -> int:  # pragma: no cover - simple
            provider = providers[address]
            return provider.get_unique_contracts_interacted(address)

    providers = {
        "0x1": low,
        "0x2": mid,
        "0x3": high,
    }

    engine = ScoringEngine(provider=SequencedProvider())
    ranking = engine.rank_addresses(providers.keys())
    assert [address for address, _ in ranking] == ["0x3", "0x2", "0x1"]
