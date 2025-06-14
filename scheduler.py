from apscheduler.schedulers.background import BackgroundScheduler
import requests
from constants import SERVER_URL
from utils.logger_config import logger


def start_scheduler():
    scheduler = BackgroundScheduler(timezone='Asia/Seoul')
    # scheduler.add_job(
    #     auto_crypto,
    #     'cron',
    #     hour='0,4,8,12,16,20',
    #     minute='3',
    #     id='upbit_job'
    # )
    scheduler.add_job(
        check_attendance,
        'cron',
        hour='5',
        id='zzz_attendance_check_job'
    )
    scheduler.add_job(
        prevent_sleep,
        'interval',
        minutes=5,
        id='prevent_sleep_job'
    )
    scheduler.start()
    logger.info("스케줄러 시작됨")
    return scheduler


def auto_crypto():
    try:
        logger.info("스케줄 작업 실행: Upbit API 호출")
        # result = requests.get(f"http://121.163.246.222:10000/download-csv")
        # requests.post(f"http://121.163.246.222:10000/order", json={"csv_file_path": result.json()['csv_file_path']})
        result = requests.get(f"{SERVER_URL}/download-csv")
        requests.post(f"{SERVER_URL}/order",
                      json={"csv_file_path": result.json()['csv_file_path']})
        logger.info(f"스케줄 작업 실행 완료: Upbit API 호출")
    except Exception as e:
        logger.error(f"스케줄된 작업 실행 중 오류 발생: {str(e)}")


def check_attendance():
    try:
        logger.info("스케줄 작업 실행: ZZZ 출석 체크 API 호출")
        requests.get(f"{SERVER_URL}/check-attendance")
        logger.info(f"스케줄 작업 실행 완료: ZZZ 출석 체크 API 호출")
    except Exception as e:
        logger.error(f"스케줄된 작업 실행 중 오류 발생: {str(e)}")


def prevent_sleep():
    requests.get(f"{SERVER_URL}/knock-knock")
