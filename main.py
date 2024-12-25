import os
import time
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from selenium_utils.selenium_settings import init_driver
from selenium_utils.actions import click_download_button
from services import calculate_order_amount, check_safe_download, delete_csv_files, get_last_row_data, send_trade_email
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


@app.get('/test-csv')
def test_csv():
    csv_file_path = check_safe_download()
    last_row_data = get_last_row_data(csv_file_path)
    logger.info(f"side 타입: {last_row_data['decision']}")
    return {"message": "CSV 파일 읽기 완료", "last_row_data": last_row_data}


@app.get("/download-csv")
def download_csv():
    try:
        driver = None
        delete_csv_files()
        driver = init_driver()
        url = 'http://3.35.214.209:8501/'
        driver.get(url)

        csv_file_path = click_download_button(driver)
        return {"message": "Success", "csv_file_path": csv_file_path}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if driver:
            driver.quit()


@app.get('/order')
def order_btc():
    csv_file_path = check_safe_download()
# def order_btc(payload: dict):
#     csv_file_path = payload['csv_file_path']
    # if not csv_file_path:
    #     csv_file_path = check_safe_download()
    last_row_data = get_last_row_data(csv_file_path)
    decision = last_row_data['decision']
    percentage = float(last_row_data['percentage']) / 100

    if decision == 'hold':
        return {"message": "투자 방향이 'hold'입니다. 투자하지 않습니다."}

    accounts = get_accounts()
    logger.info(f"accounts?????: {accounts}")
    order_amount = calculate_order_amount(decision, percentage, accounts)
    # result = post_order(decision, order_amount)
    # send_trade_email(last_row_data)

    return accounts


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)