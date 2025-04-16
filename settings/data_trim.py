import pandas as pd
from settings.utils import is_korean_etf

def initialize_result_series(hist, ticker):
    """결과를 저장할 시리즈를 초기화합니다."""
    tr = pd.Series(index=hist.index, dtype='float64')
    tr_krw = pd.Series(index=hist.index, dtype='float64') if not is_korean_etf(ticker) else None
    return tr, tr_krw

def reindex_history(df, all_dates):
    """
    주어진 DataFrame을 all_dates에 맞춰 reindex합니다.
    Close는 forward fill, Dividends는 없으면 0으로 채웁니다.
    """
    df = df.reindex(all_dates, method='ffill')
    df['Dividends'] = df['Dividends'].reindex(all_dates, fill_value=0)
    return df

def get_true_start(tickers, histories, weights):
    """유효한 시작일은 비중이 0이 아닌 티커들의 'Close'가 NaN이 아닌 첫 데이터 날짜 중 최대값."""
    valid_dates = []
    for t in tickers:
        if weights[t] > 0 and histories[t] is not None:
            first_valid = histories[t].dropna(subset=['Close']).index.min()
            valid_dates.append(first_valid)
    return max(pd.to_datetime(valid_dates))