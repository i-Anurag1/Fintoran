import sys
import types

from tools import market_tools


class FakeFastInfo(dict):
    pass


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.fast_info = FakeFastInfo({
            "lastPrice": 190.5,
            "previousClose": 188.0,
            "dayHigh": 192.0,
            "dayLow": 187.5,
            "currency": "USD",
        })
        self.recommendations = None


def test_get_stock_price_success(monkeypatch):
    fake_yf = types.SimpleNamespace(Ticker=lambda t: FakeTicker(t))
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    result = market_tools.get_stock_price("AAPL")
    assert result["ticker"] == "AAPL"
    assert result["current_price"] == 190.5
    assert result["currency"] == "USD"


def test_get_stock_price_handles_error(monkeypatch):
    def raise_error(t):
        raise RuntimeError("network down")
    fake_yf = types.SimpleNamespace(Ticker=raise_error)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    result = market_tools.get_stock_price("AAPL")
    assert "error" in result


def test_get_analyst_recommendations_no_data(monkeypatch):
    fake_yf = types.SimpleNamespace(Ticker=lambda t: FakeTicker(t))
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)

    result = market_tools.get_analyst_recommendations("AAPL")
    assert result["ticker"] == "AAPL"
    assert result["recommendations"] == "No analyst data available"


class FakeDDGS:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def news(self, query, max_results=5):
        return [
            {"title": "Big news", "source": "Reuters", "date": "2024-01-01",
             "url": "https://example.com", "body": "Something happened " * 20},
        ]


class RaisingDDGS:
    def __enter__(self):
        raise RuntimeError("search failed")


def test_search_financial_news_success(monkeypatch):
    # `ddgs` is the maintained package and is tried first by market_tools.
    fake_ddgs_module = types.SimpleNamespace(DDGS=FakeDDGS)
    monkeypatch.setitem(sys.modules, "ddgs", fake_ddgs_module)

    result = market_tools.search_financial_news("NVIDIA earnings")
    assert result["query"] == "NVIDIA earnings"
    assert len(result["results"]) == 1
    assert result["results"][0]["title"] == "Big news"
    assert len(result["results"][0]["excerpt"]) <= 200


def test_search_financial_news_handles_error(monkeypatch):
    fake_ddgs_module = types.SimpleNamespace(DDGS=RaisingDDGS)
    monkeypatch.setitem(sys.modules, "ddgs", fake_ddgs_module)

    result = market_tools.search_financial_news("test")
    assert "error" in result


def test_search_financial_news_falls_back_to_legacy_package(monkeypatch):
    # If `ddgs` isn't installed at all, market_tools should fall back to
    # the legacy `duckduckgo_search` package name transparently.
    monkeypatch.delitem(sys.modules, "ddgs", raising=False)
    monkeypatch.setattr(market_tools, "_get_ddgs_class", lambda: FakeDDGS)

    result = market_tools.search_financial_news("legacy path")
    assert result["query"] == "legacy path"
    assert result["results"][0]["title"] == "Big news"
