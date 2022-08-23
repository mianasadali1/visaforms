import glob
from logging import Logger
import os, sys
from pathlib import Path
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from uuid import uuid4
from src.automation.countries.visa_application_base import VisaApplicantionBase
from selenium.common.exceptions import TimeoutException
from time import sleep
from random import uniform
from tenacity import retry, wait_fixed

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

NEXT = 'PassportWizard_StepNavigationTemplateContainerID_StartNextPreviousButton'
PRINT = 'PassportWizard_nextStepsStep_printFormButton'
CONFIRM = 'PassportWizard_nextStepsStep_ConfirmationCheckBox'
FINISH = 'PassportWizard_FinishNavigationTemplateContainerID_FinishButton'


class USPassportRenew(VisaApplicantionBase):
    def __init__(self, session_id: str, kwargs: dict):
        super().__init__(session_id, kwargs)
        self.url = "https://pptform.state.gov/PassportWizardMain.aspx"

        # step 1
        self.given_name = kwargs.get("given_name", "")
        self.surname = kwargs.get("surname", "")
        self.midname = kwargs.get("midname", "")
        self.date_of_birth = kwargs.get("date_of_birth", "")
        self.city_of_birth = kwargs.get("city_of_birth", "")
        self.country_of_birth = kwargs.get("country_of_birth", "")
        self.state_of_birth = kwargs.get("state_of_birth", "")
        self.ssn = kwargs.get("ssn", "")
        self.gender = kwargs.get("gender", "")
        self.height_feet = kwargs.get("height_feet", "")
        self.height_inches = kwargs.get("height_inches", "")
        self.hair = kwargs.get("hair", "")
        self.eye_color = kwargs.get("eye_color", "")
        self.occupation = kwargs.get("occupation", "")
        # STEP2
        self.address1 = kwargs.get("address1", "")
        self.address2 = kwargs.get("address2", "")
        self.city = kwargs.get("city", "")
        self.country = kwargs.get("country", "")
        self.state = kwargs.get("state", "")
        self.zip = kwargs.get("zip", "")
        self.email = kwargs.get("email", "")
        self.phone = kwargs.get("phone", "")
        # STEP5
        # passport book, YES
        self.passport_have = kwargs.get("passport_have", "")
        self.passport_posession = kwargs.get("passport_posession", "")
        self.passport_lost_report = kwargs.get("passport_lost_report", "")
        self.passport_lost_how = kwargs.get("passport_lost_how", "")
        self.passport_lost_where = kwargs.get("passport_lost_where", "")
        self.passport_lost_date = kwargs.get("passport_lost_date", "")
        self.passport_book_first = kwargs.get("passport_book_first", "")
        self.passport_book_lastname = kwargs.get("passport_book_lastname", "")
        self.passport_issue_date = kwargs.get("passport_issue_date", "")
        self.passport_name_change = kwargs.get("passport_name_change", "")
        self.passport_reason_name_change = kwargs.get("passport_reason_name_change", "")
        self.passport_date_name_change = kwargs.get("passport_date_name_change", "")
        self.passport_place_change = kwargs.get("passport_place_change", "")
        self.passport_number = kwargs.get("passport_number", "")
        self.mother_name = kwargs.get("mother_name", "")
        self.mother_surname = kwargs.get("mother_surname", "")
        self.mother_gender = kwargs.get("mother_gender", "")
        self.mother_us_citizen = kwargs.get("mother_us_citizen", "")
        self.father_name = kwargs.get("father_name", "")
        self.father_surname = kwargs.get("father_surname", "")
        self.father_gender = kwargs.get("father_gender", "")
        self.father_us_citizen = kwargs.get("father_us_citizen", "")
        self.been_married = kwargs.get("been_married", "")
        self.spouse_fullname = kwargs.get("spouse_fullname", "")
        self.spouse_birth_date = kwargs.get("spouse_birth_date", "")
        self.spouse_place_of_birth = kwargs.get("spouse_place_of_birth", "")
        self.spouse_us_citizen = kwargs.get("spouse_us_citizen", "")
        self.date_of_most_recent_marriage = kwargs.get("date_of_most_recent_marriage", "")
        self.been_widowed_or_divorced = kwargs.get("been_widowed_or_divorced", "")
        # STEP6
        # STEP7 summary
        # STEP8 Passport_book_130$
        # STEP9 I have read, Download form
        self.link = ''

    def i(self, id: str, timeout: int = 30) -> WebElement:
        """useful for locating element by id with timeout,
        thus letting the element load for some time"""
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, id)))

    def x(self, locator: str, timeout: int = 30) -> WebElement:
        """useful for locating element by xpath with timeout,
        thus letting the element load for some time"""
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))

    def click_next(self):
        self.i(NEXT).click()
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        except TimeoutException:
            pass
        else:
            exception_info = self.driver.switch_to.alert.text
            logger.debug(exception_info)
            self.driver.switch_to.alert.accept()
            raise Exception(exception_info)

    def click_radios(self, radios: dict):
        for k, v in radios.items():
            try:
                self.x(f'//input[starts-with(@id,"{k}")][@value="{v}"]', 20).click()
                logger.debug(f'set {k}={v}')
                sleep(uniform(4, 6))
            except Exception as exc:
                # if k == "PassportWizard_mostRecentPassportContinued_dataIncorrectNone":
                pass
                # else:
                    # key_for_label = "_".join(k.split("_")[:2])
                    # failed_field = self.x(f'//label[starts-with(@id,"{key_for_label}")]', 20).text
                    # exception_info = "Failed on question: '%s'; key: '%s'; value: '%s'; method: '%s'" % (failed_field, k, v, "click_radios")
                    # logger.debug(exception_info)
                    # raise exc.__class__(exception_info)

    def select_selects(self, selects: dict):
        for k, v in selects.items():
            el = Select(self.i(k))
            el.select_by_visible_text(v.upper())
            logger.debug(f'set {k}={v}')
            sleep(0.05)

    def fill_textfields(self, textfields: dict):
        for k, v in textfields.items():
            self.i(k).send_keys(v.upper())
            logger.debug(f'set {k}={v}')
            sleep(0.05)

    def step1(self):
        self.driver.get(self.url)
        sleep(2)
        self.i('PassportWizard_portalStep_ApplyButton').click()
        _ = self.i('PassportWizard_aboutYouStep_pageHeaderPanel')

        radios = {'PassportWizard_aboutYouStep_sexList': self.gender}
        self.click_radios(radios)

        selects = {
            'PassportWizard_aboutYouStep_pobCountryList': self.country_of_birth,
            'PassportWizard_aboutYouStep_pobStateList': self.state_of_birth,
            'PassportWizard_aboutYouStep_hairList': self.hair,
            'PassportWizard_aboutYouStep_heightFootList': self.height_feet,
            'PassportWizard_aboutYouStep_heightInchList': self.height_inches,
            'PassportWizard_aboutYouStep_eyeList': self.eye_color,
        }
        self.select_selects(selects)

        textfields = {
            'PassportWizard_aboutYouStep_firstNameTextBox': self.given_name,
            'PassportWizard_aboutYouStep_lastNameTextBox': self.surname,
            'PassportWizard_aboutYouStep_middleNameTextBox': self.midname,
            'PassportWizard_aboutYouStep_dobTextBox': self.date_of_birth,
            'PassportWizard_aboutYouStep_pobCityTextBox': self.city_of_birth,
            'PassportWizard_aboutYouStep_ssnTextBox': self.ssn,
            'PassportWizard_aboutYouStep_occupationTextBox': self.occupation,
        }
        self.fill_textfields(textfields)
        # self.i(NEXT).click()
        self.click_next()

    def step2(self):
        _ = self.i('PassportWizard_addressStep_mailPassportWherePanel')

        radios = {
            'PassportWizard_addressStep_permanentAddressList': "Yes",
            'PassportWizard_addressStep_CommunicateEmail': 'CommunicateEmail',
            'PassportWizard_addressStep_PhoneNumberType': 'C',
        }

        self.click_radios(radios)

        selects = {
            'PassportWizard_addressStep_mailCountryList': self.country,
            'PassportWizard_addressStep_mailStateList': self.state,
        }
        self.select_selects(selects)

        textfields = {
            'PassportWizard_addressStep_mailStreetTextBox': self.address1,
            'PassportWizard_addressStep_mailStreet2TextBox': self.address2,
            'PassportWizard_addressStep_mailCityTextBox': self.city,
            'PassportWizard_addressStep_mailZipTextBox': self.zip,
            'PassportWizard_addressStep_emailTextBox': self.email,
            'PassportWizard_addressStep_confirmEmailTextBox': self.email,
            'PassportWizard_addressStep_addPhoneNumberTextBox': self.phone,
        }

        self.fill_textfields(textfields)

        # self.i(NEXT).click()
        self.click_next()

    def step3(self):
        _ = self.x('//h1[contains(text(),"Travel Plans")]')
        # self.i(NEXT).click()
        self.click_next()

    def step4(self):
        _ = self.x('//h1[contains(text(),"Who should we contact in case of an emergency?")]')
        # self.i(NEXT).click()
        self.click_next()

    def step5(self):
        _ = self.x('//h1[contains(text(),"Your Most Recent Passport")]')

        textfields = {}

        radios = {
            'PassportWizard_mostRecentPassport_CurrentHave': self.passport_have,  # CurrentHaveBook or CurrentHaveNone
        }
        if 'CurrentHaveBook' in radios['PassportWizard_mostRecentPassport_CurrentHave']:
            radios['PassportWizard_mostRecentPassport_Book'] = self.passport_posession

            textfields = {
                'PassportWizard_mostRecentPassport_BookIssueDate': self.passport_date_issue,
                'PassportWizard_mostRecentPassport_firstNameOnBook': self.passport_book_first,
                'PassportWizard_mostRecentPassport_lastNameOnBook': self.passport_book_lastname,
                'PassportWizard_mostRecentPassport_ExistingBookNumber': self.passport_number,
            }

            if any([x in radios['PassportWizard_mostRecentPassport_Book'] for x in ['Lost', 'Stolen']]):
                radios['PassportWizard_mostRecentPassport_ReportLostBook'] = self.passport_lost_report


        self.click_radios(radios)

        self.fill_textfields(textfields)

        # self.i(NEXT).click()
        self.click_next()

        if len(self.driver.find_elements(By.XPATH, '//h1[contains(text(),"Lost Or Stolen Passport Information")]')):
            radios = {
                'PassportWizard_lostStolenStep_reporter': 'reporterYesRadioButton',
                'PassportWizard_lostStolenStep_lostPrev': 'lostPrevNoRadioButton',
            }
            self.click_radios(radios)

            textfields = {
                'PassportWizard_lostStolenStep_bookLostHowTextBox': self.passport_lost_how,
                'PassportWizard_lostStolenStep_bookLostWhereTextBox': self.passport_lost_where,
                'PassportWizard_lostStolenStep_bookLostDateTextBox': self.passport_lost_date,
            }
            self.fill_textfields(textfields)
            # self.i(NEXT).click()
            self.click_next()

        if len(self.driver.find_elements(By.XPATH, '//h1[contains(text(),"Parent & Spouse Information")]')):

            radios = {
                'PassportWizard_moreAboutYouStep_parent1SexList': self.father_gender,
                'PassportWizard_moreAboutYouStep_parent1CitizenList': self.father_us_citizen,
                'PassportWizard_moreAboutYouStep_parent2SexList': self.mother_gender,
                'PassportWizard_moreAboutYouStep_parent2CitizenList': self.mother_us_citizen,
                'PassportWizard_moreAboutYouStep_marriedList': self.been_married,
            }

            textfields = {
                'PassportWizard_moreAboutYouStep_parent1FirstNameTextBox': self.father_name,
                'PassportWizard_moreAboutYouStep_parent1LastNameTextBox': self.father_surname,
                'PassportWizard_moreAboutYouStep_parent2FirstNameTextBox': self.mother_name,
                'PassportWizard_moreAboutYouStep_parent2LastNameTextBox': self.mother_surname,
            }

            if 'Yes' in radios['PassportWizard_moreAboutYouStep_marriedList']:
                radios['PassportWizard_moreAboutYouStep_divorcedList'] = self.been_widowed_or_divorced
                radios['PassportWizard_moreAboutYouStep_spouseCitizenList'] = self.spouse_us_citizen
                textfields['PassportWizard_moreAboutYouStep_spouseNameTextBox'] = self.spouse_fullname
                textfields['PassportWizard_moreAboutYouStep_spouseBirthDateTextBox'] = self.spouse_birth_date
                textfields['PassportWizard_moreAboutYouStep_marriedDateTextBox'] = self.date_of_most_recent_marriage
                textfields['PassportWizard_moreAboutYouStep_spouseBirthplaceTextBox'] = self.spouse_place_of_birth

            self.click_radios(radios)

            self.fill_textfields(textfields)
            # self.i(NEXT).click()
            self.click_next()

        if len(self.driver.find_elements(By.XPATH, '//h1[contains(text(),"Your Most Recent Passport")]')):
            radios = {
                'PassportWizard_mostRecentPassportContinued_dataIncorrectNone': 'dataIncorrectNone',
                'PassportWizard_mostRecentPassportContinued_DataChangedYesNoButtons': 'No',
                'PassportWizard_mostRecentPassportContinued_nameChange': self.passport_name_change,  # nameChangeBook / nameChangeNone
            }

            textfields = {}
            if 'nameChangeBook' in radios['PassportWizard_mostRecentPassportContinued_nameChange']:
                radios['PassportWizard_mostRecentPassportContinued_NameChangeReason'] = self.passport_reason_name_change  # M or C
                radios['PassportWizard_mostRecentPassportContinued_NameChangeCertified'] = 'Yes'

                textfields = {
                    'PassportWizard_mostRecentPassportContinued_NameChangeDate': self.passport_date_name_change,
                    'PassportWizard_mostRecentPassportContinued_NameChangePlace': self.passport_place_change,
                }

            self.click_radios(radios)

            self.fill_textfields(textfields)
            # self.i(NEXT).click()
            self.click_next()

    def step6(self):
        _ = self.x('//h1[contains(text(),"List all other names you have used")]')
        # self.i(NEXT).click()
        self.click_next()

    def step7(self):
        _ = self.x('//h1[contains(text(),"Personal Application")]')

        self.scrollToEnd()
        # self.i(NEXT).click()
        self.click_next()

    def step8(self):
        _ = self.x('//h1[contains(text(),"Passport Products and Fees")]')
        radios = {'PassportWizard_feesStep_bookFee': 'bookFee'}
        self.click_radios(radios)
        self.i(FINISH).click()

        if len(self.driver.find_elements(By.XPATH, '//h1[contains(text(),"Electronic Signature")]')):
            radios = {
                'PassportWizard_esignatureStep_lostOrStolenDelivery': 'Print, Sign and Mail',
            }

            self.click_radios(radios)

            # self.i(NEXT).click()
            self.click_next()

    def step9(self):
        _ = self.i('PassportWizard_nextStepsStep_PrintFormInstructionRow')
        self.i(CONFIRM).click()
        self.i(PRINT).click()
        form_pdf = self.check_downloads()
        logger.debug(form_pdf)
        form = Path(form_pdf)
        newform = uuid4()
        form.rename(Path(f'/app/files/{newform}.pdf'))
        self.link = f'http://137.184.16.25:8080/df/{newform}/'
        self.driver.quit()

    @retry(wait=wait_fixed(5))
    def check_downloads(self, dir: str = '/app/files') -> str:
        list_of_pdf_files = glob.glob(f"{dir}/DS*.pdf")
        return str(max(list_of_pdf_files, key=os.path.getmtime))

    def scrollToEnd(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    # def step_download_and_save_receipt(self):
    #     el = self.driver.find_element(By.CSS_SELECTOR, "input[name='submit_btn'][value='Generate Fee Receipt']")
    #     el.click()

    #     self.wait_file_download()
    #     downloaded_files = self.get_downloaded_files()
    #     file_content = self.get_file_content(downloaded_files[0])
    #     with open(f"src/automation/output/receipt_{self.session_id}.pdf", "wb") as f:
    #         f.write(file_content)

    def submit_visa(self):
        try:
            self.step1()
            self.step2()
            self.step3()
            self.step4()
            self.step5()
            self.step6()
            self.step7()
            self.step8()
            self.step9()
        except Exception as e:
            # exc_type, _, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            formatted_exception_info = f'Info: {str(e)}'
            logger.debug(formatted_exception_info)
            self.driver.quit()
            return formatted_exception_info
        else:
            logger.debug(f'submitvisa ended, {self.link=}')
            return self.link
