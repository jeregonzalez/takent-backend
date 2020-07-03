from werkzeug.exceptions import HTTPException


class SchemaValidationError(HTTPException):
    pass


class AccountAlreadyExistsError(HTTPException):
    pass


errors = {
    'SchemaValidationError': {
        'message': 'Request fields are not correct',
        'status': 400
    },
    'AccountAlreadyExistsError': {
        'message': 'Account already exists',
        'status': 400
    }
}
