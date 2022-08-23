from loguru import logger

from src.automation.countries.visa_application_turkey import VisaApplicantionTurkey
from src.automation.countries.visa_application_india import VisaApplicantionIndia
from src.automation.countries.visa_application_kenya import VisaApplicantionKenya
from src.automation.passport.us_passport_renew import USPassportRenew

logger.add("automation.log")


@logger.catch(reraise=True)
def submit_visa_application(session_id: str, country: str, applicantInfoDict: dict):
    logger.info(f"Initiating session ({session_id})")
    application = None
    if country == "india":
        application = VisaApplicantionIndia(session_id, applicantInfoDict)
    elif country == "turkey":
        application = VisaApplicantionTurkey(session_id, applicantInfoDict)
    elif country == "us-passp-renew":
        application = USPassportRenew(session_id, applicantInfoDict)
    elif country == "kenya":
        application = VisaApplicantionKenya(session_id, applicantInfoDict)
    elif not country:
        raise Exception("Country needs to be provided")
    else:
        raise Exception(f'Automation not implemented for "{country}"')

    application.init_driver()
    result = application.submit_visa()
    logger.debug('application.submit_visa ended')
    return result
