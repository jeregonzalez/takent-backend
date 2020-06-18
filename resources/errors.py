from werkzeug.exceptions import HTTPException


class InternalServerError(HTTPException):
    pass


class SchemaValidationError(HTTPException):
    pass


class AccountAlreadyExistsError(HTTPException):
    pass


class UnauthorizedError(HTTPException):
    pass


errors = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "AccountAlreadyExistsError": {
        "message": "User with given account already exists",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    }
}
