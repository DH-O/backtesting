import pandas as pd
from logger import logger

def initialize_result_series(hist, ticker):
    """
    결과를 저장할 시리즈를 초기화합니다.
    
    Args:
        hist (pd.DataFrame): 주식 데이터
        ticker (str): 주식 티커 심볼
        
    Returns:
        tuple: (USD 시리즈, KRW 시리즈)
    """
    tr = pd.Series(index=hist.index, dtype='float64')
    tr_krw = pd.Series(index=hist.index, dtype='float64')
    return tr, tr_krw

def reindex_history(df, dates):
    """
    데이터프레임을 새로운 날짜 인덱스로 재인덱싱합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        dates (pd.DatetimeIndex): 새로운 날짜 인덱스
        
    Returns:
        pd.DataFrame: 재인덱싱된 데이터프레임
    """
    if df is None:
        return None
        
    # Close는 forward fill, Dividends는 0으로 채움
    df = df.reindex(dates)
    df['Close'] = df['Close'].ffill()
    df['Dividends'] = df['Dividends'].fillna(0)
    
    return df

def get_true_start(tickers, histories, weights):
    """
    실제 데이터가 시작되는 날짜를 찾습니다.
    
    Args:
        tickers (list): 티커 리스트
        histories (dict): 티커별 데이터
        weights (dict): 티커별 가중치
        
    Returns:
        datetime: 실제 시작 날짜
    """
    start_dates = []
    for ticker in tickers:
        if weights[ticker] > 0 and histories[ticker] is not None:
            start_dates.append(histories[ticker].index[0])
    
    if not start_dates:
        raise Exception("유효한 시작 날짜를 찾을 수 없습니다.")
        
    return max(start_dates) 