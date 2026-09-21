import streamlit as st
import pandas as pd
from ui.context import *
from services.import_pipeline import validate_and_preview,commit_preview,safe_export_csv

def render():
    page_header('Transactions','Import, validate, enrich, review, and manage your personal transaction dataset.')
    u=current_user();upload=st.file_uploader('Bank statement CSV',type=['csv'])
    if upload:
        preview=validate_and_preview(u['id'],upload.name,upload.getvalue())
        if preview['status']=='mapping_required':
            st.error('Map the required columns before importing.')
            st.write(preview['columns']); st.json(preview['mapping'])
        elif preview['status']=='error':st.error(preview['error'])
        else:
            st.subheader('Import preview');st.dataframe(preview['preview'],use_container_width=True,hide_index=True);st.write(f"Accepted: {len(preview['rows'])} · Rejected: {len(preview['errors'])}")
            if preview['errors']:st.json(preview['errors'][:10])
            replace=st.checkbox('Replace existing transactions',value=False)
            if preview['duplicate_import']:st.warning('This file was already imported for this account.')
            if st.button('Commit import',type='primary',disabled=preview['duplicate_import']):
                st.success(commit_preview(u['id'],preview,replace))
    tx=transactions(); df=pd.DataFrame(tx)
    if not df.empty:
        st.subheader('Dataset')
        categories=sorted(df['category'].dropna().astype(str).unique().tolist()) if 'category' in df else []
        c1,c2,c3=st.columns(3)
        with c1: search=st.text_input('Search merchant or description')
        with c2: category_filter=st.selectbox('Category filter',['All']+categories)
        with c3: type_filter=st.selectbox('Type filter',['All','debit','credit'])
        view=df.copy()
        if search:
            q=search.lower(); view=view[view.apply(lambda r:q in str(r.get('description','')).lower() or q in str(r.get('merchant','')).lower(),axis=1)]
        if category_filter!='All': view=view[view['category']==category_filter]
        if type_filter!='All': view=view[view['type']==type_filter]
        sort_col=st.selectbox('Sort by',['date','amount','merchant','category'])
        view=view.sort_values(sort_col,ascending=False)
        st.dataframe(view,use_container_width=True,hide_index=True)
        st.download_button('Export CSV',safe_export_csv(view.to_dict('records')),'fintoran_transactions.csv','text/csv')
        st.subheader('Correct category')
        row_id=st.selectbox('Transaction',view['id'].tolist())
        new_category=st.text_input('New category',value=str(view.loc[view['id']==row_id,'category'].iloc[0]))
        if st.button('Save category'): 
            from database.db import update_transaction_category
            update_transaction_category(u['id'],int(row_id),new_category.strip() or 'Other'); st.success('Category updated.'); st.rerun()
    else:st.info('No transactions yet — import a CSV to unlock personal analytics.')
render()
