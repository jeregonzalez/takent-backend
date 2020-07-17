from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from database.models.users import CommonUser, EnterpriseUser
from database.models.roles import Role

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


def validate_user_exists():
    user_type = get_jwt_identity().get('user_type')
    user_account = get_jwt_identity().get('user_account')
    state_name = 'active'
    exist = (bool(USER_TYPES[user_type].objects(account=user_account).count()) and
             USER_TYPES[user_type].objects.get(account=user_account).state.name == state_name)
    if not exist:
        abort(400, message='User {} does not exist'.format(user_account))


def validate_user_not_exists(user_account=None):
    exist = (bool(USER_TYPES['common'].objects(account=user_account).count()) and
             USER_TYPES['common'].objects.get(account=user_account).state.name == 'active') or \
            (bool(USER_TYPES['enterprise'].objects(account=user_account).count()) and
             USER_TYPES['enterprise'].objects.get(account=user_account).state.name == 'active')

    if exist:
        abort(400, message='User {} already exists'.format(user_account))


def get_user(user_type=None, user_account=None):
    if not user_type or not user_account:
        user_type = get_jwt_identity().get('user_type')
        user_account = get_jwt_identity().get('user_account')
    return USER_TYPES[user_type].objects.get(account=user_account)


def get_user_type(user_account):
    if CommonUser.objects(account=user_account).count() and \
            CommonUser.objects.get(account=user_account).state.name == 'active':
        return 'common'
    if EnterpriseUser.objects(account=user_account).count() and \
            EnterpriseUser.objects.get(account=user_account).state.name == 'active':
        return 'enterprise'
    return None


def validate_enterprise_user_exist(user_account):
    """
    Método que valida que el usuario administrador exista, que sea usuario empresa y administrador
    :param user_account: el email (account) del usuario
    """
    # Valido que exista el usuario y que esté activo
    exist = (bool(EnterpriseUser.objects(account=user_account).count()) and
             EnterpriseUser.objects.get(account=user_account).state.name == 'active')

    if not exist:
        abort(400, message='User {} not exists'.format(user_account))

    is_admin = EnterpriseUser.objects(account=user_account, role=Role.objects.get(name='admin')).count()

    if not is_admin:
        abort(400, message='User {} is not admin'.format(user_account))
