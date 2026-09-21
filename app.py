"""Fintoran application entrypoint.

Streamlit's st.navigation/st.Page API provides the application shell while
page modules keep product features separated and testable.
"""
from __future__ import annotations
import os
import streamlit as st
from dotenv import load_dotenv
from database import db
from auth import auth
from services.import_pipeline import validate_and_preview, commit_preview
from ui.theme import apply

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=os.path.join(BASE_DIR,'data')
os.makedirs(DATA_DIR,exist_ok=True)
load_dotenv(os.path.join(BASE_DIR,'.env'))

db.init_db()
st.set_page_config(page_title='Fintoran',page_icon='F',layout='wide',initial_sidebar_state='collapsed')
apply()

if 'user' not in st.session_state:st.session_state.user=None
if 'chat_history' not in st.session_state:st.session_state.chat_history=[]
if 'current_balance' not in st.session_state:st.session_state.current_balance=25000.0


def login_screen():
    """Render a compact, responsive authentication experience."""
    left, center, right = st.columns([1, 1.15, 1], gap="large")
    with center:
        st.markdown('<div class="fintoran-brand fintoran-auth-brand">Fintoran</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="fintoran-auth-tagline">Agentic personal finance workspace for grounded analytics, market research, and private document RAG.</div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            login_tab, signup_tab = st.tabs(["Log in", "Create account"])

            with login_tab:
                with st.form('login', clear_on_submit=False):
                    username = st.text_input('Username', placeholder='Enter your username', autocomplete='username')
                    password = st.text_input('Password', type='password', placeholder='Enter your password', autocomplete='current-password')
                    submit = st.form_submit_button('Log in', type='primary', use_container_width=True)
                if submit:
                    r = auth.login(username, password)
                    if r['success']:
                        st.session_state.user = r['user']
                        st.rerun()
                    else:
                        st.error(r['message'])

            with signup_tab:
                with st.form('signup', clear_on_submit=False):
                    username = st.text_input('Username', key='su', placeholder='Choose a username', autocomplete='username')
                    password = st.text_input('Password', type='password', key='sp', placeholder='Create a password', autocomplete='new-password')
                    confirm = st.text_input('Confirm password', type='password', key='sc', placeholder='Re-enter your password', autocomplete='new-password')
                    submit = st.form_submit_button('Create account', type='primary', use_container_width=True)
                if submit:
                    if password != confirm:
                        st.error("Passwords don't match.")
                    else:
                        r = auth.signup(username, password)
                        if r['success']:
                            st.session_state.user = r['user']
                            st.rerun()
                        else:
                            st.error(r['message'])

if st.session_state.user is None:
    login_screen();st.stop()

user=st.session_state.user
with st.sidebar:
    st.markdown('<div class="fintoran-brand">Fintoran</div>',unsafe_allow_html=True)
    st.caption(f"Signed in as {user['username']}")
    st.session_state.current_balance=st.number_input('Current balance (₹)',min_value=0.0,value=float(st.session_state.current_balance),step=500.0)
    st.divider()
    st.subheader('Import')
    uploaded=st.file_uploader('CSV bank statement',type=['csv'],key='global_csv')
    if uploaded:
        p=validate_and_preview(user['id'],uploaded.name,uploaded.getvalue())
        if p['status']=='preview':
            st.caption(f"Preview: {len(p['rows'])} accepted · {len(p['errors'])} rejected")
            replace=st.checkbox('Replace existing data',key='replace_global')
            if st.button('Commit CSV',use_container_width=True,disabled=p['duplicate_import']):st.success(commit_preview(user['id'],p,replace))
        elif p['status']=='mapping_required':st.warning('Use Transactions for custom column mapping.')
        else:st.error(p['error'])
    if st.button('Load historical public dataset',use_container_width=True):
        path=os.path.join(DATA_DIR,'kaggle_transactions.csv');data=open(path,'rb').read();p=validate_and_preview(user['id'],'kaggle_transactions.csv',data,source='historical_public_dataset')
        if p['status']=='preview':st.success(commit_preview(user['id'],p,replace_existing=False))
    if st.button('Load synthetic demo data',use_container_width=True):
        path=os.path.join(DATA_DIR,'sample_transactions.csv');data=open(path,'rb').read();p=validate_and_preview(user['id'],'sample_transactions.csv',data,source='demo_synthetic')
        if p['status']=='preview':st.success(commit_preview(user['id'],p,replace_existing=False))
    st.divider()
    st.caption('Data freshness: personal data reflects your latest import. External data shows provider timestamps on the relevant pages.')
    if st.button('Log out',use_container_width=True):
        for key in ('user','agent','memory','chat_history','last_trace'):st.session_state.pop(key,None)
        st.rerun()

pages={
    'Workspace':[
        st.Page('pages/overview.py',title='Overview',default=True),
        st.Page('pages/copilot.py',title='AI Copilot'),
        st.Page('pages/transactions.py',title='Transactions'),
        st.Page('pages/analytics.py',title='Analytics'),
        st.Page('pages/budgets.py',title='Budgets'),
        st.Page('pages/insights.py',title='Insights'),
    ],
    'Research':[
        st.Page('pages/market.py',title='Market Research'),
        st.Page('pages/documents.py',title='Documents / RAG'),
    ],
    'Account':[
        st.Page('pages/memory.py',title='Memory'),
        st.Page('pages/settings.py',title='Settings'),
    ],
}
pg=st.navigation(pages,position='sidebar',expanded=True)
pg.run()
