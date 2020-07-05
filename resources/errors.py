from werkzeug.exceptions import HTTPException


class SchemaValidationError(HTTPException):
    pass


class AccountAlreadyExistsError(HTTPException):
    pass


errors = {
    'SchemaValidationError': {
        'message': 'Request is missing required fields',
        'status': 400
    },
    'AccountAlreadyExistsError': {
        'message': 'Account already exists',
        'status': 400
    }
}
