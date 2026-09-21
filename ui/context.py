from __future__ import annotations
import os
import streamlit as st
from database import db
from memory.vector_memory import ConversationMemory
from core.graph import MultiAgentOrchestrator
from analytics.financial import overview

def require_user():
    user=st.session_state.get('user')
    if not user:
        st.warning('Please log in from the Fintoran home screen.')
        st.stop()
    return user

def current_user(): return require_user()
def transactions(): return db.get_all_transactions(current_user()['id'])
def budgets(): return db.get_budgets(current_user()['id'])
def agent():
    if 'agent' not in st.session_state: st.session_state.agent=MultiAgentOrchestrator()
    return st.session_state.agent
def memory():
    if 'memory' not in st.session_state: st.session_state.memory=ConversationMemory(current_user()['id'])
    return st.session_state.memory
def balance(): return float(st.session_state.get('current_balance',25000.0))
def page_header(title,subtitle=''):
    st.title(title)
    if subtitle: st.caption(subtitle)
