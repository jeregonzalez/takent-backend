import json

from flask import make_response

from resources.helpers.encoder_helper import CustomEncoder
from resources.helpers.log_helper import LOGGER_REQUEST_INFO


def json_output(data, code, headers=None):
    dumped = json.dumps(data, cls=CustomEncoder)
    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    LOGGER_REQUEST_INFO.info("""Status code {status_code}
-------------------------------------------------------------------
Response headers:
{response_headers}
-------------------------------------------------------------------
Response body:
{response_body}
-------------------------------------------------------------------""".format(status_code=code,
                                                                              response_headers=headers,
                                                                              response_body=dumped))
    return resp
