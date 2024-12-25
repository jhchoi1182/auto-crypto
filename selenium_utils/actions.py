from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException


def click_download_button(driver: WebDriver) -> None:
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
    except TimeoutException:
        raise RuntimeError("다운로드 버튼을 찾을 수 없습니다.")
    except ElementClickInterceptedException:
        raise RuntimeError("다운로드 버튼을 클릭할 수 없습니다. 다른 요소에 가려져 있을 수 있습니다.")
    except Exception as e:
        raise RuntimeError(f"다운로드 버튼 클릭 중 오류가 발생했습니다: {str(e)}")