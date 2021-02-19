import re

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort
from mongoengine import DoesNotExist

from database.models.user import CommonUser, EnterpriseUser
from resources.consts.consts import JwtKey

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


def user_exists(user_account, user_type=None):
    if not user_type:
        user_type = ['common', 'enterprise']
    if isinstance(user_type, str):
        user_type = [user_type]
    exist = any(USER_TYPES[user_type].objects(account=user_account).count() for user_type in user_type)
    return exist


def users_exist(user_accounts, user_type=None):
    if not user_type:
        user_type = ['common', 'enterprise']
    if isinstance(user_type, str):
        user_type = [user_type]
    existing_accounts = []
    for user_account in user_accounts:
        if any(USER_TYPES[user_type].objects(account=user_account).count() for user_type in user_type):
            existing_accounts.append(user_account)
    if existing_accounts:
        return True, existing_accounts
    else:
        return False, []


def get_user(user_account, user_type=None, fail_ok=False):
    if not user_type:
        user_type = 'common' if USER_TYPES['common'].objects(account=user_account).count() else 'enterprise'
    user = None
    try:
        user = USER_TYPES[user_type].objects.get(account=user_account)
    except DoesNotExist as e:
        if not fail_ok:
            raise e
    return user


def get_user_from_jwt(keys=None):
    user_data = get_jwt_identity()
    if not user_data:
        return None
    if keys:
        if isinstance(keys, str):
            return user_data.get(keys)
        return {key: user_data.get(key) for key in keys}
    return USER_TYPES[user_data.get(JwtKey.USER_TYPE)].objects.get(account=user_data.get(JwtKey.USER_ACCOUNT))


def validate_password(password=None):
    if password:
        result = re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,15}$", password)

        if not result:
            abort(400, message='Password is invalid')


def get_member_user(user_account=None):
    return get_user(user_account=user_account, user_type='enterprise') if user_account else get_user_from_jwt()


def calculate_average_score(user):
    from database.models.service import Service
    services = Service.objects(publication_user=user)
    total_score = 0
    score_count = 0
    for service in services:
        for service_request in service.service_requests:
            if service_request.score:
                total_score += service_request.score
                score_count += 1
    return total_score/score_count if score_count else 0
