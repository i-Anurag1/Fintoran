from __future__ import annotations

from datetime import datetime, timezone

from tools import market_tools


def _provenance(provider, source, dataset_date_range=None, freshness="provider-dependent"):
    result = {
        "provider": provider,
        "source": source,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "freshness": freshness,
    }
    if dataset_date_range:
        result["dataset_date_range"] = dataset_date_range
    return result


def quote(ticker):
    data = market_tools.get_stock_price(ticker)
    if data.get("status") != "ok":
        return {"status": "unavailable", "data": data, "provenance": data.get("provenance")}
    return {"status": "ok", "data": data, "provenance": data.get("provenance") or _provenance("yfinance", "Yahoo Finance via yfinance")}


def history(ticker, period="1y"):
    try:
        import yfinance as yf
        from providers.resilience import retry_call

        frame = retry_call(lambda: yf.Ticker(ticker).history(period=period))
        return {
            "status": "ok",
            "data": frame.reset_index().to_dict("records"),
            "provenance": _provenance("yfinance", "Yahoo Finance via yfinance", period),
        }
    except Exception:
        return {"status": "unavailable", "data": [], "error": "Market history unavailable right now.", "provenance": None}


def fundamentals(ticker):
    try:
        import yfinance as yf
        from providers.resilience import retry_call

        info = retry_call(lambda: yf.Ticker(ticker).info)
        fields = {
            key: info.get(key)
            for key in (
                "longName", "sector", "industry", "marketCap", "enterpriseValue",
                "trailingPE", "forwardPE", "profitMargins", "operatingMargins",
                "returnOnEquity", "totalRevenue", "operatingIncome", "freeCashflow",
                "totalCash", "totalDebt",
            )
            if info.get(key) is not None
        }
        return {"status": "ok", "ticker": ticker, "data": fields, "provenance": _provenance("yfinance", "Yahoo Finance via yfinance")}
    except Exception:
        return {"status": "unavailable", "ticker": ticker, "data": {}, "error": "Company fundamentals are unavailable right now.", "provenance": None}


def returns_volatility_drawdown(ticker, period="1y"):
    result = history(ticker, period)
    if result.get("status") != "ok":
        return result
    try:
        import pandas as pd
        frame = pd.DataFrame(result["data"])
        close_col = "Close"
        frame[close_col] = pd.to_numeric(frame[close_col], errors="coerce")
        returns = frame[close_col].pct_change().dropna()
        running_max = frame[close_col].cummax()
        drawdown = frame[close_col] / running_max - 1
        return {
            "status": "ok",
            "ticker": ticker,
            "data": {
                "period_return_pct": float((frame[close_col].iloc[-1] / frame[close_col].iloc[0] - 1) * 100) if len(frame) > 1 else 0.0,
                "annualized_volatility_pct": float(returns.std(ddof=1) * (252 ** 0.5) * 100) if len(returns) > 1 else 0.0,
                "max_drawdown_pct": float(drawdown.min() * 100) if len(drawdown) else 0.0,
                "moving_average_20": float(frame[close_col].rolling(20).mean().iloc[-1]) if len(frame) >= 20 else None,
                "moving_average_50": float(frame[close_col].rolling(50).mean().iloc[-1]) if len(frame) >= 50 else None,
                "volume_latest": float(pd.to_numeric(frame.get("Volume"), errors="coerce").iloc[-1]) if "Volume" in frame and len(frame) else None,
            },
            "provenance": result.get("provenance"),
        }
    except Exception:
        return {"status": "unavailable", "ticker": ticker, "data": {}, "error": "Market analytics are unavailable right now.", "provenance": None}
