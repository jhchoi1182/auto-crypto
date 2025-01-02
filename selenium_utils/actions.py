from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from utils.logger_config import logger

from services import check_safe_download


def click_download_csv_button(driver: WebDriver) -> None:
    try:
        scroller = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.dvn-scroller.stDataFrameGlideDataEditor"))
        )
    except TimeoutException:
        raise RuntimeError("데이터 스크롤러를 찾을 수 없습니다. 페이지가 올바르게 로드되었는지 확인해주세요.")

    try:
        actions = ActionChains(driver)
        actions.move_to_element(scroller)
        actions.perform()
    except Exception:
        raise RuntimeError("스크롤러에 마우스 호버를 할 수 없습니다.")

    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='stBaseButton-elementToolbar']"))
        )
        button.click()
        csv_file_path = check_safe_download()
        logger.info(f"다운로드 버튼 클릭 완료: {csv_file_path}")
        return csv_file_path
    except TimeoutException:
        raise RuntimeError("다운로드 버튼을 찾을 수 없습니다.")
    except ElementClickInterceptedException:
        raise RuntimeError("다운로드 버튼을 클릭할 수 없습니다. 다른 요소에 가려져 있을 수 있습니다.")
    except Exception as e:
        raise RuntimeError(f"다운로드 버튼 클릭 중 오류가 발생했습니다: {str(e)}")


def click_dialog_close_button(driver: WebDriver) -> None:
    try:
        dialog_close = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "components-pc-assets-__dialog_---dialog-close---3G9gO2"))
        )
        dialog_close.click()
        logger.info("다이얼로그 닫기 버튼 클릭 성공")
    except (TimeoutException, NoSuchElementException):
        logger.info("다이얼로그 닫기 버튼을 찾는 데 실패했습니다.")


def click_today_attendance_check_button(driver: WebDriver) -> None:
    try:
        target_image_url = "https://act-webstatic.hoyoverse.com/event-static/2024/06/17/3b211daae47bbfac6bed5b447374a325_3353871917298254056.png"
        css_selector = f".components-pc-assets-__prize-list_---item---F852VZ[style*='{target_image_url}']"

        prize_item = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
        )
        prize_item.click()
        logger.info("오늘 출석 체크 아이템 클릭 성공")
    except (TimeoutException, NoSuchElementException) as e:
        logger.error(f"오늘 출석 체크 아이템 클릭 중 오류: {str(e)}")
        raise
