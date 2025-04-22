"""
포트폴리오 구성 설정
"""

import yaml
import os

def load_portfolio_configs():
    """포트폴리오 구성 파일을 로드합니다."""
    config_path = os.path.join(os.path.dirname(__file__), 'portfolio_configs.yaml')
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 포트폴리오 구성 로드
PORTFOLIO_CONFIGS = load_portfolio_configs() 