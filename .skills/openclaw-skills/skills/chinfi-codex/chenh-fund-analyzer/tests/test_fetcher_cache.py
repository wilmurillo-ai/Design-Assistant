import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))

from fund_data_fetcher import FundDataFetcher


class StubPro:
    def __init__(self):
        self.calls = 0

    def fund_basic(self, **kwargs):
        self.calls += 1
        return pd.DataFrame([{"ts_code": "000001.OF", **kwargs}])


def test_request_cache_reuses_same_response_without_extra_call():
    fetcher = FundDataFetcher.__new__(FundDataFetcher)
    fetcher.pro = StubPro()
    fetcher._request_cache = {}
    fetcher._last_request_ts = 0.0
    fetcher._min_interval = 0.0
    fetcher._cache_ttl_seconds = 300

    first = fetcher._request("fund_basic", ttl_seconds=300, market="E")
    second = fetcher._request("fund_basic", ttl_seconds=300, market="E")

    assert fetcher.pro.calls == 1
    assert first.equals(second)
