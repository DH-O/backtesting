from settings.utils import is_korean_etf

def initialize_portfolio(tickers, histories, weights, cash_weight, initial_investment, fx_hist, first_date):
    """
    초기 투자 시 각 티커별 주식 수와 현금 금액(USD)을 계산합니다.
    한국 상장 ETF의 경우 환율을 곱한 KRW 기준으로 초기 투자했다고 가정합니다.
    """
    shares_owned = {}
    for ticker in tickers:
        price = histories[ticker].loc[first_date, 'Close']
        if is_korean_etf(ticker):
            # 한국 ETF: 초기투자금에 환율 적용하여 KRW 기준 금액으로 계산한 후, 실제 가격(USD값)을 나눔.
            shares_owned[ticker] = (initial_investment * weights[ticker] * fx_hist.loc[first_date, 'FX']) / price
        else:
            shares_owned[ticker] = (initial_investment * weights[ticker]) / price
    cash_usd = initial_investment * cash_weight
    return shares_owned, cash_usd

def recalculate_portfolio(tickers, weights, histories, date, shares_owned, fx_hist, cash_now_usd):
    total_value_usd = 0
    for ticker in tickers:
        if weights[ticker] == 0.0:
            continue
        hist = histories[ticker]
        if hist is None:
            raise Exception(f"No data for {ticker}")
            continue
        row = hist.loc[date]
        if is_korean_etf(ticker):
            total_value_usd += shares_owned[ticker] * (row['Close'] / fx_hist.loc[date, 'FX'])
        else:
            total_value_usd += shares_owned[ticker] * row['Close']
    total_value_usd += cash_now_usd
    return total_value_usd