import streamlit as st
from ui.context import *
from analytics.financial import spending_trend,category_trends,merchant_concentration,percentile_outliers,anomaly_explanations,scenario,income_vs_expense,seasonal_spending_patterns,rolling_spending_average
from analytics.forecast import compare

def render():
    page_header('Analytics','Deterministic trends, outliers, forecasts, and scenarios.')
    tx=transactions();
    if not tx:st.info('Load transactions first.');return
    frequency=st.selectbox('Spending trend granularity',['D','W','M'],index=2)
    st.subheader('Spending trend');st.line_chart(spending_trend(tx,frequency).set_index('period'))
    c1,c2=st.columns(2)
    with c1:st.subheader('Merchant concentration');st.json(merchant_concentration(tx))
    with c2:st.subheader('Forecast models');st.json(compare(tx))
    st.subheader('Income vs expense / cash flow');st.dataframe(income_vs_expense(tx),use_container_width=True,hide_index=True)
    st.subheader('Category trend');st.dataframe(category_trends(tx),use_container_width=True,hide_index=True)
    st.subheader('Seasonal spending pattern');st.dataframe(seasonal_spending_patterns(tx),use_container_width=True,hide_index=True)
    st.subheader('Rolling spending average');st.line_chart(rolling_spending_average(tx).set_index('date')[['spending','rolling_average']])
    st.subheader('Why transactions were flagged');st.json(anomaly_explanations(tx))
    st.subheader('Percentile outliers');st.dataframe(percentile_outliers(tx),use_container_width=True,hide_index=True)
    extra=st.number_input('Extra monthly spending',min_value=0.0,value=0.0);income=st.number_input('Monthly income change',value=0.0);st.json(scenario(tx,balance(),extra,income))
render()
