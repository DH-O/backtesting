import yaml
from backtesting.DRIP_backtest_w_contirb import calc_tr_series_with_monthly_contrib
from backtesting.DRIP_backtest_w_contrib_PORT import run_backtest
from config import BACKTEST_CONFIG
from utils.plot_utils import save_portfolio_graphs

# 포트폴리오 구성 로드
with open("portfolio_configs.yaml", "r", encoding="utf-8") as f:  # 인코딩 명시
    portfolio_configs = yaml.safe_load(f)

print("Backtest Config:")
print(BACKTEST_CONFIG)

def main():
    results = {}
    for name, weights in portfolio_configs.items():
        cash_weight = 1.0 - sum(weights.values())
        print(f"{name} weights: {weights}")
        print(f"{name} cash_weight: {cash_weight}")
        results[name] = run_backtest(
            port_name=name,
            weights=weights,
            cash_weight=cash_weight,
            initial_investment=BACKTEST_CONFIG["initial_investment"],
            start_date=BACKTEST_CONFIG["start_date"],
            end_date=BACKTEST_CONFIG["end_date"],
            rebalance_period=BACKTEST_CONFIG["rebalance_period"],
            periodic_contribution=BACKTEST_CONFIG["periodic_contribution"],
            contribution_interval_days=BACKTEST_CONFIG["contribution_interval_days"]
        )

    # SPY DRIP 수익률 (비교용)
    results_baseline = calc_tr_series_with_monthly_contrib(
        "SPY",
        BACKTEST_CONFIG["start_date"],
        BACKTEST_CONFIG["end_date"],
        BACKTEST_CONFIG["initial_investment"],
        BACKTEST_CONFIG["periodic_contribution"],
        BACKTEST_CONFIG["contribution_interval_days"]
    )

    # 결과 저장 및 그래프 생성
    save_portfolio_graphs(results, results_baseline, log_dir="results")

if __name__ == "__main__":
    main()