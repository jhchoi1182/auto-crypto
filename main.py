import time
import os
import pandas as pd
import logging
import numpy as np
from datetime import datetime, timedelta
from fastapi import FastAPI

from selenium_utils.selenium_settings import init_driver
from selenium_utils.actions import click_download_button
from utils.utils import translate_text_to_korean

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI()


@app.get('/test-csv')
def test_csv():
    _, csv_file_path = check_safe_download()
    last_row_data = get_last_row_data(csv_file_path)
    return {"message": "CSV 파일 읽기 완료", "last_row_data": last_row_data}

@app.get("/hi")
def auto_crypto():
    driver = None
    try:
        driver = init_driver()
        url = 'http://3.35.214.209:8501/'
        driver.get(url)

        # 페이지가 로드될 때까지 기다림
        time.sleep(1)
        click_download_button(driver)
        download_complete, csv_file_path = check_safe_download()

        if download_complete and csv_file_path:
            last_row_data = get_last_row_data(csv_file_path)

            return {
                "status": "success",
                "message": "File processed successfully",
                "last_row_data": last_row_data
            }
        else:
            return {
                "status": "error",
                "message": "Download timeout"
            }

    except Exception as e:
        # 이상 상황에 대해 알람을 울려야함
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
    finally:
        if driver:
            driver.quit()


def check_safe_download():
    downloads_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "downloads")
    max_wait_time = 10
    wait_time = 0
    download_complete = False
    csv_file_path = None

    while wait_time < max_wait_time:
        # downloads 디렉토리의 파일 확인
        files = os.listdir(downloads_path)
        csv_files = [f for f in files if f.endswith('.csv')]

        if csv_files:
            csv_file_path = os.path.join(downloads_path, csv_files[0])
            download_complete = True
            break

        time.sleep(1)
        wait_time += 1

    return download_complete, csv_file_path


def get_last_row_data(csv_file_path):
    df = pd.read_csv(csv_file_path)

    last_row = df.iloc[-1]
    last_decision = last_row['decision']
    last_percentage = float(last_row['percentage']) if isinstance(
        last_row['percentage'], np.number) else last_row['percentage']
    last_timestamp = last_row['timestamp']
    last_reason = last_row['reason']
    last_reflection = last_row['reflection']

    # check_time_difference(last_timestamp)

    logging.info(f"마지막 행 정보:")
    logging.info(f"Decision: {last_decision}")
    logging.info(f"Percentage: {last_percentage}")
    logging.info(f"Timestamp: {last_timestamp}")
    logging.info(f"Reason: {last_reason}")
    logging.info(f"Reflection: {last_reflection}")

    return {
        "decision": last_decision,
        "percentage": last_percentage,
        "timestamp": last_timestamp,
        "reason": last_reason,
        "reflection": last_reflection
    }


def check_time_difference(last_timestamp):
    last_time = datetime.fromisoformat(last_timestamp)
    current_time = datetime.now()

    logging.info(f"마지막 타임스탬프: {last_time}")
    logging.info(f"현재 시간: {current_time}")

    time_difference = current_time - last_time

    if time_difference > timedelta(minutes=5):
        raise ValueError(f"마지막 타임스탬프가 현재 시간보다 5분 이상 지났습니다. 시간 차이: {time_difference}")