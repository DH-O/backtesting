import logging
import os
from datetime import datetime

def setup_logger():
    # 현재 작업 디렉토리를 기준으로 로그 디렉토리 설정
    current_dir = os.getcwd()
    LOG_DIR = os.path.join(current_dir, 'logs')
    
    # 로그 디렉토리 생성
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"로그 디렉토리 생성됨: {LOG_DIR}")

    # 로그 파일명 설정 (날짜 포함)
    LOG_FILE = os.path.join(LOG_DIR, f'finance_{datetime.now().strftime("%Y%m%d")}.log')
    print(f"로그 파일 경로: {LOG_FILE}")

    # 로거 설정
    logger = logging.getLogger('finance')
    logger.setLevel(logging.INFO)

    # 기존 핸들러 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()

    # 파일 핸들러 설정
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.INFO)

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 로그 초기화 확인
    logger.info('로깅 시스템이 초기화되었습니다.')
    logger.info(f'로그 파일 경로: {LOG_FILE}')
    
    return logger

# 로거 초기화
logger = setup_logger()

# 로그 예시
logger.info('로깅 시스템이 초기화되었습니다.') 