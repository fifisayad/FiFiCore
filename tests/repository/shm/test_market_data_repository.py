import numpy as np
import pytest
from src.fifi import MarketDataRepository
from src.fifi.enums import Market
from src.fifi.enums.market import MarketData


@pytest.fixture
def create_repo():
    repo = MarketDataRepository(market=Market.BTCUSD_PERP, interval="1m", create=True)
    yield repo
    repo.close()


class TestMarketDataRepository:
    def test_get_methods(self, create_repo):
        repo: MarketDataRepository = create_repo
        data = np.arange(repo._rows * repo._columns).reshape(repo._rows, repo._columns)
        repo._data = data

        closes = repo.get_closes()
        assert np.array_equal(closes, data[:, MarketData.CLOSE.value])

        opens = repo.get_opens()
        assert np.array_equal(opens, data[:, MarketData.OPEN.value])

        highs = repo.get_highs()
        assert np.array_equal(highs, data[:, MarketData.HIGH.value])

        lows = repo.get_lows()
        assert np.array_equal(lows, data[:, MarketData.LOW.value])

        vols = repo.get_vols()
        assert np.array_equal(vols, data[:, MarketData.VOL.value])

        time = repo.get_time()
        assert time == data[-1, MarketData.TIME.value]

        trade = repo.get_last_trade()
        assert trade == data[-1, MarketData.PRICE.value]
