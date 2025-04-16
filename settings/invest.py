from settings.utils import is_korean_etf

def initialize_investment(ticker, hist, initial_investment, fx_hist):
    """초기 투자 금액과 주식 보유 수를 설정합니다."""
    if is_korean_etf(ticker):
        invested = initial_investment * fx_hist.loc[hist.index[0], 'FX']
    else:
        invested = initial_investment
    shares = invested / hist.loc[hist.index[0], 'Close']
    return shares, invested

def apply_monthly_contribution(shares, price, periodic_contribution):
    """월별 투자 금액을 주식에 재투자합니다."""
    shares += periodic_contribution / price
    invested = shares * price
    return shares, invested

def reinvest_dividends(shares, price, dividend):
    """배당금을 재투자하여 주식을 추가합니다."""
    if dividend > 0:
        shares += (shares * dividend) / price
    return shares