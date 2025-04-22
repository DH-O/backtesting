"""
데이터 다운로드 관련 기능
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from finance.logger import logger

def download_data(ticker, start, end):
    """티커에 대한 가격 및 배당금 데이터를 다운로드합니다."""
    t = yf.Ticker(ticker)
    df = t.history(start=start, end=end, actions=True, auto_adjust=True)
    if df.empty:
        raise Exception(f"No data for {ticker}")
    df = df[['Close', 'Dividends']]
    df = df[~df.index.duplicated()]
    df.index = df.index.tz_localize(None)
    return df

def download_fx_data(start, end, all_dates):
    """환율 데이터를 다운로드하여 정렬합니다."""
    fx = yf.Ticker("USDKRW=X")
    fx_hist = fx.history(start=start, end=end)[['Close']]
    fx_hist.columns = ['FX']
    fx_hist.index = fx_hist.index.tz_localize(None)
    fx_hist = fx_hist.reindex(all_dates).ffill().bfill()
    if fx_hist['FX'].isna().sum() > 0:
        print("❗ 환율 데이터에 NaN 존재:", fx_hist[fx_hist['FX'].isna()].head())
    return fx_hist