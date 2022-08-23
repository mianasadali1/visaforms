import base64
import time
import traceback
from typing import List

from loguru import logger
from selenium import webdriver
from twocaptcha import (
    ApiException,
    NetworkException,
    TimeoutException,
    TwoCaptcha,
    ValidationException,
)
from base64 import b64decode
import tempfile
import os
from datauri import DataURI

API_KEY_SCRAPER_API = ""
API_KEY_TWOCAPTCHA = "99b388343cd217abbaf679e9f2508c1e"


class VisaApplicantionBase:
    def __init__(self, session_id: str, kwargs: dict):
        self.driver = None
        self.captcha_solver = TwoCaptcha(API_KEY_TWOCAPTCHA)

        self.given_name = kwargs.get("given_name", "")
        self.surname = kwargs.get("surname", "")
        self.date_of_birth = kwargs.get("date_of_birth", "")
        self.email = kwargs.get("email", "")

        self.passport_number = kwargs.get("passport_number", "")
        self.passport_place_issue = kwargs.get("passport_place_issue", "")
        self.passport_date_issue = kwargs.get("passport_date_issue", "")
        self.passport_date_expiry = kwargs.get("passport_date_expiry", "")
        self.session_id = session_id

    def init_driver(self) -> webdriver.Remote:
        logger.debug("Initializing driver")

        if self.driver:
            return

        capabilities_chrome = {
            "browserName": "chrome",
            "goog:chromeOptions": {
                "args": [],
                "prefs": {
                    "download.prompt_for_download": False,
                    "plugins.always_open_pdf_externally": True,
                    "safebrowsing_for_trusted_sources_enabled": False,
                },
            },
        }

        # proxy_options = {
        #     'addr': 'visaaplcation_automation-automation-1',
        #     "proxy": {
        #         "http": f"http://scraperapi.session_number={self.session_id}:{API_KEY_SCRAPER_API}@proxy-server.scraperapi.com:8001",
        #         "no_proxy": "localhost,127.0.0.1",
        #     }
        # }

        driver = webdriver.Remote(
            command_executor="http://selenium-hub:4444",
            desired_capabilities=capabilities_chrome,
            # seleniumwire_options=proxy_options,
        )
        driver.implicitly_wait(10)

        self.driver = driver

    def __del__(self):
        logger.debug("Quitting driver")

        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def solve_normal_captcha(self, image_base64: str):
        result = ""

        for attempt in range(3):
            logger.debug(f"Solving captcha attempt {attempt}...")
            try:
                result = self.captcha_solver.normal(image_base64)
            except ValidationException as ex:
                logger.error("Invalid parameters passed: {ex}")
            except NetworkException as ex:
                logger.error("Network error occurred: {ex}")
            except ApiException as ex:
                logger.error("Api respond with error: {ex}")
            except TimeoutException as ex:
                logger.error("Captcha is not solved so far: {ex}")

            if result:
                break

        # Format {'captchaId': '69486729673', 'code': 'zuqfu'}
        logger.debug(f'Captcha result: "{result}"')

        return result

    def report_captcha_result(self, solved_captcha: dict, success: bool):
        # https://github.com/2captcha/2captcha-python

        try:
            if success:
                self.captcha_solver.report(solved_captcha["captchaId"], True)
                logger.debug(f"Captcha solved successfully: {solved_captcha}")
            else:
                logger.error(f"Invalid captcha: {solved_captcha}")
                self.captcha_solver.report(solved_captcha["captchaId"], False)
        except Exception as ex:
            logger.warning(f"Error reporting captcha. Will continue. Exception: {traceback.format_exc()}")

    def wait_file_download(self, timeout=10.0, poll_interval=0.5):
        end_time = time.time() + timeout
        condition = lambda: len(self.get_downloaded_files()) > 0
        status = condition()
        while not status and time.time() < end_time:
            time.sleep(poll_interval)
            status = condition()
        return status

    def get_downloaded_files(self) -> List[str]:
        if not self.driver.current_url.startswith("chrome://downloads"):
            self.driver.get("chrome://downloads/")

        return self.driver.execute_script(
            "return  document.querySelector('downloads-manager')  "
            " .shadowRoot.querySelector('#downloadsList')         "
            " .items.filter(e => e.state === 'COMPLETE')          "
            " .map(e => e.filePath || e.file_path || e.fileUrl || e.file_url); "
        )

    def get_file_content(self, path):
        el = self.driver.execute_script(
            "var input = window.document.createElement('INPUT'); "
            "input.setAttribute('type', 'file'); "
            "input.hidden = true; "
            "input.onchange = function (e) { e.stopPropagation() }; "
            "return window.document.documentElement.appendChild(input); "
        )
        el._execute("sendKeysToElement", {"value": [path], "text": path})
        base64_file_content_str = self.driver.execute_async_script(
            "var input = arguments[0], callback = arguments[1]; "
            "var reader = new FileReader(); "
            "reader.onload = function (ev) { callback(reader.result) }; "
            "reader.onerror = function (ex) { callback(ex.message) }; "
            "reader.readAsDataURL(input.files[0]); "
            "input.remove(); ",
            el,
        )
        if not base64_file_content_str.startswith("data:"):
            raise Exception(f"Failed to get file content: {base64_file_content_str}")

        data_uri_from_file = DataURI(base64_file_content_str)
        return data_uri_from_file.data
    
    def __data_uri_get_file_extension(self, data_uri: DataURI):
        # https://en.wikipedia.org/wiki/Data_URI_scheme
        # data:[<media type>][;base64],<data>
        # "data:image/jpeg;base64,/9j/4AAQS..."
        return data_uri.mimetype.split('/')[1]

    def create_temp_file_from_data_uri_str(self, data_uri_str: str):
        IS_DEBUG = os.environ.get('VISAAPPLICATION_DEBUG', '0') == '1'

        if IS_DEBUG:
            data_uri = DataURI.from_file(data_uri_str)
        else:
            data_uri = DataURI(data_uri_str)

        file_extension = '.' + self.__data_uri_get_file_extension(data_uri)

        namedTempFile = tempfile.NamedTemporaryFile(mode='w+b', suffix=file_extension)
        namedTempFile.write(data_uri.data)
        namedTempFile.flush()

        return namedTempFile

