import pandas as pd

def compute_drawdown_with_info(series: pd.Series):
    """
    포트폴리오 비쥬얼라이저 방식의 드로우다운 계산 (시계열 기준)
    """
    # ... (기존 코드 동일) ...
    hwm = series.cummax()
    # Handle potential division by zero if hwm starts at 0
    drawdowns = pd.Series(0.0, index=series.index)
    non_zero_hwm = hwm != 0
    drawdowns[non_zero_hwm] = (series[non_zero_hwm] - hwm[non_zero_hwm]) / hwm[non_zero_hwm] * 100  # %

    max_dd = 0
    peak, trough, recovery = None, None, None
    # Handle empty or single-point series
    if len(series) < 2:
        return {
            'drawdowns': drawdowns, # Return the (potentially empty) series
            'max_drawdown': 0,
            'peak': None, 'trough': None, 'recovery': None,
            'dd_length': None, 'recovery_time': None, 'underwater_period': None
        }

    temp_peak_idx = 0 # Use index position for iloc
    temp_peak_date = series.index[temp_peak_idx]

    for i in range(1, len(series)):
        current_date = series.index[i]
        current_value = series.iloc[i]
        peak_value = series.iloc[temp_peak_idx] # Value at the current peak index

        if current_value >= peak_value:
            temp_peak_idx = i
            temp_peak_date = current_date

        # Calculate drawdown relative to the current peak value
        dd_now = 0.0
        if peak_value != 0: # Avoid division by zero
             dd_now = (current_value - peak_value) / peak_value * 100

        if dd_now < max_dd:
            max_dd = dd_now
            peak = temp_peak_date
            trough = current_date
            recovery = None # Reset recovery when a new low is found
        # Check for recovery only if we have a valid peak and trough
        elif peak is not None and trough is not None and recovery is None and current_value >= series[peak]:
             # Ensure we are comparing against the value at the actual peak date
            recovery = current_date

    # 기간 계산
    dd_length = (trough - peak).days if peak and trough else None
    recovery_time = (recovery - trough).days if trough and recovery else None
    underwater = (recovery - peak).days if peak and recovery else None

    return {
        'drawdowns': drawdowns, # The drawdown series itself
        'max_drawdown': max_dd,
        'peak': peak,
        'trough': trough,
        'recovery': recovery,
        'dd_length': dd_length,
        'recovery_time': recovery_time,
        'underwater_period': underwater
    }


def dual_mode_drawdown_analyzer(series: pd.Series, title='Portfolio'):
    """
    일간 및 월간 기준 드로우다운 분석 리포트.
    요약 DataFrame과 일간/월간 드로우다운 시계열을 반환합니다.
    """
    if series is None or series.empty:
        return {'summary': pd.DataFrame(), 'daily_series': pd.Series(), 'monthly_series': pd.Series()}

    # 일간 분석
    dd_daily_info = compute_drawdown_with_info(series)

    # 월간 리샘플링 후 분석
    # Ensure index is DatetimeIndex before resampling
    if not isinstance(series.index, pd.DatetimeIndex):
        try:
            series.index = pd.to_datetime(series.index)
        except Exception as e:
             print(f"Error converting index to DatetimeIndex: {e}")
             # Handle error appropriately, maybe return empty results
             return {'summary': pd.DataFrame(), 'daily_series': pd.Series(), 'monthly_series': pd.Series()}

    series_monthly = series.resample('ME').last()
    dd_monthly_info = compute_drawdown_with_info(series_monthly)

    # 결과를 DataFrame으로 정리
    results_df = pd.DataFrame({
        "Metric": [
            "Max Drawdown (%)",
            "Drawdown Start",
            "Drawdown Trough",
            "Recovery Point",
            "Drawdown Length (days)",
            "Recovery Time (days)",
            "Underwater Period (days)"
        ],
        "Daily": [
            f"{dd_daily_info['max_drawdown']:.2f}%",
            dd_daily_info['peak'].date() if dd_daily_info['peak'] else "N/A",
            dd_daily_info['trough'].date() if dd_daily_info['trough'] else "N/A",
            dd_daily_info['recovery'].date() if dd_daily_info['recovery'] else "N/A",
            dd_daily_info['dd_length'],
            dd_daily_info['recovery_time'],
            dd_daily_info['underwater_period']
        ],
        "Monthly": [
            f"{dd_monthly_info['max_drawdown']:.2f}%",
            dd_monthly_info['peak'].date() if dd_monthly_info['peak'] else "N/A",
            dd_monthly_info['trough'].date() if dd_monthly_info['trough'] else "N/A",
            dd_monthly_info['recovery'].date() if dd_monthly_info['recovery'] else "N/A",
            dd_monthly_info['dd_length'],
            dd_monthly_info['recovery_time'],
            dd_monthly_info['underwater_period']
        ]
    })

    # 요약 DataFrame과 함께 시계열 데이터 반환
    return {
        'summary': results_df,
        'daily_series': dd_daily_info['drawdowns'],
        'monthly_series': dd_monthly_info['drawdowns']
    }