from __future__ import annotations
import json,logging,time,uuid
from contextvars import ContextVar
from security.input_validation import redact_secrets
correlation_id=ContextVar('correlation_id',default=None)
def new_correlation_id():
    cid=uuid.uuid4().hex; correlation_id.set(cid); return cid
def get_logger(name='fintoran'):
    logger=logging.getLogger(name)
    if not logger.handlers:
        h=logging.StreamHandler(); h.setFormatter(logging.Formatter('%(message)s')); logger.addHandler(h); logger.setLevel(logging.INFO); logger.propagate=False
    return logger
def event(logger,event_name,**fields):
    safe={k:redact_secrets(str(v)) for k,v in fields.items() if k not in {'password','api_key','token','private_data'}}
    safe.update(event=event_name,correlation_id=correlation_id.get()); logger.info(json.dumps(safe,separators=(',',':'),default=str))
class Timer:
    def __init__(self,logger,name,**fields): self.logger,self.name,self.fields,self.start=logger,name,fields,time.perf_counter()
    def __enter__(self): return self
    def __exit__(self,*_): event(self.logger,self.name,latency_ms=round((time.perf_counter()-self.start)*1000,2),**self.fields)
