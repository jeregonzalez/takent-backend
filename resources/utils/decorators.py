from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restful import abort
from jwt import ExpiredSignatureError

from resources.consts.consts import RequestHeaderKey, RequestHeaderValue, JwtKey
from resources.helpers import user_helper, enterprise_helper, offer_helper, postulant_helper, service_helper
from resources.helpers.user_helper import validate_password
from resources.utils import exceptions
from resources.utils.messages import Message


def validate_headers(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        content_type = request.headers.get(RequestHeaderKey.CONTENT_TYPE)
        accept = request.headers.get(RequestHeaderKey.ACCEPT)
        if content_type and content_type not in [RequestHeaderValue.APPLICATION_JSON,
                                                 RequestHeaderValue.APPLICATION_ANY]:
            raise exceptions.UnsupportedContentTypeException(content_type)
        if accept and accept not in [RequestHeaderValue.APPLICATION_JSON, RequestHeaderValue.APPLICATION_ANY]:
            raise exceptions.UnsupportedResponseTypeException(accept)
        return func(*args, **kwargs)

    return wrapper


def authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.headers.get(RequestHeaderKey.AUTHORIZATION):
            raise exceptions.AuthorizationHeaderMissingException
        try:
            verify_jwt_in_request()
        except ExpiredSignatureError:
            raise exceptions.AuthorizationTokenExpiredException
        except Exception:
            raise exceptions.UnauthorizedException
        return func(*args, **kwargs)

    return wrapper


def validate_user_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not get_jwt_identity():
            body = request.get_json()
            user_account = body.get('account')
            user_type = body.get('user_type')
        else:
            user_account, user_type = get_jwt_identity().get(JwtKey.USER_ACCOUNT), \
                                      get_jwt_identity().get(JwtKey.USER_TYPE)
        if not user_helper.user_exists(user_account=user_account, user_type=user_type):
            abort(400, message='User {} not exists'.format(user_account))
        return func(*args, **kwargs)

    return wrapper


def validate_user_not_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.get_json().get('user'):
            user_account = request.get_json().get('user').get('account')
        else:
            user_account = request.get_json().get('account')
        if user_helper.user_exists(user_account=user_account):
            abort(400, message='User {} already exists'.format(user_account))
        return func(*args, **kwargs)

    return wrapper


def validate_user_is_enterprise(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt_identity().get('user_type') != 'enterprise':
            abort(400, message='User type must be enterprise')
        return func(*args, **kwargs)

    return wrapper


def validate_user_is_common(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_jwt_identity().get('user_type') != 'common':
            abort(400, message='User type must be common')
        return func(*args, **kwargs)

    return wrapper


def validate_enterprise_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = get_jwt_identity().get('user_account')
        if not enterprise_helper.enterprise_exists(user_account=user_account):
            abort(400, message='User {} does not have an enterprise associated'.format(user_account))
        return func(*args, **kwargs)

    return wrapper


def validate_enterprise_not_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = get_jwt_identity().get('user_account')
        if enterprise_helper.enterprise_exists(user_account=user_account):
            abort(400, message='User {} already has an enterprise associated'.format(user_account))
        return func(*args, **kwargs)

    return wrapper


def validate_offer_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('id_offer') and not offer_helper.offer_exists(_id=kwargs.get('id_offer')):
            return Message.bad_request(message='Offer {} not exists'.format(kwargs.get('id_offer')))
        return func(*args, **kwargs)
    return wrapper


def validate_postulant_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('id_postulant') and not postulant_helper.postulant_exists(_id=kwargs.get('id_postulant')):
            return Message.bad_request(message='Postulant {} not exists'.format(kwargs.get('id_postulant')))
        return func(*args, **kwargs)
    return wrapper


def validate_user_password(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        body = request.get_json()
        if body.get('user'):
            if 'password' in body.get('user'):
                validate_password(body['user']['password'])
            if 'member_users' in body.get('enterprise'):
                for member in body['enterprise']['member_users']:
                    if 'password' in member:
                        validate_password(member.get('password'))
        if 'password' in body:
            validate_password(body['password'])
        if 'new_password' in body:
            validate_password(body['new_password'])
        if 'member_users' in body:
            for member in body['member_users']:
                if 'password' in member:
                    validate_password(member.get('password'))

        return func(*args, **kwargs)

    return wrapper


def validate_member_user_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        permission = get_jwt_identity().get('permission')
        if permission == 'admin':
            member_user_account = kwargs.get('account')
        else:
            member_user_account = get_jwt_identity().get('user_account')
        if not member_user_account:
            abort(400, message='Missing member user account')
        if not user_helper.user_exists(user_account=member_user_account, user_type='enterprise'):
            abort(400, message='User {} not exists'.format(member_user_account))
        return func(*args, **kwargs)

    return wrapper


def validate_permission_is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        permission = get_jwt_identity().get('permission')
        if permission != 'admin':
            abort(403, message='Unauthorized')
        return func(*args, **kwargs)

    return wrapper


def validate_service_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('service_id') and not service_helper.service_exists(_id=kwargs.get('service_id')):
            return Message.bad_request(message='Service {} not exists'.format(kwargs.get('service_id')))
        return func(*args, **kwargs)

    return wrapper
