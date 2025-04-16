import math
import pandas as pd
from settings.utils import is_korean_etf
from settings.data_trim import reindex_history, get_true_start
from settings.data_download import download_data, download_fx_data
from statistics.calc_drawdowns import dual_mode_drawdown_analyzer
from statistics.calc_return import compute_rolling_return
from backtesting.portfolio import initialize_portfolio, recalculate_portfolio

def run_backtest(port_name, weights, cash_weight,
                 initial_investment,
                 start_date, end_date,
                 rebalance_period=122,
                 periodic_contribution=140,
                 contribution_interval_days=30):

  if not math.isclose(sum(weights.values()) + cash_weight, 1.0, rel_tol=1e-6):
      print(weights)
      print(sum(weights.values()))
      print(cash_weight)
      print(sum(weights.values()) + cash_weight)
      raise Exception("Weights must sum to 1")

  tickers = [t for t in weights if t != 'cash']

  histories = {}
  for ticker in tickers:
      histories[ticker] = download_data(ticker, start_date, end_date)

  # ✅ 실제 데이터가 존재하는 날짜들의 합집합 사용 (개별 티커 날짜의 union)
  all_dates = sorted(set.intersection(*[set(df.index) for df in histories.values() if df is not None]))
  # all_dates = sorted(set().union(*[df.index for df in histories.values() if df is not None]))
  # 필요에 따라, asfreq('B')를 사용하면 영업일 전체로 확장되지만,
  # 여기서는 forward fill을 위해 전체 날짜 인덱스(all_dates)를 그대로 사용합니다.
  # 야후파이낸스에서 영업일 기준으로만 종가를 제공하지만, 혹시 모를 오류때문에 저런 행위를 한다고 생각합니다.
  all_dates = pd.to_datetime(all_dates) # pd.DatetimeIndex 타입이 된다.

  # ✅ 각 티커별 데이터프레임을 all_dates로 재인덱싱 (Close는 forward fill, Dividends는 없으면 0)
  for ticker, df in histories.items():
      histories[ticker] = reindex_history(df, all_dates)

  # all_dates를 true_start 이후로 제한
  true_start = get_true_start(tickers, histories, weights)
  all_dates = all_dates[all_dates >= true_start]
  print(f'all_dates 시작일: ', all_dates[0])

  # 환율 데이터 다운로드
  fx_hist = download_fx_data(start_date, end_date, all_dates)
  # ✅ 초기화
  portfolio_cumulative_usd = pd.Series(index=all_dates, dtype='float64')
  portfolio_cumulative_krw = pd.Series(index=all_dates, dtype='float64')
  record = [] # 엑셀에 값들 저장하기 위함

  # ★ 초기 리밸런싱: 첫 번째 날짜에서 초기 투자금을 기준으로 각 티커별 보유 주식 수 산정
  first_date = all_dates[0]
  shares_owned, cash_now_usd = initialize_portfolio(tickers, histories, weights, cash_weight, initial_investment, fx_hist, first_date)
  total_value_usd = initial_investment
  portfolio_cumulative_usd.loc[first_date] = total_value_usd
  portfolio_cumulative_krw.loc[first_date] = total_value_usd * fx_hist.loc[first_date, 'FX']

  # ✅ 백테스트 루프 (첫 날 이후)
  last_invest_date = all_dates[0]
  last_rebalance_date = all_dates[0]

  for date in all_dates[1:]:
      # 투자 간격이 일정 기간을 초과했는지 확인
      if (date - last_invest_date).days >= contribution_interval_days:
          # 일단 현금 보유량에 monthly_contribution 더하기
          cash_now_usd += periodic_contribution
          for ticker in tickers:
              if weights[ticker] == 0.0:
                  continue
              price = histories[ticker].loc[date, 'Close']
              # monthly_contribution에 weights[ticker]만큼 주식 사기
              if is_korean_etf(ticker):
                  shares_owned[ticker] += (periodic_contribution * fx_hist.loc[first_date, 'FX'] * weights[ticker]) / price
              else:
                  shares_owned[ticker] += (periodic_contribution * weights[ticker]) / price
              # 쓴 돈만큼 cash_now에서 차감
              cash_now_usd -= periodic_contribution * weights[ticker]
          last_invest_date = date

      # 1. 당일 배당 처리 (모든 티커에 대해)
      for ticker in tickers:
          if weights[ticker] == 0.0:
              continue
          # 이미 모든 날짜에 대해 reindex했으므로 항상 row가 있음
          row = histories[ticker].loc[date]
          if row['Dividends'] > 0:
              # 배당 재투자: 보유 주식수 증가
              total_dividend = shares_owned[ticker] * row['Dividends']  # 전체 배당금
              shares_owned[ticker] += total_dividend / row['Close']     # 그걸로 다시 주식 구매

      # 2. 배당 반영 후, 해당 날짜의 포트폴리오 총가치 계산
      total_value_usd = recalculate_portfolio(tickers, weights, histories, date, shares_owned, fx_hist, cash_now_usd)

      # 3. 리밸런싱 (리밸런싱 날짜에 해당하면)
      if (date - last_rebalance_date).days >= rebalance_period:
          # 현금과 각 자산의 비율을 정확하게 재설정
          portfolio_value_usd = total_value_usd  # 현재 총 포트폴리오 가치
          cash_now_usd = portfolio_value_usd * cash_weight  # 현금 비중을 유지

          # 각 자산에 대한 비중에 맞춰 주식 수 재설정
          for ticker in tickers:
              if weights[ticker] == 0.0:
                  continue
              price = histories[ticker].loc[date, 'Close']  # forward fill 덕분에 항상 값이 있음
              if is_korean_etf(ticker):
                  shares_owned[ticker] = portfolio_value_usd * fx_hist.loc[date, 'FX'] * weights[ticker] / price
              else:
                  shares_owned[ticker] = portfolio_value_usd * weights[ticker] / price

          # 리밸런싱 후, 재설정된 보유 주식수로 포트폴리오 가치 재계산
          total_value_usd = recalculate_portfolio(tickers, weights, histories, date, shares_owned, fx_hist, cash_now_usd)

          last_rebalance_date = date
      portfolio_cumulative_usd.loc[date] = total_value_usd
      portfolio_cumulative_krw.loc[date] = total_value_usd * fx_hist.loc[date, 'FX']

      # 엑셀에 기록할 데이터
      row_data = {
          'Date': date,
          'Cash_USD': cash_now_usd,
          'Cash_KRW': (cash_now_usd * fx_hist.loc[date, 'FX']),
          'Total Value_USD': total_value_usd,
          'Total Value_KRW': total_value_usd * fx_hist.loc[date, 'FX'],
          'Exchange_Rate': fx_hist.loc[date, 'FX']
      }
      for ticker in tickers:
        if weights[ticker] > 0:
            shares = shares_owned.get(ticker, 0)
            price = histories[ticker].loc[date, 'Close']

            row_data[f'{ticker} Shares'] = shares
            if is_korean_etf(ticker):
                row_data[f'{ticker} Value (KRW)'] = shares * price
            else:
                row_data[f'{ticker} Value'] = shares * price
                row_data[f'{ticker} Value (KRW)'] = shares * price * fx_hist.loc[date, 'FX']
      record.append(row_data)

  # 루프 종료 후 엑셀 저장
  df_record = pd.DataFrame(record).set_index('Date')

  # ✅ 정규화
  portfolio_cumulative_usd = portfolio_cumulative_usd.dropna()
  portfolio_cumulative_krw = portfolio_cumulative_krw.dropna()
  portfolio_cumulative_normalized = portfolio_cumulative_usd / portfolio_cumulative_usd.iloc[0] if not portfolio_cumulative_usd.empty else pd.Series(dtype='float64')

  # 드로우다운 분석
  dd_analysis_usd = dual_mode_drawdown_analyzer(portfolio_cumulative_usd, title=port_name + ' (USD)')
  dd_analysis_krw = dual_mode_drawdown_analyzer(portfolio_cumulative_krw, title=port_name + ' (KRW)') if fx_hist is not None else {'summary': pd.DataFrame(), 'daily_series': pd.Series()}

  # 필요한 데이터 추출 (요약 DataFrame에서)
  max_drawdown_usd = None
  if not dd_analysis_usd['summary'].empty:
      max_drawdown_usd_str = dd_analysis_usd['summary'].loc[dd_analysis_usd['summary']['Metric'] == "Max Drawdown (%)", "Daily"].values[0]
      try:
          max_drawdown_usd = float(max_drawdown_usd_str.replace('%', ''))
      except:
           max_drawdown_usd = None

  max_drawdown_krw = None
  if not dd_analysis_krw['summary'].empty:
      max_drawdown_krw_str = dd_analysis_krw['summary'].loc[dd_analysis_krw['summary']['Metric'] == "Max Drawdown (%)", "Daily"].values[0]
      try:
          max_drawdown_krw = float(max_drawdown_krw_str.replace('%', ''))
      except:
           max_drawdown_krw = None

  rolling_returns = {
      '10y': compute_rolling_return(portfolio_cumulative_krw, window_days=3650),
      '5y': compute_rolling_return(portfolio_cumulative_krw, window_days=1825),
      '1y': compute_rolling_return(portfolio_cumulative_krw, window_days=365),
      '6m': compute_rolling_return(portfolio_cumulative_krw, window_days=180),
      '3m': compute_rolling_return(portfolio_cumulative_krw, window_days=90),
      '1m': compute_rolling_return(portfolio_cumulative_krw, window_days=30)
  }

  return {
      'cumulative_ratio': portfolio_cumulative_normalized,
      'cumulative_value_USD': portfolio_cumulative_usd,
      'cumulative_value_KRW': portfolio_cumulative_krw,
      'drawdown_summary': dd_analysis_usd['summary'], # 요약 DataFrame
      'drawdowns': dd_analysis_usd['monthly_series'],   # 월간 드로우다운 시계열
      'max_drawdown': max_drawdown_usd,
      'drawdown_summary_KRW': dd_analysis_krw['summary'], # KRW 요약 DataFrame
      'drawdowns_KRW': dd_analysis_krw['monthly_series'],    # KRW 월간 드로우다운 시계열
      'max_drawdown_KRW': max_drawdown_krw,
      'rolling_returns': rolling_returns,
      'log': df_record
  }