from werkzeug.exceptions import HTTPException

MSG_MISSING_REQUIRED_FIELDS = 'Missing required fields'
MSG_SCHEMA_VALIDATION_ERROR = 'Schema is not valid: {}'
MSG_USER_ALREADY_EXISTS = 'User {} already exists'
MSG_USER_NOT_EXISTS = 'User {} not exists'
MSG_AUTHORIZATION_HEADER_MISSING = 'Authorization header is missing'
MSG_AUTHORIZATION_TOKEN_EXPIRED = 'Authorization token expired'
MSG_UNAUTHORIZED = 'Unauthorized'
MSG_UNSUPPORTED_CONTENT_TYPE = 'Unsupported content type {}'
MSG_UNSUPPORTED_RESPONSE_TYPE = 'Unsupported response type {}'
MSG_IMMUTABLE_FIELDS = 'There are fields that cannot be updated'
MSG_SAVE_ERROR = 'Error saving object: {}'
MSG_UPDATE_ERROR = 'Error updating object: {}'
MSG_GET_ERROR = 'Error getting object: {}'


def message(code, info):
    return {'code': code, 'message': info}


class SaveException(HTTPException):
    def __init__(self, info):
        self.code = 400
        self.data = message(400, MSG_SAVE_ERROR.format(info))
        super().__init__()


class UpdateException(HTTPException):
    def __init__(self, info):
        self.code = 400
        self.data = message(400, MSG_UPDATE_ERROR.format(info))
        super().__init__()


class GetException(HTTPException):
    def __init__(self, info):
        self.code = 400
        self.data = message(400, MSG_GET_ERROR.format(info))
        super().__init__()


class MissingRequiredFieldsException(HTTPException):
    code = 400
    data = message(400, MSG_MISSING_REQUIRED_FIELDS)


class SchemaValidationErrorException(HTTPException):
    def __init__(self, info):
        self.code = 400
        self.data = message(400, MSG_SCHEMA_VALIDATION_ERROR.format(info))
        super().__init__()


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
    code = 401
    data = message(401, MSG_AUTHORIZATION_HEADER_MISSING)


class AuthorizationTokenExpiredException(HTTPException):
    code = 401
    data = message(401, MSG_AUTHORIZATION_TOKEN_EXPIRED)


class UnauthorizedException(HTTPException):
    code = 401
    data = message(401, MSG_UNAUTHORIZED)


class UnsupportedContentTypeException(HTTPException):
    def __init__(self, content_type):
        self.code = 400
        self.data = message(400, MSG_UNSUPPORTED_CONTENT_TYPE.format(content_type))
        super().__init__()


class UnsupportedResponseTypeException(HTTPException):
    def __init__(self, accept):
        self.code = 400
        self.data = message(400, MSG_UNSUPPORTED_RESPONSE_TYPE.format(accept))
        super().__init__()


class ImmutableFieldsException(HTTPException):
    code = 400
    data = message(400, MSG_IMMUTABLE_FIELDS)
