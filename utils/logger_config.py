import logging
import sys

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 이미 핸들러가 있다면 제거
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 콘솔 핸들러만 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)

    return logger

# 글로벌 logger 설정
logger = setup_logger()
