from __future__ import annotations
import os, re
ALLOWED_DOC_EXTENSIONS={'.pdf','.txt','.md','.markdown','.csv'}
MAX_DOCUMENT_BYTES=int(os.getenv('MAX_DOCUMENT_BYTES',str(15*1024*1024)))
def validate_filename(filename):
    name=os.path.basename(filename or '').strip()
    if not name or name in {'.','..'} or '..' in name or '\x00' in name or '/' in (filename or '') or '\\' in (filename or ''): raise ValueError('Invalid filename')
    if os.path.splitext(name)[1].lower() not in ALLOWED_DOC_EXTENSIONS: raise ValueError('Unsupported document type')
    return name
def validate_upload_size(data,max_bytes=MAX_DOCUMENT_BYTES):
    if len(data)>max_bytes: raise ValueError(f'Upload exceeds {max_bytes//(1024*1024)} MB')
def redact_secrets(value):
    for pattern in [r'(?i)(api[_-]?key|password|token|secret)\s*[:=]\s*[^\s,;]+']:
        value=re.sub(pattern,lambda m:m.group(1)+'=[REDACTED]',value)
    return value
