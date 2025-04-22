"""
포트폴리오 자산들의 상관관계 분석
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from config.portfolio import PORTFOLIO_CONFIGS
from finance.logger import logger

# 티커 정보 딕셔너리
TICKER_INFO = {
    '000660.KS': 'SK Hynix',
    '003230.KS': 'Samyang Foods',
    '005380.KS': 'Hyundai Motor',
    '005930.KS': 'Samsung Electronics',
    '006400.KS': 'Samsung SDI',
    '035420.KS': 'NAVER',
    '161510.KS': 'ARIRANG High Dividend',
    '294400.KS': 'KODEX KOSPI200',
    '411060.KS': 'ACE KRX Gold',
    '438900.KS': 'KODEX Food',
    '449450.KS': 'KODEX Defense',
    '456610.KS': 'KODEX SOFR',
    '458730.KS': 'KODEX Dow Jones Dividend',
    '473590.KS': 'KODEX Bestseller',
    '475350.KS': 'KODEX Berkshire Top 10',
    '481190.KS': 'KODEX US Top 10',
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'NVDA': 'NVIDIA',
    'SOL-USD': 'Solana'
}

def get_portfolio_correlation(lookback_days=365):
    """
    포트폴리오에 있는 모든 자산들의 상관관계를 계산합니다.
    
    Args:
        lookback_days (int): 분석할 과거 데이터 기간 (일)
    """
    try:
        # 모든 포트폴리오에서 유니크한 티커 추출
        all_tickers = set()
        for portfolio in PORTFOLIO_CONFIGS.values():
            all_tickers.update(portfolio.keys())
        
        logger.info(f"분석 대상 티커 ({len(all_tickers)}개): {sorted(all_tickers)}")
        
        # 날짜 범위 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        logger.info(f"분석 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        # 각 자산의 수익률 데이터 가져오기
        all_prices = pd.DataFrame()
        
        for ticker in sorted(all_tickers):
            try:
                logger.info(f"{ticker} 데이터 로드 중...")
                data = yf.download(
                    ticker, 
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    progress=False,
                    auto_adjust=True
                )
                
                if not data.empty and 'Close' in data.columns:
                    all_prices[ticker] = data['Close']
                    logger.info(f"{ticker} 데이터 로드 성공 (데이터 수: {len(data)})")
                else:
                    logger.warning(f"{ticker} 데이터가 비어있거나 종가 정보가 없습니다.")
            except Exception as e:
                logger.error(f"{ticker} 데이터 로드 중 에러 발생: {str(e)}")
                continue
        
        if all_prices.empty:
            logger.error("가격 데이터가 없습니다.")
            return None
        
        # 결측치가 있는 날짜 제거
        all_prices = all_prices.dropna()
        
        logger.info(f"공통 거래일 수: {len(all_prices)}")
        if len(all_prices) > 0:
            logger.info(f"분석 기간: {all_prices.index[0].strftime('%Y-%m-%d')} ~ {all_prices.index[-1].strftime('%Y-%m-%d')}")
            
            # 일간 수익률 계산
            returns_df = all_prices.pct_change().dropna()
            
            # 상관관계 행렬 계산
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
        else:
            logger.error("공통된 거래일이 없습니다.")
            return None
    
    except Exception as e:
        logger.error(f"상관관계 계산 중 에러 발생: {str(e)}")
        return None

def save_correlation_heatmap(correlation_matrix, output_dir="analysis_results"):
    """
    상관관계 히트맵을 저장합니다.
    """
    try:
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 히트맵 생성
        plt.figure(figsize=(20, 16))
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   fmt='.2f', 
                   cmap='coolwarm',
                   center=0,
                   square=True,
                   xticklabels=[f"{ticker}\n{TICKER_INFO[ticker]}" for ticker in correlation_matrix.columns],
                   yticklabels=[f"{ticker}\n{TICKER_INFO[ticker]}" for ticker in correlation_matrix.index])
        plt.title('Portfolio Asset Correlation Heatmap', pad=20, fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        # 히트맵 저장
        heatmap_file = os.path.join(output_dir, 'portfolio_correlation_heatmap.png')
        plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
        logger.info(f"히트맵이 '{heatmap_file}' 파일로 저장되었습니다.")
        
    except Exception as e:
        logger.error(f"히트맵 저장 중 에러 발생: {str(e)}")

if __name__ == "__main__":
    # 테스트 실행
    correlation_matrix = get_portfolio_correlation()
    if correlation_matrix is not None:
        save_correlation_heatmap(correlation_matrix) 