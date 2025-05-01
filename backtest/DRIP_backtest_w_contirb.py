import pandas as pd
from settings.data_download import download_data, download_fx_data
from settings.data_trim import initialize_result_series
from settings.invest import initialize_investment, apply_monthly_contribution, reinvest_dividends
from analysis.risk.calc_drawdowns import dual_mode_drawdown_analyzer
from analysis.returns.calc_return import compute_rolling_return


def calc_tr_series_with_monthly_contrib(ticker, start, end, initial_investment,
                                        periodic_contribution=0, interval_days=30):
    # 데이터 다운로드
    hist = download_data(ticker, start, end)
    if hist is None:
        return None

    fx_hist = download_fx_data(start, end, hist.index)

    # 초기 투자 및 주식 보유 수 설정
    shares, invested = initialize_investment(ticker, hist, initial_investment, fx_hist)

    # 결과를 저장할 시리즈 초기화
    tr, tr_krw = initialize_result_series(hist, ticker)
    tr[hist.index[0]] = invested

    # 백테스트 시작
    last_invest_date = hist.index[0]
    for date in hist.index:
        price = hist.loc[date, 'Close']

        # 월별 투자 검증 및 추가
        if (date - last_invest_date).days >= interval_days:
            shares, invested = apply_monthly_contribution(shares, price, periodic_contribution)
            last_invest_date = date

        # 배당금 재투자
        shares = reinvest_dividends(shares, price, hist.loc[date, 'Dividends'])

        # 총 가치 계산 및 기록
        tr.loc[date] = shares * price
        if tr_krw is not None:
            tr_krw.loc[date] = shares * price * fx_hist.loc[date, 'FX']

    # 드로우다운 분석
    dd_analysis_usd = dual_mode_drawdown_analyzer(tr, title=ticker + ' (USD)') if tr is not None and not tr.empty else {'summary': pd.DataFrame(), 'daily_series': pd.Series()}
    dd_analysis_krw = dual_mode_drawdown_analyzer(tr_krw, title=ticker + ' (KRW)') if tr_krw is not None and not tr_krw.empty else {'summary': pd.DataFrame(), 'daily_series': pd.Series()}

    # 필요한 데이터 추출 (요약 DataFrame에서)
    max_drawdown_usd = None
    if not dd_analysis_usd['summary'].empty:
        max_drawdown_usd_str = dd_analysis_usd['summary'].loc[dd_analysis_usd['summary']['Metric'] == "Max Drawdown (%)", "Daily"].values[0]
        try:
            # Extract float value from string like "-12.34%"
            max_drawdown_usd = float(max_drawdown_usd_str.replace('%', ''))
        except:
            max_drawdown_usd = None # Handle cases like "N/A" or parsing errors

    max_drawdown_krw = None
    if not dd_analysis_krw['summary'].empty:
        max_drawdown_krw_str = dd_analysis_krw['summary'].loc[dd_analysis_krw['summary']['Metric'] == "Max Drawdown (%)", "Daily"].values[0]
        try:
            max_drawdown_krw = float(max_drawdown_krw_str.replace('%', ''))
        except:
             max_drawdown_krw = None

    rolling_returns = {
        '10y': compute_rolling_return(tr, window_days=3650),
        '5y': compute_rolling_return(tr, window_days=1825),
        '1y': compute_rolling_return(tr, window_days=365),
        '6m': compute_rolling_return(tr, window_days=180),
        '3m': compute_rolling_return(tr, window_days=90),
        '1m': compute_rolling_return(tr, window_days=30)
    }

    return {
        'cumulative_ratio': tr / tr.iloc[0] if tr is not None and not tr.empty and tr.iloc[0] != 0 else pd.Series(),
        'cumulative_value': tr,
        'cumulative_value_krw': tr_krw,
        'drawdown_summary': dd_analysis_usd['summary'], # 요약 DataFrame
        'drawdowns': dd_analysis_usd['monthly_series'],   # 월간 드로우다운 시계열
        'max_drawdown': max_drawdown_usd,
        'drawdown_summary_krw': dd_analysis_krw['summary'], # KRW 요약 DataFrame
        'drawdowns_krw': dd_analysis_krw['monthly_series'],    # KRW 월간 드로우다운 시계열
        'max_drawdown_krw': max_drawdown_krw,
        'rolling_returns': rolling_returns,
        'total_invested': invested
    }