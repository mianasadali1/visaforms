import time
import re
import os, sys

from loguru import logger
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.automation.countries.visa_application_base import VisaApplicantionBase
from time import sleep
from random import uniform
import pyotp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

MFA_STRING = 'KRIEE4PQUDSYBDPRTKCRICLLP2UOBVWY'
PAYPAL_PASS = "get_your_paypal_pass_here"
PAYPAL_LOGIN = "denis@sharapenko.ca"


class VisaApplicantionIndia(VisaApplicantionBase):
    def __init__(self, session_id: str, kwargs: dict):
        super().__init__(session_id, kwargs)
        self.url = "https://indianvisaonline.gov.in/evisa/tvoa.html"

        self.passport_type = "ORDINARY PASSPORT"
        self.port_of_arrival = kwargs.get("port_of_arrival", "")
        self.expected_date_of_arrival = kwargs.get("expected_date_of_arrival", "")
        self.gender = kwargs.get("gender", "")
        self.nationality = kwargs.get("nationality", "")

        # step 2
        self.city_of_birth = kwargs.get("city_of_birth", "")
        self.country_of_birth = kwargs.get("country_of_birth", "")
        self.citizenship_national_id_no = "NA"
        self.religion = kwargs.get("religion", "")
        self.visible_identification_marks = "NA"
        self.educational_qualification = kwargs.get("educational_qualification", "")
        self.how_did_you_aquired_nationality = kwargs.get("how_did_you_aquired_nationality", "")
        self.have_you_lived_2_years = kwargs.get("have_you_lived_2_years", "")
        self.any_other_valid_passport = "No"

        # step 3
        self.present_house_number_and_street = kwargs.get("present_house_number_and_street", "")
        self.present_city = kwargs.get("present_city", "")
        self.present_country = kwargs.get("present_country", "")
        self.present_district = kwargs.get("present_district", "")
        self.present_zip_code = kwargs.get("present_zip_code", "")
        self.present_phone_number = kwargs.get("present_phone_number", "")
        # self.permanent_house_number_and_street = kwargs.get("permanent_house_number_and_street", "")
        # self.permanent_city = kwargs.get("permanent_city", "")
        # self.permanent_district = kwargs.get("permanent_district", "")
        self.father_name = kwargs.get("father_name", "")
        self.father_nationality = kwargs.get("father_nationality", "")
        self.father_place_of_birth = kwargs.get("father_place_of_birth", "")
        self.father_country = kwargs.get("father_country", "")
        self.mother_name = kwargs.get("mother_name", "")
        self.mother_nationality = kwargs.get("mother_nationality", "")
        self.mother_place_of_birth = kwargs.get("mother_place_of_birth", "")
        self.mother_country = kwargs.get("mother_country", "")
        self.applicant_marital_status = "SINGLE"
        self.are_parents_from_pakistan = kwargs.get("are_parents_from_pakistan", "")
        self.parents_from_pakistan_details = kwargs.get("parents_from_pakistan_details", "")
        self.profession_present_occupation = kwargs.get("profession_present_occupation", "")
        self.profession_employer_name = kwargs.get("profession_employer_name", "")
        self.profession_address = kwargs.get("profession_address", "")
        self.are_you_military = "NO"

        self.places_to_be_visited = kwargs.get("places_to_be_visited", "")
        self.expected_port_of_exit_from_india = kwargs.get("expected_port_of_exit_from_india", "")
        self.countries_visited_last_10_years = kwargs.get("countries_visited_last_10_years", "")
        self.reference_name_in_india = kwargs.get("reference_name_in_india", "")
        self.reference_address = kwargs.get("reference_address", "")
        self.reference_state = kwargs.get("reference_state", "")
        self.reference_district = kwargs.get("reference_district", "")
        self.reference_phone = kwargs.get("reference_phone", "")
        self.reference_phone_in_us = kwargs.get("reference_phone_in_us", "")
        self.reference_name_in_us = kwargs.get("reference_name_in_us", "")
        self.reference_address_in_us = kwargs.get("reference_address_in_us", "")

        self.user_photo_file_path = kwargs.get("user_photo_file_path", "")
        self.user_passport_file_path = kwargs.get("user_passport_file_path", "")

    def hide_calendar(self):
        # workaround to hide the calendar by clicking in the top banner
        header_el = self.driver.find_element(By.CSS_SELECTOR, ".pageHeader")
        header_el.click()

    def step_registration(self):
        self.driver.get(self.url)

        el = self.driver.find_element(By.CSS_SELECTOR, "a[href='Registration']")
        el.click()

        el = Select(self.driver.find_element(By.ID, "nationality_id"))
        el.select_by_visible_text(self.nationality.upper())

        el = Select(self.driver.find_element(By.ID, "ppt_type_id"))
        el.select_by_visible_text(self.passport_type.upper())

        el = Select(self.driver.find_element(By.ID, "missioncode_id"))
        el.select_by_visible_text(self.port_of_arrival.upper())

        el = self.driver.find_element(By.ID, "dob_id")
        el.send_keys(self.date_of_birth)
        self.hide_calendar()

        el = self.driver.find_element(By.ID, "email_id")
        el.send_keys(self.email)

        el = self.driver.find_element(By.ID, "email_re_id")
        el.send_keys(self.email)

        el = self.driver.find_element(By.ID, "visa_ser_id")
        if el.is_displayed():
            el.click()
            try:
                wait = WebDriverWait(self.driver, 2)
                wait.until(alert_is_present(), "Timed out waiting for alert to show")
                alert: Alert = self.driver.switch_to.alert
                alert.accept()
            except Exception as ex:
                # Timed out. Alert didn't show up?!
                pass

            el = self.driver.find_element(By.NAME, "evisa_purpose_31")
            el.click()

        self.scrollToEnd()

        el = self.driver.find_element(By.CSS_SELECTOR, "img[src='captcha']")
        image_base64 = el.screenshot_as_base64
        solved_captcha = self.solve_normal_captcha(image_base64)

        el = self.driver.find_element(By.ID, "captcha")
        el.send_keys(solved_captcha["code"])

        el = self.driver.find_element(By.ID, "read_instructions_check")
        el.click()

        self.driver.execute_script('document.getElementById("jouryney_id").removeAttribute("readonly")')
        el = self.driver.find_element(By.ID, "jouryney_id")
        el.send_keys(self.expected_date_of_arrival)
        self.hide_calendar()

        el = self.driver.find_element(By.CSS_SELECTOR, "input[value='Continue']")
        el.click()

        # there are two elements. The first one is invisible. Get the second one
        el = self.driver.find_elements(By.CSS_SELECTOR, ".ui-dialog-buttonset button")[1]
        el.click()

        try:
            # try to check element from next step
            el = self.driver.find_element(By.ID, "surname")
            self.report_captcha_result(solved_captcha, True)
        except:
            try:
                # if it couldn't be found, check if the captcha was invalid
                el = self.driver.find_element_by_xpath("//*[contains(text(), 'Invalid Captcha')]")
                self.report_captcha_result(solved_captcha, False)
            except:
                raise "Could not proceed to step 2"

        return ""

    def step_basic_details(self):
        el = self.driver.find_element(By.ID, "surname")
        el.send_keys(self.surname)

        el = self.driver.find_element(By.ID, "givenName")
        el.send_keys(self.given_name)

        el = Select(self.driver.find_element(By.ID, "gender"))
        el.select_by_visible_text(self.gender.upper())

        el = self.driver.find_element(By.ID, "birth_place")
        el.send_keys(self.city_of_birth)

        el = Select(self.driver.find_element(By.ID, "country_birth"))
        el.select_by_visible_text(self.country_of_birth.upper())

        el = self.driver.find_element(By.ID, "nic_number")
        el.send_keys(self.citizenship_national_id_no)

        el = Select(self.driver.find_element(By.ID, "religion"))
        el.select_by_visible_text(self.religion.upper())

        el = self.driver.find_element(By.ID, "identity_marks")
        el.send_keys(self.visible_identification_marks)

        el = Select(self.driver.find_element(By.ID, "education"))
        el.select_by_visible_text(self.educational_qualification.upper())

        el = Select(self.driver.find_element(By.ID, "nationality_by"))
        el.select_by_visible_text(self.how_did_you_aquired_nationality)

        if self.have_you_lived_2_years.upper() == "NO":
            el = self.driver.find_element(By.ID, "refer_flag2")
        else:
            el = self.driver.find_element(By.ID, "refer_flag1")
        el.click()

        el = self.driver.find_element(By.ID, "passport_no")
        el.send_keys(self.passport_number)

        el = self.driver.find_element(By.ID, "passport_issue_place")
        el.send_keys(self.passport_place_issue)

        el = self.driver.find_element(By.ID, "passport_issue_date")
        el.send_keys(self.passport_date_issue)
        self.hide_calendar()

        el = self.driver.find_element(By.ID, "passport_expiry_date")
        el.send_keys(self.passport_date_expiry)
        self.hide_calendar()

        el = self.driver.find_element(By.ID, "other_ppt_2")
        el.click()

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def step_family_details_step(self):
        el = self.driver.find_element(By.ID, "pres_add1")
        el.send_keys(self.present_house_number_and_street)

        el = self.driver.find_element(By.ID, "pres_add2")
        el.send_keys(self.present_city)

        el = Select(self.driver.find_element(By.ID, "pres_country"))
        el.select_by_visible_text(self.present_country.upper())

        el = self.driver.find_element(By.ID, "pres_add3")
        el.send_keys(self.present_district)

        el = self.driver.find_element(By.ID, "pincode")
        el.send_keys(self.present_zip_code)

        el = self.driver.find_element(By.ID, "pres_phone")
        el.send_keys(self.present_phone_number)

        el = self.driver.find_element(By.ID, "sameAddress_id")
        el.click()  # this will fill the permanent address with same values

        # el = self.driver.find_element(By.ID, "perm_address1")
        # el.send_keys(self.permanent_house_number_and_street)

        # el = self.driver.find_element(By.ID, "perm_address2")
        # el.send_keys(self.permanent_city)

        # el = self.driver.find_element(By.ID, "")
        # el.send_keys(self.permanent_district)

        el = self.driver.find_element(By.ID, "fthrname")
        el.send_keys(self.father_name)

        el = Select(self.driver.find_element(By.ID, "father_nationality"))
        el.select_by_visible_text(self.father_nationality.upper())

        el = self.driver.find_element(By.ID, "father_place_of_birth")
        el.send_keys(self.father_place_of_birth)

        el = Select(self.driver.find_element(By.ID, "father_country_of_birth"))
        el.select_by_visible_text(self.father_country.upper())

        el = self.driver.find_element(By.ID, "mother_name")
        el.send_keys(self.mother_name)

        el = Select(self.driver.find_element(By.ID, "mother_nationality"))
        el.select_by_visible_text(self.mother_nationality.upper())

        el = self.driver.find_element(By.ID, "mother_place_of_birth")
        el.send_keys(self.mother_place_of_birth)

        el = Select(self.driver.find_element(By.ID, "mother_country_of_birth"))
        el.select_by_visible_text(self.mother_country.upper())

        el = Select(self.driver.find_element(By.ID, "marital_status"))
        el.select_by_visible_text(self.applicant_marital_status.upper())

        if self.are_parents_from_pakistan.upper() == "NO":
            el = self.driver.find_element(By.ID, "grandparent_flag2")
            el.click()
        else:
            el = self.driver.find_element(By.ID, "grandparent_flag1")
            el.click()

            el = self.driver.find_element(By.ID, "grandparent_details")
            el.send_keys(self.parents_from_pakistan_details)

        el = Select(self.driver.find_element(By.ID, "occupation"))
        el.select_by_visible_text(self.profession_present_occupation.upper())

        el = self.driver.find_element(By.ID, "empname")
        el.send_keys(self.profession_employer_name)

        el = self.driver.find_element(By.ID, "empaddress")
        el.send_keys(self.profession_address)

        el = self.driver.find_element(By.ID, "prev_org2")
        el.click()  # are you Military? No.

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def step_visa_details_step(self):
        el = self.driver.find_element(By.NAME, "appl.placesToBeVisited1")
        el.send_keys(self.places_to_be_visited)

        # workaround to make it work and select 'no'
        el = self.driver.find_element(By.ID, "haveYouBookedRoomInHotel_yes_id")
        el.click()
        el = self.driver.find_element(By.ID, "haveYouBookedRoomInHotel_no_id")
        el.click()

        el = Select(self.driver.find_element(By.ID, "exitpoint"))
        el.select_by_visible_text(self.expected_port_of_exit_from_india.upper())

        el = self.driver.find_element(By.ID, "old_visa_flag2")  # Have you ever visited India before?
        el.click()

        el = self.driver.find_element(
            By.ID, "refuse_flag2"
        )  # Has permission to visit or to extend stay in India previously been refused?
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, ".chosen-search-input")
        for country in self.countries_visited_last_10_years:
            el.send_keys(country.upper())
            el.send_keys(Keys.RETURN)

        el = self.driver.find_element(
            By.ID, "saarc_flag2"
        )  # Have you visited SAARC countries (except your own country) during last 3 years?
        el.click()

        el = self.driver.find_element(By.ID, "nameofsponsor_ind")
        el.send_keys(self.reference_name_in_india)

        el = self.driver.find_element(By.ID, "add1ofsponsor_ind")
        el.send_keys(self.reference_address)

        el = Select(self.driver.find_element(By.ID, "stateofsponsor_ind"))
        el.select_by_visible_text(self.reference_state.upper())

        time.sleep(0.5)  # wait for transitions to happen after selecting previous dropdown

        el = Select(self.driver.find_element(By.ID, "districtofsponsor_ind"))
        el.select_by_visible_text(self.reference_district.upper())

        el = self.driver.find_element(By.ID, "phoneofsponsor_ind")
        el.send_keys(self.reference_phone)

        el = self.driver.find_element(By.ID, "nameofsponsor_msn")
        el.send_keys(self.reference_name_in_us)

        el = self.driver.find_element(By.ID, "add1ofsponsor_msn")
        el.send_keys(self.reference_address_in_us)

        el = self.driver.find_element(By.ID, "phoneofsponsor_msn")
        el.send_keys(self.reference_phone_in_us)

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def step_additional_questions(self):
        el = self.driver.find_element(By.ID, "question_no_1")
        el.click()
        el = self.driver.find_element(By.ID, "question_no_2")
        el.click()
        el = self.driver.find_element(By.ID, "question_no_3")
        el.click()
        el = self.driver.find_element(By.ID, "question_no_4")
        el.click()
        el = self.driver.find_element(By.ID, "question_no_5")
        el.click()
        el = self.driver.find_element(By.ID, "question_no_6")
        el.click()
        el = self.driver.find_element(By.ID, "verifyQuestions")
        el.click()

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def step_photo_upload(self):

        with self.create_temp_file_from_data_uri_str(self.user_photo_file_path) as f:
            el = self.driver.find_element(By.ID, "image_error_id")
            el.send_keys(f.name)

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def step_crop_photo(self):
        el = self.driver.find_element(By.CSS_SELECTOR, "input[name='submit_btn']")
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, "input[name='submit_btn'][value='Save and Continue']")
        el.click()

    def step_document_upload_step(self):

        with self.create_temp_file_from_data_uri_str(self.user_passport_file_path) as f:
            el = self.driver.find_element(By.ID, "mFile_1")
            el.send_keys(f.name)

        el = self.driver.find_element(By.CSS_SELECTOR, "input[name='submit_btn'][value='Upload Document']")
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, ".text_uploaded_class")  # just to see if the status 'Uploaded' showd up

        el = self.driver.find_element(By.ID, "verifyDoc")
        el.click()

        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def verification(self):
        el = self.driver.find_element(By.ID, "continue")
        el.click()

    def x(self, locator: str, timeout: int = 30) -> WebElement:
        """useful for locating element by xpath with timeout,
        thus letting the element load for some time"""
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))

    def scrollToEnd(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    def fee_payment(self):
        # close alert
        popup = self.driver.switch_to.alert

        pattern = r'application\s+id:\s\"([\d\w]+)\"'
        r = re.findall(pattern, popup.text, re.IGNORECASE)
        self.refid = r[0] if r else "couldn't grab appId"
        logger.critical(self.refid)
        popup.accept()

        el = self.driver.find_element(By.XPATH, '//input[@type="radio"][@name="confirm"][@value="Y"]')
        el.click()

        el = self.driver.find_element(By.ID, "paynow_btn")
        el.click()

        self.scrollToEnd()

        el = self.driver.find_element(By.XPATH, '//input[@name="bank_select"][@value="S"][2]')
        el.click()

        el = self.driver.find_element(By.XPATH, '//input[@type="button"][@value="Continue"]')
        el.click()
        sleep(5)

        ok = self.x('//button[text()="Ok"]')
        ok.click()

        # just waiting for sbi-pay to load
        _ = self.x('//div[text()="Order Summary"]')

        self.scrollToEnd()
        sleep(3)
        paypal_row = self.x('//a[@href="#collapsepp"]')
        self.driver.execute_script("calcFees('PAYPAL', arguments[0], arguments[0].id);", paypal_row)
        self.driver.execute_script("arguments[0].click();", paypal_row)
        sleep(5)

        paypal = self.x('//button[@name="paypal_Submit"]')
        paypal.click()
        sleep(5)
        # waiting for paypal to open up
        _ = self.x('//button[@id="startOnboardingFlow"]')

        action = webdriver.ActionChains(self.driver)

        login = self.x('//input[@id="email"]')
        sleep(uniform(2.5, 5))
        action.move_to_element(login).move_by_offset(10, 20).click().perform()
        sleep(uniform(1, 3))
        for l in PAYPAL_LOGIN:
            login.send_keys(l)
            sleep(uniform(0.043, 0.096))
        login.send_keys(Keys.ENTER)

        HIDDEN_CAPTCHA = '//input[@type="hidden"][contains(@name,"captcha")]'
        challenge = self.driver.find_elements_by_xpath(HIDDEN_CAPTCHA)
        if len(challenge):
            sitekey = '6LeZ6egUAAAAAGwL8CjkDE8dcSw2DtvuVpdwTkwG'
            result = self.captcha_solver.recaptcha(sitekey=sitekey, url=self.driver.current_url, enterprise=1)
            TOKEN_FROM_2CAPTCHA = result['code']
            logger.debug(f'{TOKEN_FROM_2CAPTCHA=}')
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, f'//iframe[contains(@src,"{sitekey}")]'))
            )
            textarea = self.driver.find_element_by_xpath('//*[@id="g-recaptcha-response"]')

            self.driver.execute_script("arguments[0].style.display='inline';", textarea)
            sleep(3)
            self.driver.execute_script(f"arguments[0].innerText='{TOKEN_FROM_2CAPTCHA}';", textarea)
            sleep(3)
            self.driver.execute_script(f"verifyCallback('{TOKEN_FROM_2CAPTCHA}');")

        password = self.x('//input[@id="password"]')
        sleep(3.1)
        password.click()
        sleep(1.7)
        for l in PAYPAL_PASS:
            password.send_keys(l)
            sleep(0.05)

        next = self.x('//button[@id="btnLogin"]')
        sleep(1.7)
        next.click()
        return
        otp = self.x('//input[@id="otpCode"]')
        otp.click()
        sleep(2)
        code = pyotp.TOTP(MFA_STRING)
        otp.send_keys(code.now())

        next = self.x('//button[@type="submit"]')
        next.click()

        submit = self.x('//button[@id="payment-submit-btn"]')

    def step_download_and_save_receipt(self):
        el = self.driver.find_element(By.CSS_SELECTOR, "input[name='submit_btn'][value='Generate Fee Receipt']")
        el.click()

        self.wait_file_download()
        downloaded_files = self.get_downloaded_files()
        file_content = self.get_file_content(downloaded_files[0])
        with open(f"src/automation/output/receipt_{self.session_id}.pdf", "wb") as f:
            f.write(file_content)

    def submit_visa(self):

        try:
            self.step_registration()
            self.step_basic_details()
            self.step_family_details_step()
            self.step_visa_details_step()
            self.step_additional_questions()
            self.step_photo_upload()
            self.step_crop_photo()
            self.step_document_upload_step()
            self.verification()
            self.fee_payment()
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            formatted_exception_info = f'Info: {str(e)}\nType: {exc_type}\nFile: {fname}\nLine: {exc_tb.tb_lineno}'
            logger.debug(formatted_exception_info)
            return formatted_exception_info
        else:
            if self.refid:
                logger.debug(self.refid)
                return self.refid
            self.step_download_and_save_receipt()
