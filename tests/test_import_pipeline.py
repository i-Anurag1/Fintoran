from services.import_pipeline import validate_and_preview, commit_preview

def test_import_preview_and_commit(temp_db, sample_user):
    payload=b"date,description,amount,type\n2026-09-01,Salary,50000,credit\n2026-09-02,Swiggy,-500,debit\n"
    preview=validate_and_preview(sample_user['id'],'bank.csv',payload)
    assert preview['status']=='preview'
    result=commit_preview(sample_user['id'],preview)
    assert result['transactions_loaded']==2
    assert len(temp_db.get_all_transactions(sample_user['id']))==2

def test_duplicate_import_is_rejected(temp_db, sample_user):
    payload=b"date,description,amount,type\n2026-09-01,Salary,50000,credit\n"
    p=validate_and_preview(sample_user['id'],'bank.csv',payload);commit_preview(sample_user['id'],p)
    p2=validate_and_preview(sample_user['id'],'bank.csv',payload)
    assert p2['duplicate_import'] is True
