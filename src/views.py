import os
from django.http import HttpResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from celery.result import AsyncResult
from src.visaapplication.tasks import app
from loguru import logger

CDP = 'Content-disposition'


def download_form(request, file):
    if os.path.exists(f'/app/files/{file}.pdf'):
        print('exists')
        with open(f'/app/files/{file}.pdf', 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response[CDP] = f'attachment ; filename = {file}.pdf'
            return response
        raise Http404


@csrf_exempt
def check_task(request):
    response = {'info': 'Method GET is not implemented'}
    if request.method == 'POST':
        id = json.loads(request.body).get('id', None)
        logger.debug(f'checking state for {id=}')
        if id:
            result = AsyncResult(id, app=app)
            logger.info(f'{id=} {result.state=}')
            response = {'state': result.state}
            if result.state == 'SUCCESS':
                response['result'] = result.get()

    return JsonResponse(response)
