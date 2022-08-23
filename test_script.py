import uuid
import json
import sys, os

from loguru import logger

from src.automation.visa_application import submit_visa_application

if __name__ == "__main__":
    os.environ['VISAAPPLICATION_DEBUG'] = "1"

    application_result = ""
    country = 'turkey'

    test_data = None
    with open(f'src/automation/input_data/test/data_{country}.json', 'r') as f:
        test_data = json.load(f)

    if not test_data:
        logger.error("Test data is missing")
        sys.exit(os.EX_DATAERR)

    session_id = str(uuid.uuid4())

    submit_visa_application(session_id, test_data['country'], test_data['data'])

    if application_result == "":
        logger.success("Visa application submitted successfully!")
    else:
        logger.error("Error submitting visa application")
