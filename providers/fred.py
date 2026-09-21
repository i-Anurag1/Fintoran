from __future__ import annotations
import os
from providers.base import Provenance
from providers.resilience import retry_call

def series_observations(series_id,limit=100):
    key=os.getenv('FRED_API_KEY')
    if not key:
        return {'status':'unavailable','reason':'FRED_API_KEY is not configured.'}
    import requests
    url='https://api.stlouisfed.org/fred/series/observations'
    def call():
        r=requests.get(url,params={'api_key':key,'series_id':series_id,'file_type':'json','limit':limit},timeout=10)
        r.raise_for_status(); return r.json()
    try:
        data=retry_call(call)
        return {'status':'ok','data':data,'provenance':Provenance.now('FRED',url,license_note='FRED API; API key required').as_dict()}
    except Exception:
        return {'status':'unavailable','reason':'FRED data is unavailable right now.'}
