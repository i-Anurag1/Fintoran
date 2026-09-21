"""External market/news tools with bounded retries and provenance."""
from __future__ import annotations
from datetime import datetime, timezone
from providers.resilience import retry_call


def _get_ddgs_class():
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        from duckduckgo_search import DDGS
        return DDGS


def _stamp(provider, source):
    return {"provider": provider, "source": source, "retrieved_at": datetime.now(timezone.utc).isoformat()}


def get_stock_price(ticker: str) -> dict:
    ticker = ticker.strip().upper()
    if not ticker:
        return {"status": "unavailable", "error": "Ticker is required.", "provenance": None}
    try:
        import yfinance as yf
        def call():
            info = yf.Ticker(ticker).fast_info
            price = info.get("lastPrice")
            if price is None:
                raise ValueError("no price")
            return info
        info = retry_call(call)
        return {
            "status": "ok", "ticker": ticker,
            "current_price": round(float(info.get("lastPrice")), 2),
            "previous_close": round(float(info.get("previousClose", 0) or 0), 2),
            "day_high": round(float(info.get("dayHigh", 0) or 0), 2),
            "day_low": round(float(info.get("dayLow", 0) or 0), 2),
            "currency": info.get("currency", "USD"),
            "provenance": _stamp("yfinance", "Yahoo Finance via yfinance"),
        }
    except Exception:
        return {"status": "unavailable", "error": f"Market price is unavailable for {ticker} right now.", "provenance": None}


def get_analyst_recommendations(ticker: str) -> dict:
    ticker = ticker.strip().upper()
    try:
        import yfinance as yf
        rec = retry_call(lambda: yf.Ticker(ticker).recommendations)
        if rec is None or rec.empty:
            return {"status": "ok", "ticker": ticker, "recommendations": "No analyst data available", "provenance": _stamp("yfinance", "Yahoo Finance via yfinance")}
        return {"status": "ok", "ticker": ticker, "latest_recommendation_counts": rec.iloc[-1].to_dict(), "provenance": _stamp("yfinance", "Yahoo Finance via yfinance")}
    except Exception:
        return {"status": "unavailable", "ticker": ticker, "error": f"Analyst data is unavailable for {ticker} right now.", "provenance": None}


def search_financial_news(query: str, max_results: int = 5) -> dict:
    try:
        DDGS = _get_ddgs_class()
        def call():
            results = []
            with DDGS() as ddgs:
                for item in ddgs.news(query, max_results=max_results):
                    results.append({"title": item.get("title"), "source": item.get("source"), "date": item.get("date"), "url": item.get("url"), "excerpt": (item.get("body") or "")[:200]})
            return results
        return {"status": "ok", "query": query, "results": retry_call(call), "provenance": _stamp("ddgs", "Public web news search")}
    except Exception:
        return {"status": "unavailable", "query": query, "results": [], "error": "Financial news is unavailable right now.", "provenance": None}
