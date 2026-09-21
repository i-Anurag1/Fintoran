import os

import streamlit as st

from ui.context import *
from providers.market import quote, history, fundamentals, returns_volatility_drawdown
from providers.sec_edgar import company_facts, submissions
from providers.fred import series_observations
from tools.market_tools import get_analyst_recommendations, search_financial_news


def render():
    page_header("Market Research", "Quotes, history, fundamentals, filings, macro context, news, and source provenance.")
    st.caption("Informational research only. External data is provider-dependent and shown with freshness metadata.")
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
    period = st.selectbox("Historical window", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

    if st.button("Research", type="primary"):
        q = quote(ticker)
        st.subheader("Quote")
        st.json(q)
        if q.get("provenance"):
            st.caption(f"Data as of {q['provenance'].get('retrieved_at')} · {q['provenance'].get('provider')}")

        st.subheader("Historical price and risk")
        h = history(ticker, period)
        if h.get("status") == "ok":
            st.dataframe(h.get("data", []), use_container_width=True, hide_index=True)
        else:
            st.info(h.get("error", "Historical data unavailable."))
        st.json(returns_volatility_drawdown(ticker, period))

        st.subheader("Company fundamentals")
        st.json(fundamentals(ticker))

        st.subheader("Analyst data")
        st.json(get_analyst_recommendations(ticker))

        st.subheader("SEC filing data")
        st.json({"submissions": submissions(ticker) if ticker.isdigit() else {"status": "info", "message": "SEC adapter expects a CIK for filing retrieval."}})
        if ticker.isdigit():
            st.json(company_facts(ticker))

        st.subheader("Macro context")
        fred_series = st.text_input("Optional FRED series ID", value="CPIAUCSL", key="fred_series")
        if fred_series:
            st.json(series_observations(fred_series.strip().upper()))

        st.subheader("Financial news")
        st.json(search_financial_news(ticker))


render()
