from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from database.models.users import CommonUser, EnterpriseUser

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


def validate_user_exists():
    user_type = get_jwt_identity().get('user_type')
    user_account = get_jwt_identity().get('user_account')
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if not exist:
        abort(400, message='User {} does not exist'.format(user_account))


def validate_user_not_exists(user_account=None):
    exist = bool(USER_TYPES['common'].objects(account=user_account).count()) or \
            bool(USER_TYPES['enterprise'].objects(account=user_account).count())
    if exist:
        abort(400, message='User {} already exists'.format(user_account))


def get_user():
    user_type = get_jwt_identity().get('user_type')
    user_account = get_jwt_identity().get('user_account')
    return USER_TYPES[user_type].objects.get(account=user_account)


def get_user_type(user_account):
    if CommonUser.objects(account=user_account).count():
        return 'common'
    if EnterpriseUser.objects(account=user_account).count():
        return 'enterprise'
    return None
