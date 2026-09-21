from analytics.financial import overview, anomaly_explanations

def test_overview_is_deterministic():
    rows=[{'date':'2026-09-01','description':'Salary','amount':50000,'type':'credit','category':'Income'}, {'date':'2026-09-02','description':'Food','amount':500,'type':'debit','category':'Food & Dining'}]
    result=overview(rows,current_balance=10000)
    assert result['monthly_income']==50000
    assert result['monthly_spending']==500
    assert result['savings_rate']==99.0

def test_anomaly_explanation_returns_reasons():
    rows=[]
    for i,a in enumerate([100,110,90,5000]):rows.append({'date':f'2026-09-{i+1:02d}','description':f'M{i}','amount':a,'type':'debit','category':'Other','merchant':f'M{i}'})
    result=anomaly_explanations(rows)
    assert any(x['amount']==5000 for x in result)
