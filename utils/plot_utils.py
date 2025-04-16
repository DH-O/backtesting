import os
from matplotlib import pyplot as plt
import pandas as pd

def save_portfolio_graphs(results, results_baseline, log_dir="results"):
    # 결과 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    excel_dir = os.path.join(log_dir, "excels")
    graph_dir = os.path.join(log_dir, "graphs")
    os.makedirs(excel_dir, exist_ok=True)
    os.makedirs(graph_dir, exist_ok=True)

    # 포트폴리오 비교 그래프
    plt.figure(figsize=(12, 6))
    for name, res in results.items():
        plt.plot(res['cumulative_value_KRW'], label=name)
        res['log'].to_excel(os.path.join(excel_dir, f"{name}.xlsx"))

        # 드로우다운 분석 결과 저장
        drawdown_results = res['drawdowns']
        if isinstance(drawdown_results, pd.DataFrame):
            drawdown_series = drawdown_results['drawdowns']  # DataFrame에서 특정 열 선택
        elif isinstance(drawdown_results, pd.Series):
            drawdown_series = drawdown_results  # 이미 Series인 경우
        else:
            drawdown_series = pd.Series(drawdown_results)  # numpy.ndarray를 Series로 변환

        drawdown_series.to_excel(os.path.join(excel_dir, f"{name}_drawdowns.xlsx"))

    if results_baseline['cumulative_value_krw'] is not None:
        plt.plot(results_baseline['cumulative_value_krw'], label="SPY (DRIP)", linestyle="--")
        plt.yscale("log")
        plt.title("Portfolio Balance Comparison (Log Scale, KRW)")
        plt.legend()
        plt.grid(True, which="both", linestyle="--")
        plt.tight_layout()
        plt.savefig(os.path.join(graph_dir, "all_portfolios_logscale.png"))
        plt.close()

        # SPY 드로우다운 분석 결과 저장
        baseline_drawdown_results = results_baseline['drawdowns']
        if isinstance(baseline_drawdown_results, pd.DataFrame):
            baseline_drawdown_series = baseline_drawdown_results['drawdowns']
        elif isinstance(baseline_drawdown_results, pd.Series):
            baseline_drawdown_series = baseline_drawdown_results
        else:
            baseline_drawdown_series = pd.Series(baseline_drawdown_results)

        baseline_drawdown_series.to_excel(os.path.join(excel_dir, "SPY_drawdowns.xlsx"))

    # 드로우다운 그래프
    plt.figure(figsize=(12, 6))
    for name, res in results.items():
        drawdown_results = res['drawdowns']
        if isinstance(drawdown_results, pd.DataFrame):
            drawdown_series = drawdown_results['drawdowns']
        elif isinstance(drawdown_results, pd.Series):
            drawdown_series = drawdown_results
        else:
            drawdown_series = pd.Series(drawdown_results)

        plt.plot(drawdown_series, label=name)

    if results_baseline['drawdowns'] is not None:
        baseline_drawdown_results = results_baseline['drawdowns']
        if isinstance(baseline_drawdown_results, pd.DataFrame):
            baseline_drawdown_series = baseline_drawdown_results['drawdowns']
        elif isinstance(baseline_drawdown_results, pd.Series):
            baseline_drawdown_series = baseline_drawdown_results
        else:
            baseline_drawdown_series = pd.Series(baseline_drawdown_results)

        plt.plot(baseline_drawdown_series, label="SPY (DRIP)", linestyle="--")

    plt.title("Drawdown")
    plt.ylabel("Drawdown (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(graph_dir, "all_port_drawdowns.png"))
    plt.close()