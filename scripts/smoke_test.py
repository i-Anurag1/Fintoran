"""Dependency-light smoke test for core local services."""
import tempfile, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db
from analytics.financial import overview
from services.import_pipeline import validate_and_preview

def main():
    with tempfile.TemporaryDirectory() as d:
        old=db.DB_PATH; db.DB_PATH=os.path.join(d,'smoke.db'); db.init_db(); uid=db.create_user('smoke_user','hash')
        payload=b'date,description,amount,type\n2026-09-01,Salary,50000,credit\n2026-09-02,Swiggy,-500,debit\n'
        p=validate_and_preview(uid,'smoke.csv',payload); assert p['status']=='preview'; r=__import__('services.import_pipeline',fromlist=['commit_preview']).commit_preview(uid,p); assert r['status']=='success'; o=overview(db.get_all_transactions(uid),current_balance=50000); assert o['monthly_spending']>=500
        db.DB_PATH=old
    print('SMOKE_OK')
if __name__=='__main__':main()
