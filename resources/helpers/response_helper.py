def message(code, info):
    return {'code': code, 'message': info}


def response(http_status_code, info):
    return message(http_status_code, info), http_status_code
