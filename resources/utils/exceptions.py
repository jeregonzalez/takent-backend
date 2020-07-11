from werkzeug.exceptions import HTTPException

MSG_MISSING_REQUIRED_FIELDS = 'Missing required fields'
MSG_USER_ALREADY_EXISTS = 'User {} already exists'
MSG_USER_NOT_EXISTS = 'User {} not exists'
MSG_AUTHORIZATION_HEADER_MISSING = 'Authorization header is missing'
MSG_AUTHORIZATION_TOKEN_EXPIRED = 'Authorization token expired'
MSG_UNAUTHORIZED = 'Unauthorized'
MSG_UNSUPPORTED_CONTENT_TYPE = 'Unsupported content type {}'
MSG_UNSUPPORTED_RESPONSE_TYPE = 'Unsupported response type {}'


def message(code, info):
    return {'code': code, 'message': info}


class MissingRequiredFieldsException(HTTPException):
    code = 400
    data = message(400, MSG_MISSING_REQUIRED_FIELDS)


class UserAlreadyExistsException(HTTPException):
    def __init__(self, user):
        self.code = 400
        self.data = message(400, MSG_USER_ALREADY_EXISTS.format(user))
        super().__init__()


class UserNotExistsException(HTTPException):
    def __init__(self, user):
        self.code = 400
        self.data = message(400, MSG_USER_NOT_EXISTS.format(user))
        super().__init__()


class AuthorizationHeaderMissingException(HTTPException):
    code = 400
    data = message(400, MSG_AUTHORIZATION_HEADER_MISSING)


class AuthorizationTokenExpiredException(HTTPException):
    code = 403
    data = message(403, MSG_AUTHORIZATION_TOKEN_EXPIRED)


class UnauthorizedException(HTTPException):
    code = 403
    data = message(403, MSG_UNAUTHORIZED)


class UnsupportedContentTypeException(HTTPException):
    def __init__(self, content_type):
        self.code = 403
        self.data = message(403, MSG_UNSUPPORTED_CONTENT_TYPE.format(content_type))
        super().__init__()


class UnsupportedResponseType(HTTPException):
    def __init__(self, accept):
        self.code = 403
        self.data = message(403, MSG_UNSUPPORTED_RESPONSE_TYPE.format(accept))
        super().__init__()
