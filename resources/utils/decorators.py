from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restful import abort
from jwt import ExpiredSignatureError

from database.models.common import State
from resources.helpers.enterprise_helper import validate_enterprise_must_exists, validate_enterprise_must_not_exists, \
    validate_user_member_exist, validate_state_active_enterprise, validate_role_member, validate_member_must_not_exist
from resources.helpers.state_helper import validate_state_exist
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


def enterprise_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_enterprise_must_exists()
        return func(*args, **kwargs)

    return wrapper


def enterprise_state_must_active(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_state_active_enterprise()
        return func(*args, **kwargs)

    return wrapper


def enterprise_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = get_jwt_identity().get('user_account')
        validate_enterprise_must_not_exists(user_account)
        return func(*args, **kwargs)

    return wrapper


def user_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_user_exists()
        return func(*args, **kwargs)

    return wrapper


def user_members_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_members = request.get_json().get('member_users')
        if not user_members:
            return func(*args, **kwargs)
        validate_member_must_not_exist(user_members)
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


def user_member_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'member_users' in request.get_json():
            list_accounts = request.get_json().get('member_users')
            validate_user_member_exist(list_accounts)
        # validate_type_member_user(list_accounts)
        return func(*args, **kwargs)

    return wrapper


def role_must_be_member(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'member_users' in request.get_json():
            list_member_users = request.get_json().get('member_users')
            validate_role_member(list_member_users)
        return func(*args, **kwargs)

    return wrapper


def user_must_be_enterprise(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt_identity().get('user_type') != 'enterprise':
            abort(400, message='User must be enterprise user')

        return func(*args, **kwargs)

    return wrapper


def user_must_be_common(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt_identity().get('user_type') != 'common':
            abort(400, message='User must be common')
        return func(*args, **kwargs)

    return wrapper


def state_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'state' in request.get_json():
            validate_state_exist(request.get_json().get('state'))
            request.get_json()['state'] = State.objects.get(name=request.get_json().get('state'))

        return func(*args, **kwargs)

    return wrapper
