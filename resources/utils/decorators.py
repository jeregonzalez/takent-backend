from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restful import abort
from jwt import ExpiredSignatureError

from resources.helpers.user_helper import validate_user_exists, validate_user_not_exists, USER_TYPES
from resources.utils.exceptions import AuthorizationHeaderMissingException, AuthorizationTokenExpiredException, \
    UnauthorizedException, UnsupportedContentTypeException, UnsupportedResponseTypeException


def validate_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        content_type = request.headers.get('Content-Type')
        accept = request.headers.get('Accept')
        if content_type and not (content_type in ['application/json', '*/*']):
            raise UnsupportedContentTypeException(content_type)
        if accept and not (accept in ['application/json', '*/*']):
            raise UnsupportedResponseTypeException(accept)
        return func(*args, **kwargs)
    return wrapper


def authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.headers.get('Authorization'):
            raise AuthorizationHeaderMissingException
        try:
            verify_jwt_in_request()
        except ExpiredSignatureError:
            raise AuthorizationTokenExpiredException
        except Exception:
            raise UnauthorizedException
        return func(*args, **kwargs)
    return wrapper


def user_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_user_exists()
        return func(*args, **kwargs)
    return wrapper


def user_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_type = kwargs.get('user_type')
        if user_type not in USER_TYPES:
            abort(404)
        user_account = request.get_json().get('account')
        validate_user_not_exists(user_account=user_account)
        return func(*args, **kwargs)
    return wrapper


def user_must_be_common(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt_identity().get('user_type') != 'common':
            abort(400, message='User must be common')
        return func(*args, **kwargs)
    return wrapper
