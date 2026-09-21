import os
import streamlit as st
from ui.context import *

def render():
    u=current_user(); page_header('Settings','Account, privacy, model and data-source status.')
    st.write('Username:',u['username'])
    st.write('Groq configured:',bool(os.getenv('GROQ_API_KEY')))
    st.write('FRED configured:',bool(os.getenv('FRED_API_KEY')))
    st.write('SEC user agent configured:',bool(os.getenv('SEC_USER_AGENT')))
    st.write('Model:',os.getenv('GROQ_MODEL','openai/gpt-oss-120b'))
    st.caption('Fintoran is informational software, not a licensed financial adviser. Verify external information independently.')

    st.subheader('Financial profile')
    from database.db import get_user_profile, update_user_profile
    profile=get_user_profile(u['id'])
    currency=st.text_input('Base currency',value=profile.get('base_currency') or 'INR',max_chars=8)
    income=st.number_input('Optional monthly income',min_value=0.0,value=float(profile.get('monthly_income') or 0.0),step=1000.0)
    goals=st.text_area('Financial goals',value=profile.get('financial_goals') or '',max_chars=1000)
    if st.button('Save financial profile'):
        update_user_profile(u['id'],currency.strip().upper() or 'INR',income or None,goals.strip() or None)
        st.success('Financial profile saved.')

    st.subheader('Privacy controls')
    c1,c2=st.columns(2)
    with c1:
        if st.button('Reset my financial data',type='secondary'):
            from database.db import reset_user_data
            from rag.document_store import reset_user_documents
            reset_user_documents(u['id']); reset_user_data(u['id']); st.success('Financial data and private document records reset.'); st.rerun()
    with c2:
        if st.button('Reset conversation memory',type='secondary'):
            memory().clear(); st.success('Conversation memory reset.'); st.rerun()

    st.subheader('Documents')
    from database.db import get_documents
    docs=get_documents(u['id'])
    if docs:
        st.dataframe(docs,use_container_width=True,hide_index=True)
    else:
        st.info('No private documents are indexed.')

    st.subheader('Data-source status')
    st.write({
        'Personal transactions':'User-uploaded/local',
        'Market data':'yfinance provider, freshness shown with results',
        'Financial news':'DDGS public web search, freshness shown with results',
        'SEC filings':'SEC EDGAR public API, requires SEC_USER_AGENT',
        'Macro data':'FRED API, requires FRED_API_KEY',
        'Synthetic/demo data':'Clearly labeled in import provenance',
    })

    if st.button('Log out',type='primary'):
        for key in ('user','agent','memory','chat_history','last_trace'):
            st.session_state.pop(key,None)
        st.rerun()

render()
