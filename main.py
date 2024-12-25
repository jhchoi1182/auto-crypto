import time
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI

from selenium_utils.selenium_settings import init_driver
from selenium_utils.actions import click_download_button
from utils.utils import translate_text_to_korean
from utils.logger_config import logger

app = FastAPI()


@app.get('/test-csv')
def test_csv():
    _, csv_file_path = check_safe_download()
    last_row_data = get_last_row_data(csv_file_path)
    logger.info(f"번역된 이유: {translate_text_to_korean(last_row_data['reason'])}")
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
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
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

    check_time_difference(last_timestamp)

    logger.info(f"마지막 행 정보:")
    logger.info(f"Decision: {last_decision}")
    logger.info(f"Percentage: {last_percentage}")
    logger.info(f"Timestamp: {last_timestamp}")
    logger.info(f"Reason: {last_reason}")
    logger.info(f"Reflection: {last_reflection}")

    return {
        "decision": last_decision,
        "percentage": last_percentage,
        "timestamp": last_timestamp,
        "reason": last_reason,
        "reflection": last_reflection
    }


def check_time_difference(last_timestamp):
    last_time = datetime.fromisoformat(last_timestamp)
    
    # 현재 시간을 UTC로 가져온 후 한국 시간(+9시간)으로 변환
    current_time = datetime.now(timezone.utc) + timedelta(hours=9)

    logger.info(f"마지막 타임스탬프: {last_time}")
    logger.info(f"현재 시간: {current_time}")

    time_difference = current_time - last_time

    if time_difference > timedelta(minutes=5):
        raise ValueError(f"마지막 타임스탬프가 현재 시간보다 5분 이상 지났습니다. 시간 차이: {time_difference}")