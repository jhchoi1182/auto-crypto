from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import os
import random


def init_driver():
    user_agent = generate_random_user_agent()

    # 프로젝트 경로 설정
    project_path = os.path.dirname(os.path.realpath(__file__))
    downloads_path = os.path.join(project_path, "downloads")

    # downloads 디렉토리가 없으면 생성
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)

    # 드라이버 설정
    options = Options()
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--remote-debugging-port=9222")  # 디버깅 포트 추가

    # 다운로드 경로 설정
    prefs = {
        "download.default_directory": downloads_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver: WebDriver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # 페이지 로드 타임아웃 설정
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)

    return driver


def generate_random_user_agent():
    browsers = ["Chrome", "Firefox", "Safari", "Edge"]
    os_list = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 6.1; WOW64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64"
    ]

    browser = random.choice(browsers)
    operating_system = random.choice(os_list)

    if browser == "Chrome":
        versions = [
            "114.0.5735.198", "114.0.5735.199", "115.0.5790.170", "115.0.5790.171"
        ]
        version = random.choice(versions)
        user_agent = f"Mozilla/5.0 ({operating_system}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
    elif browser == "Firefox":
        versions = [
            "114.0", "115.0", "116.0"
        ]
        version = random.choice(versions)
        user_agent = f"Mozilla/5.0 ({operating_system}; rv:{version}) Gecko/20100101 Firefox/{version}"
    elif browser == "Safari":
        versions = [
            "16.5.2", "16.6.0", "16.6.1"
        ]
        version = random.choice(versions)
        user_agent = f"Mozilla/5.0 ({operating_system}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
    elif browser == "Edge":
        versions = [
            "115.0.1901.183", "115.0.1901.188", "116.0.1938.69"
        ]
        version = random.choice(versions)
        user_agent = f"Mozilla/5.0 ({operating_system}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"

    return user_agent
