from __future__ import annotations
import pandas as pd
from analytics.financial import frame,_expense_mask

def _series(transactions):
    df=frame(transactions)
    if df.empty:return pd.Series(dtype=float)
    e=df[_expense_mask(df)].copy();e['period']=e.date.dt.to_period('M').astype(str);return e.groupby('period').amount.apply(lambda s:float(s.abs().sum())).sort_index()
def naive(transactions):
    s=_series(transactions);return float(s.iloc[-1]) if len(s) else 0.0
def moving_average(transactions,window=3):
    s=_series(transactions);return float(s.tail(window).mean()) if len(s) else 0.0
def weighted_moving_average(transactions,window=3):
    s=_series(transactions).tail(window)
    if s.empty:return 0.0
    weights=list(range(1,len(s)+1));return float(sum(v*w for v,w in zip(s.tolist(),weights))/sum(weights))
def compare(transactions):
    s=_series(transactions)
    models={'naive':naive(transactions),'moving_average':moving_average(transactions),'weighted_moving_average':weighted_moving_average(transactions)}
    if len(s)<4:return {'models':models,'selected':'moving_average' if len(s)>1 else 'naive','holdout_evaluated':False,'limitation':'At least four monthly observations are needed for a holdout comparison.'}
    train=s.iloc[:-1];actual=float(s.iloc[-1]);preds={'naive':float(train.iloc[-1]),'moving_average':float(train.tail(3).mean()),'weighted_moving_average':float(sum(v*w for v,w in zip(train.tail(3),[1,2,3]))/6)};errors={k:abs(v-actual) for k,v in preds.items()};selected=min(errors,key=errors.get)
    return {'models':models,'selected':selected,'holdout_evaluated':True,'holdout_actual':actual,'holdout_errors':errors,'limitation':'Historical holdout error is not a statistical confidence interval.'}
