from src.config.celery import app
from loguru import logger
from src.automation.visa_application import submit_visa_application


@app.task(bind=True)
def enqueue(self, session_id, country, data):

    return submit_visa_application(session_id, country, applicantInfoDict=data)
