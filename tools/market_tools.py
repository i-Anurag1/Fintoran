"""
Market Tools
============
Live market data tools that sit alongside the personal finance tools so
the agent can reason across both ("should I buy this stock or pay down my
credit card?") instead of being a stock-news bot only.

Requires internet access at runtime (works when run locally / deployed;
sandboxed dev environments without outbound access will need to mock these
— see tests/test_market_tools.py).
"""


def _get_ddgs_class():
    """The `duckduckgo-search` package was frozen by its maintainer and
    renamed to `ddgs` (same API surface). Prefer the maintained `ddgs`
    package, but fall back to the legacy import name so this still works
    in any environment that only has the old package installed."""
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        from duckduckgo_search import DDGS
        return DDGS


def get_stock_price(ticker: str) -> dict:
    """Fetches the current price and daily change for a stock ticker (e.g. AAPL, TCS.NS)."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        return {
            "ticker": ticker.upper(),
            "current_price": round(info.get("lastPrice", 0), 2),
            "previous_close": round(info.get("previousClose", 0), 2),
            "day_high": round(info.get("dayHigh", 0), 2),
            "day_low": round(info.get("dayLow", 0), 2),
            "currency": info.get("currency", "USD"),
        }
    except Exception as e:
        return {"error": f"Could not fetch price for {ticker}: {str(e)}"}


def get_analyst_recommendations(ticker: str) -> dict:
    """Fetches analyst recommendation summary for a stock ticker."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        rec = stock.recommendations
        if rec is None or rec.empty:
            return {"ticker": ticker.upper(), "recommendations": "No analyst data available"}
        latest = rec.iloc[-1].to_dict()
        return {"ticker": ticker.upper(), "latest_recommendation_counts": latest}
    except Exception as e:
        return {"error": f"Could not fetch recommendations for {ticker}: {str(e)}"}


def search_financial_news(query: str, max_results: int = 5) -> dict:
    """Searches the web for recent financial news on a topic/company."""
    try:
        DDGS = _get_ddgs_class()
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "source": r.get("source"),
                    "date": r.get("date"),
                    "url": r.get("url"),
                    "excerpt": (r.get("body") or "")[:200],
                })
        return {"query": query, "results": results}
    except Exception as e:
        return {"error": f"News search failed: {str(e)}"}
