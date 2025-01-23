import os
import time
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium_utils.selenium_settings import init_driver, set_zzz_cokies
from selenium_utils.actions import click_dialog_close_button, click_download_csv_button, click_today_attendance_check_button
from services import calculate_order_amount, check_safe_download, delete_csv_files, get_last_row_data, send_emergency_email, send_trade_email
from upbit.apis import get_accounts, post_order
from utils.logger_config import logger
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    scheduler = start_scheduler()
    yield
    # 종료 시
    scheduler.shutdown()
    logger.info("스케줄러 종료됨")


app = FastAPI(lifespan=lifespan)
# app = FastAPI()


@app.get('/hello')
def test_csv():
    return {"message": "서버 구동 중..."}


@app.get("/download-csv")
def download_csv():
    try:
        delete_csv_files()
        driver = init_driver()
        url = 'http://3.35.214.209:8501/'
        driver.get(url)

        csv_file_path = click_download_csv_button(driver)
        return {"message": "Success", "csv_file_path": csv_file_path}
    except Exception as e:
        send_emergency_email(e)
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()


@app.post('/order')
def order_btc(payload: dict):
    try:
        csv_file_path = payload['csv_file_path']
        if not csv_file_path:
            csv_file_path = check_safe_download()
        last_row_data = get_last_row_data(csv_file_path)
        decision = last_row_data['decision']
        percentage = float(last_row_data['percentage']) / 100

        if decision == 'hold':
            return send_trade_email(last_row_data)

        accounts = get_accounts()
        order_amount = calculate_order_amount(decision, percentage, accounts)
        result = post_order(decision, order_amount)
        send_trade_email(last_row_data, result)

        return result
    except Exception as e:
        send_emergency_email(e)
        return {"error": str(e)}


@app.get('/check-attendance')
def check_attendance():
    try:
        driver = init_driver()
        set_zzz_cokies(driver)
        url = 'https://act.hoyolab.com/bbs/event/signin/zzz/e202406031448091.html?act_id=e202406031448091'
        driver.get(url)

        click_dialog_close_button(driver)
        time.sleep(3)
        click_today_attendance_check_button(driver)

        driver.quit()
        return {"message": "출석 체크 완료"}

    except Exception as e:
        logger.error(f"ZZZ 출첵 스케줄 중 오류: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return {"error": str(e)}


@app.get("/knock-knock")
def knock_knock():
    try:
        return {"message": "Success"}
    except Exception as e:
        send_emergency_email(e)
        return {"error": str(e)}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
