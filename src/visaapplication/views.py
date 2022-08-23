import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
import json
import traceback
from .tasks import enqueue


@csrf_exempt
def index(request):
    response = {'info': 'Method GET is not implemented'}
    if request.method == 'POST':
        data = json.loads(request.body).get('data', None)
        country = json.loads(request.body).get('country', None)
        id = str(uuid.uuid4())
        logger.debug(f'{id=}')
        logger.debug(f'Data is: {data}')
        if data and country:
            res = enqueue.apply_async((id, country, data), task_id=id)
            response = {'result': 'success', 'enqueued_id': res.id}
            # link = submit_visa_application(session_id, country, data)
            # logger.debug(f'submit in views ended, {link=}')
            # result = True
        else:
            error = 'You must provide "data" and "country"'
            response = {'result': 'fail', 'error': error}

        # response = {'success': result, 'link': str(link), 'session_id': session_id, 'error': error}
    return JsonResponse(response)
