import time
import os, sys

from loguru import logger
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import alert_is_present
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait

from src.automation.countries.visa_application_base import VisaApplicantionBase


class VisaApplicantionKenya(VisaApplicantionBase):
    def __init__(self, session_id: str, kwargs: dict):
        super().__init__(session_id, kwargs)
        self.url = "https://accounts.ecitizen.go.ke/login"

        # login
        self.submiter_email = kwargs.get("submiter_email", "")
        self.submiter_password = kwargs.get("submiter_password", "")

        # 3. step_nationality_and_residence
        self.nationality_at_birth = kwargs.get("nationality_at_birth", "")
        self.present_nationality_if_different = kwargs.get("present_nationality_if_different", "")
        self.applicant_continent_of_residence = kwargs.get("applicant_continent_of_residence", "")
        self.applicant_country_of_residence = kwargs.get("applicant_country_of_residence", "")
        self.applicant_physical_address = kwargs.get("applicant_physical_address", "")
        self.applicant_phone_number = kwargs.get("applicant_phone_number", "")
        self.applicant_city_town = kwargs.get("applicant_city_town", "")

        # 4. step_passport_information
        self.passport_issued_by = kwargs.get("passport_issued_by", "")

        # 5. step_travelling_informations
        self.previous_visits_to_kenya = kwargs.get("previous_visits_to_kenya", [])

        # 7 step_applicants_information
        self.applicant_gender = kwargs.get("applicant_gender", "")
        self.applicant_marital_status = kwargs.get("applicant_marital_status", "")
        self.applicant_current_ocupation = kwargs.get("applicant_current_ocupation", "")
        self.applicant_father_status = kwargs.get("applicant_father_status", "")
        self.applicant_father_name = kwargs.get("applicant_father_name", "")
        self.applicant_mother_status = kwargs.get("applicant_mother_status", "")
        self.applicant_mother_name = kwargs.get("applicant_mother_name", "")
        self.applicant_next_of_kin_name = kwargs.get("applicant_next_of_kin_name", "")
        self.applicant_next_of_kin_number = kwargs.get("applicant_next_of_kin_number", "")
        
        # 8 step_travel_information
        self.applicant_reason_for_travek = kwargs.get("applicant_reason_for_travek", "")
        self.applicant_proposed_date_of_entry = kwargs.get("applicant_proposed_date_of_entry", "")
        self.applicant_proposed_departure_from_entry = kwargs.get("applicant_proposed_departure_from_entry", "")
        self.host_detail = kwargs.get("host_detail", "")
        self.full_names_and_physical_address_of_the_host = kwargs.get("full_names_and_physical_address_of_the_host", "")
        self.host_telephone_number = kwargs.get("host_telephone_number", "")
        self.host_email = kwargs.get("host_email", "")
        self.applicant_arrives_by = kwargs.get("applicant_arrives_by", "")
        self.applicant_arrives_by = kwargs.get("applicant_arrives_by", "")
        self.point_of_entry = kwargs.get("point_of_entry", "")

        # 9 step_travel_history
        self.recent_visits_to_other_countries_in_3_months = kwargs.get("recent_visits_to_other_countries_in_3_months", "")
        
        # 10 step_uploads
        self.photo_recent_passport_size = kwargs.get("photo_recent_passport_size", "")
        self.photo_passport_front_cover = kwargs.get("photo_passport_front_cover", "")
        self.photo_passport_biodata_page = kwargs.get("photo_passport_biodata_page", "")
        self.photo_hotel_reservation = kwargs.get("photo_hotel_reservation", "")

        # step_pay_for_service
        self.card_number = kwargs.get("card_number", "")
        self.card_cvv = kwargs.get("card_cvv", "")
        self.card_expiration_month = kwargs.get("card_expiration_month", "")
        self.card_expiration_year = kwargs.get("card_expiration_year", "")
        

    def step_login_and_navigate_to_application(self):
        self.driver.get(self.url)

        el = self.driver.find_element(By.ID, "auth_username")
        el.send_keys(self.submiter_email)

        el = self.driver.find_element(By.ID, "auth_pwd")
        el.send_keys(self.submiter_password)

        el = self.driver.find_element(By.CSS_SELECTOR, 'input[value="Login"]')
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="passport.ecitizen.go.ke"]')
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, 'button[name="allow"]')
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="apply"]')
        el.click()

    def step_application_information(self):
        self.action_click_next_btn()

    def step_evisa_applicant(self):
        self.action_select_visible_text('Adult', element_id='sq_101i')
        self.action_click_next_btn()

    def step_nationality_and_residence(self):
        self.action_select_visible_text(self.nationality_at_birth, element_id='sq_104i')
        self.action_select_visible_text(self.present_nationality_if_different, element_id='sq_105i')
        self.action_select_visible_text(self.applicant_continent_of_residence, element_id='sq_106i')
        self.action_select_visible_text(self.applicant_country_of_residence, element_id='sq_107i')
        self.action_write_text_field(self.applicant_physical_address, element_id='sq_111i')
        self.action_write_text_field(self.applicant_phone_number, element_id='sq_112i')
        self.action_write_text_field(self.applicant_city_town, element_id='sq_113i')
        self.action_write_text_field(self.email, element_id='sq_114i')
        self.action_click_next_btn()

    def step_passport_information(self):
        self.action_select_visible_text('National Passport', element_id='sq_115i')
        self.action_write_text_field(self.passport_number, element_id='sq_119i')
        self.action_write_text_field(self.passport_place_issue, element_id='sq_120i')
        self.action_write_date_field(self.passport_date_issue, element_id='sq_121')
        self.action_write_date_field(self.passport_date_expiry, element_id='sq_122')
        self.action_write_text_field(self.passport_issued_by, element_id='sq_123i')
        self.action_click_next_btn()

    def step_travelling_informations(self):
        has_visited_kenya = len(self.previous_visits_to_kenya) > 0
        has_visited_kenya_txt = 'YES' if has_visited_kenya else 'NO'

        self.action_select_visible_text(has_visited_kenya_txt, 'sq_125i')

        for i in range(len(self.previous_visits_to_kenya)):
            time.sleep(0.3)
            if i != 0:
                el = self.driver.find_element_by_xpath("//span[contains(text(), 'Add row')]")
                el.click()
                time.sleep(0.3)
            
            el = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="date"')[i]
            el.send_keys(self.previous_visits_to_kenya[i]["date"])

            el = Select(self.driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Duration"')[i])
            el.select_by_visible_text(self.previous_visits_to_kenya[i]["duration"])

            el = self.driver.find_elements(By.CSS_SELECTOR, 'input[aria-label="eVisa Number"')[i]
            el.send_keys(self.previous_visits_to_kenya[i]["evisa_number"])

        self.action_select_visible_text('No', 'sq_132i')

        self.action_click_next_btn()


    def step_visa_details(self):
        self.action_select_visible_text('Single Entry Visa', element_id='sq_142i')
        self.action_click_next_btn()

    def step_applicants_information(self):
        self.action_write_text_field(self.surname, element_id='sq_149i')
        self.action_write_text_field(self.given_name, element_id='sq_150i')
        self.action_select_visible_text(self.applicant_gender, element_id='sq_151i')
        self.action_select_visible_text(self.applicant_marital_status, element_id='sq_152i')
        self.action_write_date_field(self.date_of_birth, element_id='sq_153')
        self.action_write_text_field(self.applicant_city_town, element_id='sq_155i')
        self.action_select_visible_text(self.nationality_at_birth, element_id='sq_156i')
        self.action_write_text_field(self.applicant_current_ocupation, element_id='sq_157i')

        self.action_select_visible_text(self.applicant_father_status, element_id='sq_158i')
        if 'Unknown' != self.applicant_father_status:
            self.action_write_text_field(self.applicant_father_name, element_id='sq_159i')
        
        self.action_select_visible_text(self.applicant_mother_status, element_id='sq_161i')
        if 'Unknown' != self.applicant_mother_status:
            self.action_write_text_field(self.applicant_mother_name, element_id='sq_162i')
        
        self.action_write_text_field(self.applicant_next_of_kin_name, element_id='sq_166i')
        self.action_write_text_field(self.applicant_next_of_kin_number, element_id='sq_167i')

        self.action_click_next_btn()



    def step_travel_information(self):
        self.action_select_visible_text(self.applicant_reason_for_travek, element_id='sq_168i')
        self.action_write_date_field(self.applicant_proposed_date_of_entry, element_id='sq_169')
        self.action_write_date_field(self.applicant_proposed_departure_from_entry, element_id='sq_170')
        self.action_select_visible_text(self.host_detail, element_id='sq_171i')
        self.action_write_text_field(self.full_names_and_physical_address_of_the_host, element_id='sq_173i')
        self.action_write_text_field(self.host_telephone_number, element_id='sq_174i')
        self.action_write_text_field(self.host_email, element_id='sq_175i')
        self.action_select_visible_text(self.applicant_arrives_by, element_id='sq_176i')
        self.action_select_visible_text(self.point_of_entry, element_id='sq_177i')

        self.action_click_next_btn()


    def step_travel_history(self):
        has_visited_other_countries = len(self.recent_visits_to_other_countries_in_3_months) > 0
        has_visited_other_countries_txt = 'YES' if has_visited_other_countries else 'NO'

        self.action_select_visible_text(has_visited_other_countries_txt, 'sq_178i')

        for i in range(len(self.recent_visits_to_other_countries_in_3_months)):
            time.sleep(0.3)
            if i != 0:
                el = self.driver.find_element_by_xpath("//span[contains(text(), 'Add row')]")
                el.click()
                time.sleep(0.3)
            
            el = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="date"')[i]
            el.send_keys(self.recent_visits_to_other_countries_in_3_months[i]["date"])

            el = Select(self.driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Duration"')[i])
            el.select_by_visible_text(self.recent_visits_to_other_countries_in_3_months[i]["duration"])

            el = Select(self.driver.find_elements(By.CSS_SELECTOR, 'select[aria-label="Country"')[i])
            el.select_by_visible_text(self.recent_visits_to_other_countries_in_3_months[i]["country"])

        self.action_select_visible_text('Yes', 'sq_184i')
        self.action_select_visible_text('No', 'sq_186i')
        self.action_select_visible_text('No', 'sq_194i')
        self.action_select_visible_text('No', 'sq_201i')

        self.action_click_next_btn()

    def step_uploads(self):
        with self.create_temp_file_from_data_uri_str(self.photo_recent_passport_size) as f:
            self.action_write_text_field(f.name, element_id='sq_211i')
        time.sleep(1)

        with self.create_temp_file_from_data_uri_str(self.photo_passport_front_cover) as f:
            self.action_write_text_field(f.name, element_id='sq_212i')
        time.sleep(1)

        with self.create_temp_file_from_data_uri_str(self.photo_passport_biodata_page) as f:
            self.action_write_text_field(f.name, element_id='sq_213i')
        time.sleep(1)

        with self.create_temp_file_from_data_uri_str(self.photo_hotel_reservation) as f:
            self.action_write_text_field(f.name, element_id='sq_214i')

        # wait a bit more for the images to get uploaded
        time.sleep(3)

        self.action_click_next_btn()

    def step_review_application(self):
        el = self.driver.find_element(By.ID, 'sq_242i_0')
        el.click()

        el = self.driver.find_element(By.CSS_SELECTOR, 'input[value="Preview"]')
        el.click()

    def step_complete(self):
        el = self.driver.find_element(By.CSS_SELECTOR, 'input[value="Complete"]')
        el.click()

    def step_pay_for_service(self):
        # switch to payment iframe "my_frame"
        wait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, 'my_frame')))

        el = self.driver.find_element(By.ID, 'equitycard')
        el.click()

        self.action_write_text_field(self.card_number, element_id='CardNo')
        self.action_write_text_field(self.card_cvv, element_id='CVV')
        self.action_select_visible_text(self.card_expiration_month, element_id='eMonth')
        self.action_select_visible_text(self.card_expiration_year, element_id='eYear')

        el = self.driver.find_element(By.ID, 'btnCard')
        el.click()

        time.sleep(15) # wait for payment to be successfull
        # TODO, wait for successfull payment instead
        # this is not working. I can't find the element inside the iframe
        #wait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Payment Failed')]")))

        #self.driver.switch_to.default_content()

    def action_write_text_field(self, value: str, element_id: str):
        el = self.driver.find_element(By.ID, element_id)
        el.send_keys(value)
    
    def action_write_date_field(self, value: str, element_id: str):
        el = self.driver.find_element(By.CSS_SELECTOR, f'#{element_id} input')
        el.send_keys(value)

        time.sleep(0.2)

        # clik in the active date to pass validation
        el = self.driver.find_element(By.CSS_SELECTOR, 'td.active.day')
        el.click()

        # make the calendar disapear by clicking somewhere else
        el = self.driver.find_element(By.CSS_SELECTOR, f'#{element_id} input')
        el.send_keys(Keys.ESCAPE)

    def action_select_visible_text(self, value: str, element_id: str):
        el = Select(self.driver.find_element(By.ID, element_id))
        el.select_by_visible_text(value)

    def action_click_next_btn(self):
        el = self.driver.find_element(By.CSS_SELECTOR, 'input[value="Next"]')
        el.click()

    def submit_visa(self):
        try:
            self.step_login_and_navigate_to_application()
            self.step_application_information()
            self.step_evisa_applicant()
            self.step_nationality_and_residence()
            self.step_passport_information()
            self.step_travelling_informations()
            self.step_visa_details()
            self.step_applicants_information()
            self.step_travel_information()
            self.step_travel_history()
            self.step_uploads()
            self.step_review_application()
            self.step_complete()
            self.step_pay_for_service()
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            formatted_exception_info = f'Info: {str(e)}\nType: {exc_type}\nFile: {fname}\nLine: {exc_tb.tb_lineno}'
            logger.debug(formatted_exception_info)
            return formatted_exception_info
