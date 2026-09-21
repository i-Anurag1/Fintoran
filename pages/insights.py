import streamlit as st
from ui.context import *
from analytics.financial import anomaly_explanations,recurring
def render():
    page_header('Insights','Explainable anomalies and recurring-payment signals.')
    tx=transactions();st.subheader('Recurring payments');st.dataframe(recurring(tx),use_container_width=True,hide_index=True);st.subheader('Anomalies');st.json(anomaly_explanations(tx))
render()
