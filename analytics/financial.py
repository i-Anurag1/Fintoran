from __future__ import annotations
import statistics
import pandas as pd

def frame(transactions):
    df=pd.DataFrame(transactions)
    if df.empty:return pd.DataFrame(columns=['date','description','amount','type','category','merchant'])
    df['date']=pd.to_datetime(df['date'],errors='coerce');df['amount']=pd.to_numeric(df['amount'],errors='coerce');df['type']=df['type'].astype(str).str.lower();df['category']=df.get('category','Other').fillna('Other');df['merchant']=df.get('merchant',df['description']).fillna(df['description']);return df.dropna(subset=['date','amount'])
def _expense_mask(df):return df['type'].eq('debit')|(df['amount']<0)
def recurring(data):
    df=data if isinstance(data,pd.DataFrame) else frame(data)
    if df.empty:return []
    e=df[_expense_mask(df)];out=[]
    for merchant,g in e.groupby('merchant'):
        if len(g)<2:continue
        amounts=g['amount'].abs().tolist();spread=(max(amounts)-min(amounts))/max(statistics.mean(amounts),1)
        if spread<=.15:out.append({'merchant':merchant,'occurrences':len(g),'average_amount':round(statistics.mean(amounts),2),'last_date':g['date'].max().date().isoformat()})
    return sorted(out,key=lambda x:x['average_amount'],reverse=True)
def overview(transactions,budgets=None,current_balance=0.0):
    df=frame(transactions)
    if df.empty:return {'balance':float(current_balance),'monthly_income':0.0,'monthly_spending':0.0,'savings_rate':0.0,'mom_change_pct':None,'top_categories':{},'recurring_payments':[],'anomaly_count':0,'budget_utilization':0.0,'projected_month_end_balance':float(current_balance),'recent_transactions':[],'data_as_of':None}
    latest=df.date.max();month=latest.to_period('M');cur=df[df.date.dt.to_period('M')==month];prev=df[df.date.dt.to_period('M')==(month-1)];income=cur.loc[~_expense_mask(cur),'amount'].abs().sum();spending=cur.loc[_expense_mask(cur),'amount'].abs().sum();prev_spend=prev.loc[_expense_mask(prev),'amount'].abs().sum();mom=None if prev_spend==0 else (spending-prev_spend)/prev_spend*100;cat=cur.loc[_expense_mask(cur)].groupby('category').amount.apply(lambda s:float(s.abs().sum())).sort_values(ascending=False);bt=sum((budgets or {}).values());util=0 if bt<=0 else min(100,spending/bt*100);projected=float(current_balance)-(spending/max(latest.day,1))*max(latest.days_in_month-latest.day,0)
    return {'balance':float(current_balance),'monthly_income':float(income),'monthly_spending':float(spending),'savings_rate':float((income-spending)/income*100 if income else 0),'mom_change_pct':mom,'top_categories':{k:float(v) for k,v in cat.head(6).items()},'recurring_payments':recurring(df),'anomaly_count':int(df.get('is_anomaly',pd.Series(dtype=int)).fillna(0).sum()),'budget_utilization':float(util),'projected_month_end_balance':float(projected),'recent_transactions':df.sort_values('date',ascending=False).head(8).to_dict('records'),'data_as_of':latest.date().isoformat()}
def spending_trend(transactions,frequency='M'):
    df=frame(transactions);e=df[_expense_mask(df)].copy()
    if e.empty:return pd.DataFrame(columns=['period','spending'])
    e['period']=e.date.dt.to_period(frequency).astype(str);return e.groupby('period').amount.apply(lambda s:float(s.abs().sum())).reset_index(name='spending')
def category_trends(transactions):
    df=frame(transactions);e=df[_expense_mask(df)].copy()
    if e.empty:return pd.DataFrame(columns=['period','category','spending'])
    e['period']=e.date.dt.to_period('M').astype(str);return e.groupby(['period','category']).amount.apply(lambda s:float(s.abs().sum())).reset_index(name='spending')
