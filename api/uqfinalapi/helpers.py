"""
A collection of handy helpers
"""
from functools import wraps
import json
from flask import Response
from werkzeug.exceptions import HTTPException
import logging

logging.basicConfig()
logger = logging.getLogger('api')

SUCCESS = 'success'
ERROR = 'error'
FAIL = 'fail'


class APIException(Exception):
    pass


class APIFailureException(APIException):
    pass


class APINotFoundException(APIException):
    pass


class NoResultFound(Exception):
    pass


def api_response(f):
    """
    Converts an object into an api response
    """
    @wraps(f)
    def inner(*args, **kwargs):
        response = Response()
        response.content_type = 'application/json'
        try:
            result = f(*args, **kwargs)
            result = {
                'status': SUCCESS,
                'data': result,
            }
            response.status_code = 200
        except APINotFoundException as e:
            result = {
                'status': FAIL,
                'message': str(e)
            }
            response.status_code = 404
        except APIFailureException as e:
            result = {
                'status': FAIL,
                'message': str(e),
            }
            response.status_code = 500
        except HTTPException:
            raise # This causes issues
        except Exception as e:
            logger.exception(e)
            result = {
                'status': ERROR,
                'message': str(e),
            }
            response.status_code = 500

        response.data = json.dumps(result)
        return response

    return inner
