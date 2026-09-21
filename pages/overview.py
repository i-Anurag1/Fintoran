import streamlit as st
from ui.context import *
def render():
    u=current_user(); page_header('Overview','A deterministic snapshot of your loaded financial data.')
    o=overview(transactions(),budgets(),balance()); cols=st.columns(5)
    cols[0].metric('Current balance',f"₹{o['balance']:,.0f}");cols[1].metric('Monthly income',f"₹{o['monthly_income']:,.0f}");cols[2].metric('Monthly spending',f"₹{o['monthly_spending']:,.0f}");cols[3].metric('Savings rate',f"{o['savings_rate']:.1f}%");cols[4].metric('Budget used',f"{o['budget_utilization']:.1f}%")
    c1,c2=st.columns(2)
    with c1:
        st.subheader('Spending categories');st.bar_chart(o['top_categories']) if o['top_categories'] else st.info('No transactions yet. Import a CSV to unlock analytics.')
    with c2:
        st.subheader("What's happening?")
        if o['monthly_spending']:
            change='No prior month baseline' if o['mom_change_pct'] is None else f"Spending is {abs(o['mom_change_pct']):.1f}% {'up' if o['mom_change_pct']>0 else 'down'} versus the prior month."
            st.write(change);st.write(f"Projected month-end balance: ₹{o['projected_month_end_balance']:,.0f}.")
        else: st.info('Load transactions to generate a grounded summary.')
    st.subheader('Recent transactions');st.dataframe(o['recent_transactions'],use_container_width=True,hide_index=True)
    st.caption(f"Data as of {o['data_as_of'] or 'not available'}. Calculations are deterministic.")
render()
