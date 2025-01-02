from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

import os
import random

from constants import DOWNLOADS_DIR


def init_driver():
    user_agent = generate_random_user_agent()

    # downloads 디렉토리가 없으면 생성
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    # 드라이버 설정
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--remote-debugging-port=9222")

    # Render 환경에서 Chrome 바이너리 경로 설정
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        options.binary_location = chrome_bin

    # 다운로드 경로 설정
    prefs = {
        "download.default_directory": DOWNLOADS_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # ChromeDriver 경로 설정
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
    service = Service(
        chromedriver_path if chromedriver_path else ChromeDriverManager().install())

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


def set_zzz_cokies(driver: WebDriver):
    driver.get('https://act.hoyolab.com')

    cookies = {
        'mi18nLang': 'ko-kr',
        '_HYVUUID': 'b3e86cc8-7894-4950-99a7-906effde184c',
        '_MHYUUID': 'f7a2d69f-1531-453b-ab31-12444f4085e5',
        'DEVICEFP_SEED_ID': '727b5baddb6d043a',
        'DEVICEFP_SEED_TIME': '1735736692670',
        'DEVICEFP': '38d7f45b37a8d',
        '_gid': 'GA1.2.627536408.1735736693',
        'ltoken_v2': 'v2_CAISDGNpZWF6NGVwZDV2axokYjNlODZjYzgtNzg5NC00OTUwLTk5YTctOTA2ZWZmZGUxODRjIPr61LsGKKG9t9YCMPCG18MBQgpuYXBfZ2xvYmFs.ej11ZwAAAAAB.MEQCID5NRt3eCHKWRmMj0HaAhSU6OG6Kn8RwNbmvNb5HQpNuAiBWoa5X9XOOxB_12dlQxDOoFetFkcimg3G6lmBnVhOjaA',
        'ltmid_v2': '114ve4xajt_hy',
        'ltuid_v2': '410370928',
        'HYV_LOGIN_PLATFORM_OPTIONAL_AGREEMENT': '{"content":[]}',
        'HYV_LOGIN_PLATFORM_LOAD_TIMEOUT': '{}',
        'HYV_LOGIN_PLATFORM_TRACKING_MAP': '{"sourceValue":"870"}',
        '_gat_gtag_UA_206868027_31': '1',
        'HYV_LOGIN_PLATFORM_LIFECYCLE_ID': '{"value":"5cde244c-48b6-4a28-98b7-655d4998a136"}',
        '_ga_Y5SZ86WZQH': 'GS1.1.1735801053.3.1.1735802725.0.0.0',
        '_ga_SBYZMHZRMJ': 'GS1.1.1735801053.3.1.1735802725.0.0.0',
        '_ga': 'GA1.2.363217342.1735736693'
    }

    for name, value in cookies.items():
        driver.add_cookie({
            'name': name,
            'value': value,
            'domain': '.hoyolab.com'
        })
