import pandas as pd
from models import Record

def records_to_df(records):
    """
    Convert a list of Record objects to a pandas DataFrame.
    """
    rows = [r.to_dict() for r in records]
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    df['recorded_at'] = pd.to_datetime(df['recorded_at'])
    return df

def timeseries(records, freq='D'):
    """
    Aggregate records by recorded_at datetime with the specified frequency.
    freq: 'D' = daily, 'W' = weekly, 'M' = monthly, etc.
    """
    df = records_to_df(records)
    if df.empty:
        return pd.DataFrame()
    
    ts = df.set_index('recorded_at').resample(freq)['amount'].sum().reset_index()
    return ts
