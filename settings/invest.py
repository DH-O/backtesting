import pandas as pd
from finance.logger import logger

def initialize_investment(ticker, hist, initial_investment, fx_hist):
    """
    초기 투자를 설정합니다.
    
    Args:
        ticker (str): 주식 티커
        hist (pd.DataFrame): 주식 데이터
        initial_investment (float): 초기 투자 금액
        fx_hist (pd.DataFrame): 환율 데이터
        
    Returns:
        tuple: (보유 주식 수, 투자 금액)
    """
    first_price = hist.loc[hist.index[0], 'Close']
    shares = initial_investment / first_price
    invested = initial_investment
    return shares, invested

def apply_monthly_contribution(shares, price, contribution):
    """
    월별 투자를 적용합니다.
    
    Args:
        shares (float): 현재 보유 주식 수
        price (float): 현재 주가
        contribution (float): 추가 투자 금액
        
    Returns:
        tuple: (새로운 보유 주식 수, 총 투자 금액)
    """
    new_shares = contribution / price
    total_shares = shares + new_shares
    total_invested = total_shares * price
    return total_shares, total_invested

def reinvest_dividends(shares, price, dividend):
    """
    배당금을 재투자합니다.
    
    Args:
        shares (float): 현재 보유 주식 수
        price (float): 현재 주가
        dividend (float): 배당금
        
    Returns:
        float: 새로운 보유 주식 수
    """
    if dividend > 0:
        total_dividend = shares * dividend
        new_shares = total_dividend / price
        return shares + new_shares
    return shares 