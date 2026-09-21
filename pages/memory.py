import streamlit as st
from ui.context import *
def render():
    page_header('Memory','User-controlled conversation memory with bounded retrieval.')
    q=st.text_input('Test memory retrieval');
    if q:st.json(memory().retrieve_relevant(q,k=5))
    if st.button('Reset conversation memory',type='secondary'):memory().clear();st.success('Conversation memory reset.')
render()
