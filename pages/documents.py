import streamlit as st
from ui.context import *
from rag.document_store import ingest,search,delete,reindex

def render():
    page_header('Documents / RAG','Upload private documents, retrieve grounded passages, and cite sources.')
    u=current_user();f=st.file_uploader('PDF, TXT, Markdown, or CSV',type=['pdf','txt','md','markdown','csv'])
    if f and st.button('Index document',type='primary'):
        try:st.json(ingest(u['id'],f.name,f.getvalue(),f.type))
        except ValueError as e:st.error(str(e))
    docs=__import__('database.db',fromlist=['get_documents']).get_documents(u['id']);st.subheader('Documents');st.dataframe(docs,use_container_width=True,hide_index=True)
    q=st.text_input('Ask about uploaded documents')
    selected_doc=None
    if docs: selected_doc=st.selectbox('Document filter',['All']+[d['document_id'] for d in docs])
    if q:
        for r in search(u['id'],q,document_id=None if selected_doc in (None,'All') else selected_doc):
            st.markdown(f"**{r['citation']}** · distance {r['distance']:.4f}");st.write(r['text'])
    if docs:
        did=st.selectbox('Manage document',[d['document_id'] for d in docs],key='manage_doc')
        c1,c2=st.columns(2)
        with c1:
            if st.button('Delete selected document'):delete(u['id'],did);st.success('Document deleted.');st.rerun()
        with c2:
            if st.button('Re-index selected document'):
                st.info(reindex(u['id'],did)['message'])
render()
