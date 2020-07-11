from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from jwt import ExpiredSignatureError

from resources.helpers.user_helper import validate_user_exists, validate_user_not_exists
from resources.utils.exceptions import AuthorizationHeaderMissingException, AuthorizationTokenExpiredException, \
    UnauthorizedException, UnsupportedContentTypeException, UnsupportedResponseType


def validate_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        content_type = request.headers.get('Content-Type')
        accept = request.headers.get('Accept')
        if content_type and not (content_type in ['application/json', '*/*']):
            raise UnsupportedContentTypeException(content_type)
        if accept and not (accept in ['application/json', '*/*']):
            raise UnsupportedResponseType(accept)
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


def common_user_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = get_jwt_identity()
        validate_user_exists(user_type='common', user_account=user_account)
        return func(*args, **kwargs)
    return wrapper


def common_user_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = request.get_json().get('account')
        validate_user_not_exists(user_type='common', user_account=user_account)
        return func(*args, **kwargs)
    return wrapper


def enterprise_user_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = get_jwt_identity()
        validate_user_exists(user_type='enterprise', user_account=user_account)
        return func(*args, **kwargs)
    return wrapper


def enterprise_user_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = request.get_json().get('account')
        validate_user_not_exists(user_type='enterprise', user_account=user_account)
        return func(*args, **kwargs)
    return wrapper


def user_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = request.get_json().get('account')
        validate_user_not_exists(user_type='enterprise', user_account=user_account)
        validate_user_not_exists(user_type='common', user_account=user_account)
        return func(*args, **kwargs)
    return wrapper