def merchant_concentration(transactions,top_n=10):
    df=frame(transactions);e=df[_expense_mask(df)];vals=e.groupby('merchant').amount.apply(lambda s:float(s.abs().sum())).sort_values(ascending=False).head(top_n);total=float(e.amount.abs().sum());return {'merchants':dict(vals),'top_n_share_pct':float(vals.sum()/total*100 if total else 0)}
def percentile_outliers(transactions,percentile=.95):
    df=frame(transactions);e=df[_expense_mask(df)]
    if len(e)<4:return []
    threshold=float(e.amount.abs().quantile(percentile));return e[e.amount.abs()>=threshold].sort_values('amount').to_dict('records')
def anomaly_explanations(transactions):
    df=frame(transactions);e=df[_expense_mask(df)]
    if len(e)<3:return []
    amounts=e.amount.abs();mean=amounts.mean();std=amounts.std(ddof=0);out=[]
    merchant_counts=e.groupby('merchant').size()
    for idx,row in e.iterrows():
        reasons=[];z=0 if std==0 else (abs(row.amount)-mean)/std
        if z>=2: reasons.append(f'amount is {z:.1f} standard deviations above your spending mean')
        merchant_count=int(merchant_counts.get(row.merchant,0))
        if merchant_count==1: reasons.append('merchant appears only once in the loaded history')
        elif merchant_count < max(2, int(len(e)*0.05)): reasons.append('merchant frequency is low in the loaded history')
        if merchant_count >= 3:
            merchant_amounts=e.loc[e.merchant==row.merchant,'amount'].abs()
            merchant_mean=float(merchant_amounts.mean())
            if merchant_mean and abs(abs(row.amount)-merchant_mean)/merchant_mean > 0.25: reasons.append("amount deviates materially from this merchant's recurring pattern")
        ts=pd.to_datetime(row.date,errors='coerce')
        if pd.notna(ts) and len(e)>=7:
            weekday_counts=e.date.dt.dayofweek.value_counts()
            if int(weekday_counts.get(ts.dayofweek,0)) <= 1: reasons.append('transaction occurred on an uncommon weekday in the loaded history')
            hours=e.date.dt.hour
            if (hours>0).any() and int((hours==ts.hour).sum()) <= 1: reasons.append('transaction time is unusual in the loaded history')
        if reasons:out.append({'transaction_id':int(row.get('id',idx)),'description':row.description,'amount':float(abs(row.amount)),'reasons':reasons})
    return out
def scenario(transactions,current_balance,monthly_extra_spend=0.0,monthly_income_change=0.0):
    base=overview(transactions,current_balance=current_balance)['projected_month_end_balance'];return {'base_projected_balance':base,'scenario_projected_balance':base+monthly_income_change-monthly_extra_spend,'monthly_extra_spend':monthly_extra_spend,'monthly_income_change':monthly_income_change}


def income_vs_expense(transactions):
    df=frame(transactions)
    if df.empty:return pd.DataFrame(columns=['period','income','expense','net_cash_flow'])
    df['period']=df.date.dt.to_period('M').astype(str)
    income=df.loc[~_expense_mask(df)].groupby('period').amount.sum()
    expense=df.loc[_expense_mask(df)].groupby('period').amount.apply(lambda x: x.abs().sum())
    periods=sorted(set(income.index)|set(expense.index))
    return pd.DataFrame([{'period':p,'income':float(income.get(p,0)),'expense':float(expense.get(p,0)),'net_cash_flow':float(income.get(p,0)-expense.get(p,0))} for p in periods])

def seasonal_spending_patterns(transactions):
    df=frame(transactions)
    if df.empty:return pd.DataFrame(columns=['month','average_spending'])
    e=df[_expense_mask(df)].copy(); e['month']=e.date.dt.month
    out=e.groupby('month').amount.apply(lambda s:float(s.abs().mean())).reset_index(name='average_spending')
    return out.sort_values('month')

def rolling_spending_average(transactions, window=7):
    df=frame(transactions)
    if df.empty:return pd.DataFrame(columns=['date','spending','rolling_average'])
    e=df[_expense_mask(df)].copy(); daily=e.groupby(e.date.dt.floor('D')).amount.apply(lambda s:float(s.abs().sum())).rename('spending').reset_index()
    daily['rolling_average']=daily['spending'].rolling(window,min_periods=1).mean()
    return daily
