def compute_rolling_return(series, window_days=30):
    return series.pct_change(periods=window_days) * 100