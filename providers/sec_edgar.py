from __future__ import annotations
import os
from providers.base import Provenance
from providers.resilience import retry_call
SEC_URL='https://data.sec.gov'

def _headers():
    agent=os.getenv('SEC_USER_AGENT','').strip()
    if not agent:
        raise RuntimeError('SEC_USER_AGENT is not configured.')
    return {'User-Agent': agent, 'Accept-Encoding':'gzip, deflate'}

def _get(url,timeout=10):
    import requests
    def call():
        r=requests.get(url,headers=_headers(),timeout=timeout)
        r.raise_for_status()
        return r.json()
    return retry_call(call)

def company_facts(cik):
    cik10=str(cik).strip().zfill(10); url=f'{SEC_URL}/api/xbrl/companyfacts/CIK{cik10}.json'
    return {'data':_get(url),'provenance':Provenance.now('SEC EDGAR',url,license_note='SEC public EDGAR API; respect SEC fair-access guidance').as_dict()}

def submissions(cik):
    cik10=str(cik).strip().zfill(10); url=f'{SEC_URL}/submissions/CIK{cik10}.json'
    return {'data':_get(url),'provenance':Provenance.now('SEC EDGAR',url,license_note='SEC public EDGAR API; respect SEC fair-access guidance').as_dict()}
