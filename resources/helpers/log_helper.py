import logging

from flask import request

LOGGER = logging.getLogger('app')
LOGGER_REQUEST_INFO = logging.getLogger('requests')


def log_request_info():
    LOGGER_REQUEST_INFO.info("""{path}
-------------------------------------------------------------------
Headers:
{headers}
-------------------------------------------------------------------
Body:
{body}
-------------------------------------------------------------------"""
                             .format(path=request.path,
                                     headers=request.headers,
                                     body=request.data.decode('utf-8')))
