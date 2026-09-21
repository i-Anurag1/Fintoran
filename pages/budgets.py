import streamlit as st
from ui.context import *
def render():
    page_header('Budgets','Set category limits and compare them with deterministic spending totals.')
    u=current_user(); existing=budgets(); categories=sorted(set(existing)|set(x.get('category') or 'Other' for x in transactions()))
    if not categories:categories=['Food & Dining','Shopping','Transport','Subscriptions']
    cat=st.selectbox('Category',categories);limit=st.number_input('Monthly limit',min_value=0.0,value=float(existing.get(cat,0.0)),step=500.0)
    if st.button('Save budget',type='primary'):__import__('database.db',fromlist=['set_budget']).set_budget(u['id'],cat,limit);st.success('Budget saved.')
    tx=transactions(); from analytics.financial import frame, _expense_mask
    df=frame(tx); variance=[]
    if not df.empty:
        latest=df.date.max().to_period('M'); cur=df[df.date.dt.to_period('M')==latest]; spent=cur[_expense_mask(cur)].groupby('category').amount.apply(lambda x:float(x.abs().sum())).to_dict()
        variance=[{'category':k,'limit':float(v),'spent':float(spent.get(k,0)),'variance':float(v-spent.get(k,0))} for k,v in budgets().items()]
    st.subheader('Budget variance'); st.dataframe(variance,use_container_width=True,hide_index=True)
render()
