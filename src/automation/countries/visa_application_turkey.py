import time
import os, sys

from loguru import logger
from tenacity import retry, wait_fixed, stop_after_attempt
from datetime import datetime as dt
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from imap_tools import AND, MailBox, MailMessage, MailMessageFlags
from parsel import Selector

from src.automation.countries.visa_application_base import VisaApplicantionBase


class VisaApplicantionTurkey(VisaApplicantionBase):
    def __init__(self, session_id: str, kwargs: dict):
        super().__init__(session_id, kwargs)
        self.url = "https://www.evisa.gov.tr/en/apply/"
        self.submitted = None
        # Country/Region
        self.country_region = kwargs.get("country_region", "")
        self.travel_document = "Ordinary Passport"

        # Date of Arrival
        self.arrival_date = kwargs.get("arrival_date", "")

        # Personal Information
        self.place_of_birth = kwargs.get("place_of_birth", "")
        self.phone_number = kwargs.get("phone_number", "")
        self.address = kwargs.get("address", "")

        # fill_payment_form
        self.card_number = kwargs.get("card_number", "")
        self.card_cvv = kwargs.get("card_cvv", "")
        self.card_expiration_month = kwargs.get("card_expiration_month", "")
        self.card_expiration_year = kwargs.get("card_expiration_year", "")

    def step_country_region(self):
        self.driver.get(self.url)

        el = self.driver.find_element(By.NAME, "ctl00$body$uyruklist_input")
        el.clear()
        el.send_keys(self.country_region.upper())
        el.send_keys(Keys.TAB)

        el = Select(self.driver.find_element(By.ID, "belgelist"))
        el.select_by_visible_text(self.travel_document)

        el = self.driver.find_element(By.ID, "captcha_image")
        image_base64 = el.screenshot_as_base64
        solved_captcha = self.solve_normal_captcha(image_base64)

        el = self.driver.find_element(By.ID, "recaptcha_response_field")
        el.send_keys(solved_captcha["code"])

        el = self.driver.find_element(By.ID, "btnsubmit")
        el.click()

        try:
            # try to check element from next step
            el = self.driver.find_element(By.ID, "txtGelisTarihi")
            self.report_captcha_result(solved_captcha, True)
        except:
            try:
                # if it couldn't be found, check if the captcha was invalid
                el = self.driver.find_element(By.CLASS_NAME, 'feedback_info')
                if 'Code is Invalid' in el.text:
                    self.report_captcha_result(solved_captcha, False)
                    raise Exception("Invalid captcha. Try again.")

                raise Exception("Could not proceed to step 2. Try again.")
            except Exception as ex:
                raise ex

        return ""

    def step_date_of_arrival(self):
        el = self.driver.find_element(By.ID, "txtGelisTarihi")
        time.sleep(1)  # wait for element to be interactable
        for c in self.arrival_date:
            time.sleep(0.1)
            el.send_keys(Keys.BACK_SPACE)
        el.send_keys(self.arrival_date)
        el.send_keys(Keys.TAB)

        time.sleep(1)  # wait for calendar to process the new date

        el = self.driver.find_element(By.ID, "btnSubmit")
        el.click()

    def step_personal_information(self):
        el = self.driver.find_element(By.ID, "txtAd")
        el.send_keys(self.given_name)

        el = self.driver.find_element(By.ID, "txtSoyad")
        el.send_keys(self.surname)

        el = self.driver.find_element(By.ID, "txtDogumTarihi")
        el.send_keys(self.date_of_birth)
        el.send_keys(Keys.TAB)
        time.sleep(1)  # wait for calendar to process the new date

        el = self.driver.find_element(By.ID, "txtDogumYeri")
        el.send_keys(self.place_of_birth)

        el = self.driver.find_element(By.ID, "txtPasaportNo")
        el.send_keys(self.passport_number)

        el = self.driver.find_element(By.ID, "txtPasaportVerTarih")
        el.send_keys(self.passport_date_issue)
        el.send_keys(Keys.TAB)
        time.sleep(1)  # wait for calendar to process the new date

        el = self.driver.find_element(By.ID, "txtPasaportGecTarih")
        el.send_keys(self.passport_date_expiry)
        el.send_keys(Keys.TAB)
        time.sleep(1)  # wait for calendar to process the new date

        el = self.driver.find_element(By.ID, "txtEmail")
        el.send_keys(self.email)
        self.submitted = dt.now()

        el = self.driver.find_element(By.ID, "txtTel")
        el.send_keys(self.phone_number)

        el = self.driver.find_element(By.ID, "txtadres")
        el.send_keys(self.address)

        el = self.driver.find_element(By.ID, "onamcheck")
        el.click()
        time.sleep(2)

        el = self.driver.find_element(By.ID, "cboxClose")
        el.click()
        time.sleep(2)

        el = self.driver.find_element(By.ID, "btnSubmit")
        el.click()

        # Confirm data
        el = self.driver.find_element(By.CSS_SELECTOR, ".form_submit .btn_green")
        el.click()

    def step_confirmation(self):
        el = self.driver.find_element(By.ID, "detailed_info_text")

        if 'successfully ' not in el.text:
            raise Exception('Successful message was not displayed at the last page')

    @retry(wait=wait_fixed(20), stop=stop_after_attempt(5))
    @logger.catch
    def get_payment_link_from_email(self):
        imap = 'outlook.office365.com'
        login = 'checkforms@outlook.com'
        passw = '@Visa1122'
        if self.submitted:
            with MailBox(imap).login(login, passw) as mailbox:
                for msg in mailbox.fetch(
                    AND(from_="noreply@evisa.gov.tr", subject="verification"),
                    limit=1,
                    reverse=True,
                    bulk=True,
                    mark_seen=False,
                ):
                    body = Selector(text=msg.html)
                    link = body.xpath('//a[contains(@href,"www.evisa.gov.tr/en/redirect")]/@href').get()
                    refid = body.xpath('//h1[contains(text(),"REF:")]/text()').get()
                    logger.debug(refid)
                    logger.critical(f'{link=}')
            time.sleep(5)
            self.driver.get(link)
            self.refid = refid.rsplit('REF: ', 1)[1]

    def x(self, locator: str, timeout: int = 30) -> WebElement:
        """useful for locating element by xpath with timeout,
        thus letting the element load for some time"""
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))

    def fill_payment_form(self):
        ccn = self.x('//input[@type="text"][@id="txtcn"]')
        ccn.click()
        ccn.send_keys(self.card_number)

        cvv = self.x('//input[@type="text"][@id="txtcvv"]')
        cvv.click()
        cvv.send_keys(self.card_cvv)

        expiry = self.x('//input[@id="sktpicker"]')
        self.driver.execute_script('arguments[0].removeAttribute("readonly")', expiry)
        expiry_formatted = f'{int(self.card_expiration_month):02d} / {int(self.card_expiration_year[2:]):02d}'
        expiry.send_keys(expiry_formatted)

        submit = self.x('//input[@type="button"][@id="btnsubmit"]')
        submit.click()
        time.sleep(15)

    def submit_visa(self):

        try:
            self.step_country_region()
            self.step_date_of_arrival()
            self.step_personal_information()
            self.step_confirmation()
            self.submitted = dt.now()
            sleep(60)
            self.get_payment_link_from_email()
            self.fill_payment_form()
            logger.critical(self.refid)
            if self.refid:
                return self.refid
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            formatted_exception_info = f'Info: {str(e)}\nType: {exc_type}\nFile: {fname}\nLine: {exc_tb.tb_lineno}'
            logger.debug(formatted_exception_info)
            return formatted_exception_info
