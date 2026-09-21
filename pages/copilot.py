import streamlit as st
from ui.context import *
def render():
    page_header('AI Copilot','Supervisor-led finance, analytics, market research, and document retrieval.')
    for turn in st.session_state.get('chat_history',[]):
        with st.chat_message(turn['role']): st.write(turn['content'])
    q=st.chat_input('Ask Fintoran about your finances, markets, or uploaded documents')
    if q:
        st.session_state.setdefault('chat_history',[]).append({'role':'user','content':q})
        with st.chat_message('user'):st.write(q)
        with st.chat_message('assistant'):
            with st.spinner('Running grounded analysis...'):
                history=st.session_state.chat_history[:-1];ctx=memory().get_context_string(q)
                result=agent().run(current_user()['id'],q,history,ctx)
            st.write(result['answer']);st.session_state.last_trace=result['trace']
        st.session_state.chat_history.append({'role':'assistant','content':result['answer']});memory().add_chat_turn('user',q);memory().add_chat_turn('assistant',result['answer'])
    with st.expander('Run trace'):
        for x in st.session_state.get('last_trace',[]):st.caption(x)
render()
