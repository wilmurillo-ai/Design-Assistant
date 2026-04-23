import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(ROOT))

from industry_compare_analyzer import IndustryCompareAnalyzer, IndustryContext


class StubFetcher:
    def __init__(self, funds: pd.DataFrame):
        self._funds = funds

    def get_all_funds(self):
        return self._funds.copy()


class StubIndustryAnalyzer(IndustryCompareAnalyzer):
    def _build_candidate(self, context, fund_info):
        return {
            "ts_code": fund_info["ts_code"],
            "name": fund_info["name"],
            "aum": 10.0,
            "fund_info": fund_info,
            "manager": pd.Series({"name": "经理"}),
            "tenure_years": 2.0,
            "nav_df": pd.DataFrame({"adjusted_nav": [1, 2]}),
            "sharpe": 1.0,
        }


def make_funds(names):
    return pd.DataFrame(
        [
            {
                "ts_code": f"{i:06d}.OF",
                "name": name,
                "benchmark": "",
                "fund_type": "股票型",
                "invest_type": "偏股混合型",
                "found_date": "20200101",
                "issue_amount": 10.0,
            }
            for i, name in enumerate(names, start=1)
        ]
    )


def test_screen_funds_prefers_strict_keyword_matches():
    funds = make_funds(["云计算先锋", "云计算成长", "云计算精选", "人工智能主题", "软件创新"])
    analyzer = StubIndustryAnalyzer(StubFetcher(funds))
    context = IndustryContext(input_name="云计算", canonical_name="计算机", index_code="801750.SI")

    candidates = analyzer._screen_funds(context)

    assert len(candidates) == 3
    assert all("云计算" in item["name"] for item in candidates)


def test_screen_funds_falls_back_to_alias_matches_when_strict_matches_insufficient():
    funds = make_funds(["云计算先锋", "人工智能主题", "软件创新", "信创成长"])
    analyzer = StubIndustryAnalyzer(StubFetcher(funds))
    context = IndustryContext(input_name="云计算", canonical_name="计算机", index_code="801750.SI")

    candidates = analyzer._screen_funds(context)

    names = [item["name"] for item in candidates]
    assert "云计算先锋" in names
    assert any(name in names for name in ["人工智能主题", "软件创新", "信创成长"])
