import numpy as np
import pytest
from src.fifi import MarketStatRepository
from src.fifi.enums import Market
from src.fifi.enums.market import MarketStat


@pytest.fixture
def create_repo():
    repo = MarketStatRepository(market=Market.BTCUSD_PERP, interval="1m", create=True)
    yield repo
    repo.close()


class TestMarketDataRepository:
    def test_stat(self, create_repo):
        repo: MarketStatRepository = create_repo
        data = np.arange(repo._rows * repo._columns).reshape(repo._rows, repo._columns)
        repo._data = data
        repo._data.dtype = np.double

        rsi14 = repo.get_last_stat(MarketStat.RSI14)
        assert rsi14 == data[-1, MarketStat.RSI14.value]

        repo.set_last_stat(MarketStat.RSI14, 55.6)
        rsi14 = repo.get_last_stat(MarketStat.RSI14)
        assert rsi14 == 55.6
