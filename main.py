from typing import Union
import time
import os
import pandas as pd
import logging
import numpy as np

from fastapi import FastAPI
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from selenium_settings import init_driver

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


@app.get("/hi")
def read_root():
    driver = None
    try:
        driver = init_driver()
        url = 'http://3.35.214.209:8501/'
        driver.get(url)

        # 페이지가 로드될 때까지 기다림
        time.sleep(3)

        # 데이터프레임 스크롤러 찾기
        scroller = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.dvn-scroller.stDataFrameGlideDataEditor"))
        )

        # 스크롤러에 마우스 호버
        actions = ActionChains(driver)
        actions.move_to_element(scroller)
        actions.perform()

        time.sleep(1)  # 호버 후 잠시 대기

        # 버튼 찾아서 클릭
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='stBaseButton-elementToolbar']"))
        )
        button.click()

        # 다운로드 완료 대기
        downloads_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), "downloads")
        max_wait_time = 30  # 최대 30초 대기
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

        if download_complete and csv_file_path:
            # CSV 파일 읽기
            df = pd.read_csv(csv_file_path)

            # 마지막 행의 decision과 percentage 값 가져오기
            last_row = df.iloc[-1]
            last_decision = last_row['decision']
            last_percentage = float(last_row['percentage']) if isinstance(
                last_row['percentage'], np.number) else last_row['percentage']

            # 결과 로깅
            logging.info(f"마지막 행 정보:")
            logging.info(f"Decision: {last_decision}")
            logging.info(f"Percentage: {last_percentage}")

            return {
                "status": "success",
                "message": "File processed successfully",
                "last_row_data": {
                    "decision": str(last_decision),
                    "percentage": last_percentage
                }
            }
        else:
            return {
                "status": "error",
                "message": "Download timeout"
            }

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}
    finally:
        if driver:
            driver.quit()
