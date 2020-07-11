from flask_restful import abort

from database.models.users import CommonUser, EnterpriseUser

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


def validate_user_exists(user_type, user_account):
    if not user_account:
        abort(400, message='You must enter an user')
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if not exist:
        abort(400, message='User {} does not exist'.format(user_account))


def validate_user_not_exists(user_type, user_account):
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if exist:
        abort(400, message='User {} already exists'.format(user_account))
