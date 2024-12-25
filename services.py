import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

from constants import DOWNLOADS_DIR
from utils.logger_config import logger


def delete_csv_files():
    if os.path.exists(DOWNLOADS_DIR):
        for file in os.listdir(DOWNLOADS_DIR):
            if file.endswith('.csv'):
                file_path = os.path.join(DOWNLOADS_DIR, file)
                os.remove(file_path)
                logger.info(f"기존 CSV 파일 삭제: {file_path}")


def check_safe_download():
    max_wait_time = 10
    wait_time = 0
    csv_file_path = None

    while wait_time < max_wait_time:
        # downloads 디렉토리의 파일 확인
        files = os.listdir(DOWNLOADS_DIR)
        csv_files = [f for f in files if f.endswith('.csv')]

        if csv_files:
            csv_file_path = os.path.join(DOWNLOADS_DIR, csv_files[0])
            break

        time.sleep(1)
        wait_time += 1


    return csv_file_path


def get_last_row_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    last_row = df.iloc[-1]
    last_decision = last_row['decision']
    last_percentage = float(last_row['percentage']) if isinstance(
        last_row['percentage'], np.number) else last_row['percentage']
    last_timestamp = last_row['timestamp']
    last_reason = last_row['reason']
    last_reflection = last_row['reflection']

    logger.info(f"마지막 투자 방향: {last_decision}")
    logger.info(f"마지막 투자 분포율: {last_percentage}")
    logger.info(f"마지막 타임스탬프: {last_timestamp}")

    check_time_difference(last_timestamp)

    return {
        "decision": last_decision,
        "percentage": last_percentage,
        "timestamp": last_timestamp,
        "reason": last_reason,
        "reflection": last_reflection
    }


def check_time_difference(last_timestamp):
    last_time = datetime.fromisoformat(last_timestamp)
    current_time = datetime.now(timezone.utc) + timedelta(hours=9)
    time_difference = current_time - last_time

    if time_difference > timedelta(minutes=5):
        raise ValueError(f"마지막 타임스탬프가 현재 시간보다 5분 이상 지났습니다. 시간 차이: {time_difference}")


def calculate_order_amount(decision, percentage, accounts):
    btc_balance = 0
    krw_balance = 0
    order_amount = 0

    for account in accounts:
        if account['currency'] == 'BTC':
            btc_balance = float(account['balance'])
        elif account['currency'] == 'KRW':
            krw_balance = float(account['balance'])
    
    if decision == 'buy':
        order_amount = int(krw_balance * percentage)
    elif decision == 'sell':
        order_amount = round(btc_balance * percentage, 8)

    return order_amount