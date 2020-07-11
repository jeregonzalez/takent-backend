import json

from flask import make_response

from resources.helpers.encoder_helper import CustomEncoder


def json_output(data, code, headers=None):
    dumped = json.dumps(data, cls=CustomEncoder)
    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp
