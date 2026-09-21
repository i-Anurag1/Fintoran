from __future__ import annotations
import hashlib,io,os,re
import pandas as pd
from database import db
from tools.finance_tools import _categorize
MAX_UPLOAD_BYTES=int(os.getenv('MAX_UPLOAD_BYTES',str(10*1024*1024)))
ALIASES={'date':['date','transaction date','posted date','timestamp'],'description':['description','merchant','payee','narration','details','name'],'amount':['amount','value','transaction amount'],'type':['type','transaction type','debit/credit','dr/cr'],'category':['category','expense category'],'currency':['currency','ccy']}
def _norm(s):return re.sub(r'[^a-z0-9]+',' ',str(s).lower()).strip()
def detect_columns(columns):
    normalized={_norm(c):c for c in columns};out={}
    for target,aliases in ALIASES.items():
        for alias in aliases:
            if _norm(alias) in normalized:out[target]=normalized[_norm(alias)];break
    return out
def _source_hash(data):return hashlib.sha256(data).hexdigest()
def validate_and_preview(user_id,filename,data,mapping=None,source='user_upload'):
    if len(data)>MAX_UPLOAD_BYTES:return {'status':'error','error':f'File exceeds {MAX_UPLOAD_BYTES//(1024*1024)} MB limit.'}
    try:df=pd.read_csv(io.BytesIO(data),dtype=str,encoding='utf-8-sig')
    except UnicodeDecodeError:
        try:df=pd.read_csv(io.BytesIO(data),dtype=str,encoding='latin-1')
        except Exception:return {'status':'error','error':'CSV encoding could not be decoded.'}
    except Exception as exc:return {'status':'error','error':f'CSV could not be parsed: {exc}'}
    mapping=mapping or detect_columns(df.columns);missing=[x for x in ('date','description','amount') if x not in mapping]
    if missing:return {'status':'mapping_required','missing':missing,'columns':list(df.columns),'mapping':mapping}
    out=pd.DataFrame();
    for target,source_col in mapping.items():
        if source_col in df.columns:out[target]=df[source_col]
    out['date']=pd.to_datetime(out['date'],errors='coerce');raw=out['amount'].astype(str).str.replace(',','',regex=False).str.replace('₹','',regex=False).str.strip();out['amount']=pd.to_numeric(raw,errors='coerce');out['description']=out['description'].fillna('').astype(str).str.strip()
    if 'type' not in out:out['type']=out['amount'].apply(lambda x:'debit' if x<0 else 'credit')
    out['type']=out['type'].astype(str).str.lower().map(lambda x:'credit' if x in {'credit','cr','income'} else 'debit');out['amount']=out['amount'].abs()
    if 'category' not in out:out['category']=out['description'].map(_categorize)
    out['category']=out['category'].fillna('Other').replace('','Other');out['merchant']=out['description'].map(lambda x:re.sub(r'[\s#*]+',' ',x).strip());out['currency']=out.get('currency',pd.Series('INR',index=out.index)).fillna('INR').astype(str).str.upper()
    errors=[];clean=[];seen=set()
    for i,row in out.iterrows():
        key=(str(row.date),row.description.lower(),float(row.amount) if pd.notna(row.amount) else None,row.type)
        if pd.isna(row.date):errors.append({'row':i+2,'error':'invalid date'});continue
        if not row.description:errors.append({'row':i+2,'error':'missing description'});continue
        if pd.isna(row.amount):errors.append({'row':i+2,'error':'invalid amount'});continue
        if key in seen:errors.append({'row':i+2,'error':'duplicate row in file'});continue
        seen.add(key);clean.append(row.to_dict())
    digest=_source_hash(data)
    return {'status':'preview','filename':filename,'source':source,'source_hash':digest,'mapping':mapping,'rows':clean,'errors':errors,'duplicate_import':db.has_import_hash(user_id,digest),'preview':pd.DataFrame(clean).head(25)}
def commit_preview(user_id,preview,replace_existing=False):
    if preview.get('status')!='preview':return {'status':'error','error':'Invalid import preview.'}
    if preview.get('duplicate_import'):return {'status':'error','error':'This file was already imported for this account.'}
    if replace_existing:db.clear_transactions(user_id)
    rows=preview['rows'];counts={}
    for r in rows:counts[r['description']]=counts.get(r['description'],0)+1
    for r in rows:r['is_recurring']=int(counts[r['description']]>=2);r['is_anomaly']=0;r['source']=preview['source'];r['source_hash']=preview['source_hash'];r['date']=pd.Timestamp(r['date']).isoformat()
    db.insert_transactions(user_id,rows);batch=db.create_import_batch(user_id,preview['filename'],preview['source'],preview['source_hash'],len(rows)+len(preview['errors']),len(rows),len(preview['errors']))
    return {'status':'success','batch_id':batch,'transactions_loaded':len(rows),'rejected':len(preview['errors']),'replaced':replace_existing}

def safe_export_csv(transactions):
    """Return a UTF-8 CSV with spreadsheet formula injection neutralized."""
    df=pd.DataFrame(transactions).copy()
    if df.empty:
        return b''
    dangerous=('=', '+', '-', '@')
    for col in df.columns:
        df[col]=df[col].map(lambda v: "'"+v if isinstance(v,str) and v.startswith(dangerous) else v)
    return df.to_csv(index=False).encode('utf-8-sig')
