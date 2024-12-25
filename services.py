import os
import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from constants import DOWNLOADS_DIR
from utils.logger_config import logger
from utils.utils import translate_text_to_korean


def delete_csv_files():
    try:
        if os.path.exists(DOWNLOADS_DIR):
            for file in os.listdir(DOWNLOADS_DIR):
                if file.endswith('.csv'):
                    file_path = os.path.join(DOWNLOADS_DIR, file)
                    os.remove(file_path)
                    logger.info(f"기존 CSV 파일 삭제: {file_path}")
    except Exception as e:
        logger.error(f"기존 CSV 파일 삭제 중 오류 발생: {e}")


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
    time_difference = current_time.replace(tzinfo=None) - last_time

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


def send_trade_email(last_row_data, result):
    sender_email = os.environ['GOOGLE_EMAIL']
    receiver_email = os.environ['GOOGLE_EMAIL']
    password = os.environ['GOOGLE_PASSWORD']

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email 
    message["Subject"] = f"암호화폐 거래 알림: {last_row_data['decision']}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px; line-height: 1.6;">
        <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">거래 정보</h2>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">결정</h3>
            <p style="color: #34495e;">{last_row_data['decision']}</p>
        
            <h3 style="color: #2c3e50; margin: 20px 0 10px 0;">비율</h3>
            <p style="color: #34495e;">{last_row_data['percentage']}%</p>
        
            <h3 style="color: #2c3e50; margin: 20px 0 10px 0;">결정 근거</h3>
            <p style="color: #34495e;">{translate_text_to_korean(last_row_data['reason'])}</p>
        
            <h3 style="color: #2c3e50; margin: 20px 0 10px 0;">평가</h3>
            <p style="color: #34495e; white-space: pre-line;">{translate_text_to_korean(last_row_data['reflection']).replace('*', '').replace('**', '')}</p>

            <h3 style="color: #2c3e50; margin: 20px 0 10px 0;">주문 결과</h3>
            <div style="color: #34495e; background-color: #fff; padding: 10px; border-radius: 3px;">
                <pre style="white-space: pre-wrap; margin: 0;">{json.dumps(result, indent=2, ensure_ascii=False)}</pre>
            </div>
        </div>
    </div>
    """

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            message.attach(MIMEText(html_body, "html"))
            server.send_message(message)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")