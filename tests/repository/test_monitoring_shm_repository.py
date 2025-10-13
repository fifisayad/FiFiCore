import numpy as np
import pytest

from src.fifi.enums import Market, MarketStat
from src.fifi import MonitoringSHMRepository


@pytest.fixture
def monitoring_creator_repo():
    repo = MonitoringSHMRepository(
        create=True,
        markets=[
            Market.BTCUSD_PERP,
            Market.ETHUSD,
            Market.BTCUSD,
            Market.ETHUSD_PERP,
        ],
    )
    yield repo
    repo.close()


@pytest.fixture
def monitoring_reader_repo():
    repo = MonitoringSHMRepository(
        create=False,
        markets=[
            Market.BTCUSD_PERP,
            Market.ETHUSD,
            Market.BTCUSD,
            Market.ETHUSD_PERP,
        ],
    )
    yield repo


@pytest.mark.asyncio
class TestMonitoringSHMRepository:

    def test_set_stat(self, monitoring_creator_repo):
        repo: MonitoringSHMRepository = monitoring_creator_repo
        repo.set_stat(market=Market.BTCUSD, stat=MarketStat.PRICE, value=1200)
        repo.set_stat(market=Market.ETHUSD, stat=MarketStat.PRICE, value=140)

        assert repo.stats[repo.row_index[Market.BTCUSD]][MarketStat.PRICE.value] == 1200
        assert repo.stats[repo.row_index[Market.ETHUSD]][MarketStat.PRICE.value] == 140

    def test_set_reader_error(self, monitoring_creator_repo, monitoring_reader_repo):
        creator_repo: MonitoringSHMRepository = monitoring_creator_repo
        creator_repo.set_stat(market=Market.BTCUSD, stat=MarketStat.PRICE, value=1200)
        creator_repo.set_stat(market=Market.ETHUSD, stat=MarketStat.PRICE, value=140)

        reader_repo: MonitoringSHMRepository = monitoring_reader_repo
        with pytest.raises(Exception):
            reader_repo.set_stat(
                market=Market.BTCUSD, stat=MarketStat.PRICE, value=1200
            )
        with pytest.raises(Exception):
            reader_repo.set_close_prices(
                market=Market.BTCUSD, close_prices=np.zeros(20)
            )
        with pytest.raises(Exception):
            reader_repo.set_current_candle_time(market=Market.ETHUSD, value=321432)
        with pytest.raises(Exception):
            reader_repo.set_last_trade(market=Market.ETHUSD, value=321432)
        with pytest.raises(Exception):
            reader_repo.set_is_updated(market=Market.ETHUSD)
        with pytest.raises(Exception):
            reader_repo.clear_is_updated(market=Market.ETHUSD)

    def test_is_updated(self, monitoring_creator_repo, monitoring_reader_repo):
        creator_repo: MonitoringSHMRepository = monitoring_creator_repo
        creator_repo.set_is_updated(market=Market.BTCUSD)
        assert creator_repo.is_updated(Market.BTCUSD)
        assert not creator_repo.is_updated(Market.ETHUSD)

        creator_repo.clear_is_updated(Market.BTCUSD)
        assert not creator_repo.is_updated(Market.BTCUSD)

    def test_set_close_prices(self, monitoring_creator_repo, monitoring_reader_repo):
        creator_repo: MonitoringSHMRepository = monitoring_creator_repo
        with pytest.raises(ValueError):
            creator_repo.set_close_prices(Market.BTCUSD, np.zeros(20))

        reader_repo: MonitoringSHMRepository = monitoring_reader_repo
        creator_repo.set_close_prices(Market.BTCUSD, np.arange(200))
        assert np.array_equal(
            np.arange(200), reader_repo.get_close_prices(Market.BTCUSD)
        )
