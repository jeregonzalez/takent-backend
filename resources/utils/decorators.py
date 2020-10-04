from functools import wraps

from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_restful import abort
from jwt import ExpiredSignatureError

from resources.consts.consts import RequestHeaderKey, RequestHeaderValue, JwtKey
from resources.helpers import user_helper, enterprise_helper, offer_helper
from resources.helpers.allowed_user_helper import validate_allowed_user_not_exists, validate_allowed_user_exists
from resources.helpers.state_helper import validate_state_must_exist
from resources.helpers.user_helper import validate_password, validate_birth_date
from resources.utils import exceptions


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


def validate_user_birth_date(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        body = request.get_json()
        if 'birth_date' in body.get('user'):
            validate_birth_date(body['user']['birth_date'])
        if 'birth_date' in body:
            validate_birth_date(body['birth_date'])
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


def validate_role_is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if user_helper.get_user(user_account=get_jwt_identity().get('user_account'),
                                user_type='enterprise').role.name != 'admin':
            abort(403, message='You do not have permissions to do this action')
        return func(*args, **kwargs)

    return wrapper


def offer_id_state_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.args.get('id'):
            offer_helper.validate_offer_id_state_must_exist(id=request.args.get('id'),
                                                            user=get_jwt_identity().get('user_account'))
        return func(*args, **kwargs)

    return wrapper


def offer_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        offer_helper.validate_offer_must_exist(id=kwargs.get('id_offer'))
        return func(*args, **kwargs)

    return wrapper


def offer_must_not_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        offer_helper.validate_offer_must_not_exist(request.get_json().get('title'))
        return func(*args, **kwargs)

    return wrapper


def state_must_exist(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'state' in kwargs:
            validate_state_must_exist(state=kwargs.get('state'))
        if request.args.get('state'):
            validate_state_must_exist(state=request.args.get('state'))
        return func(*args, **kwargs)

    return wrapper


def validate_offer_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if any(key not in offer_helper.get_fields() for key, value in request.args.items()):
            abort(400, message='Any attribute in the filter is invalid')
        return func(*args, **kwargs)

    return wrapper


def allowed_user_not_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' in request.get_json():
            validate_allowed_user_not_exists(admin_user=user_helper.get_user_from_jwt(),
                                             account=request.get_json().get('account'))
        return func(*args, **kwargs)

    return wrapper


def allowed_user_exists(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'account' in request.get_json():
            validate_allowed_user_exists(admin_user=user_helper.get_user_from_jwt(),
                                         account=kwargs.get('account'))
        return func(*args, **kwargs)

    return wrapper


def role_must_be_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not user_helper.get_user_from_jwt().role.name == 'admin':
            abort(400, message='User\'s role is not admin')
        return func(*args, **kwargs)

    return wrapper
