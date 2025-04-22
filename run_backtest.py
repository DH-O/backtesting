from backtesting.DRIP_backtest_w_contirb import calc_tr_series_with_monthly_contrib
from backtesting.DRIP_backtest_w_contrib_PORT import run_backtest
from config import BACKTEST_CONFIG, PORTFOLIO_CONFIGS
from utils.plot_utils import save_portfolio_graphs
import logging
from finance.logger import logger

logger.info("=== 백테스트 시작 ===")
logger.info(f"백테스트 설정: {BACKTEST_CONFIG}")
logger.info(f"포트폴리오 구성: {PORTFOLIO_CONFIGS}")

def main():
    results = {}
    for name, weights in PORTFOLIO_CONFIGS.items():
        cash_weight = 1.0 - sum(weights.values())
        logger.info(f"=== {name} 포트폴리오 백테스트 시작 ===")
        logger.info(f"자산 가중치: {weights}")
        logger.info(f"현금 가중치: {cash_weight}")
        
        try:
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
            logger.info(f"{name} 포트폴리오 백테스트 완료")
        except Exception as e:
            logger.error(f"{name} 포트폴리오 백테스트 중 에러 발생: {str(e)}", exc_info=True)
            continue

    # SPY DRIP 수익률 (비교용)
    logger.info("=== SPY DRIP 백테스트 시작 ===")
    try:
        results_baseline = calc_tr_series_with_monthly_contrib(
            "SPY",
            BACKTEST_CONFIG["start_date"],
            BACKTEST_CONFIG["end_date"],
            BACKTEST_CONFIG["initial_investment"],
            BACKTEST_CONFIG["periodic_contribution"],
            BACKTEST_CONFIG["contribution_interval_days"]
        )
        logger.info("SPY DRIP 백테스트 완료")
    except Exception as e:
        logger.error(f"SPY DRIP 백테스트 중 에러 발생: {str(e)}", exc_info=True)
        return

    # 결과 저장 및 그래프 생성
    try:
        save_portfolio_graphs(results, results_baseline, log_dir="results")
        logger.info("포트폴리오 그래프 저장 완료")
    except Exception as e:
        logger.error(f"그래프 저장 중 에러 발생: {str(e)}", exc_info=True)

    logger.info("=== 백테스트 종료 ===")

if __name__ == "__main__":
    main()