"""
백테스트 관련 설정
"""

BACKTEST_CONFIG = {
    "initial_investment": 150000,  # 초기 투자금액
    "start_date": "2024-02-27",    # 백테스트 시작일
    "end_date": "2025-04-30",      # 백테스트 종료일
    "periodic_contribution": 140,   # 정기 투자금액
    "contribution_interval_days": 30,  # 투자 주기 (일)
    "rebalance_period": 30          # 리밸런싱 주기 (일)
} 