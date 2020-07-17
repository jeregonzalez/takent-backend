from database.models.enterprise import Enterprise
from database.models.users import EnterpriseUser, CommonUser
from flask_jwt_extended import get_jwt_identity
from flask_restful import abort

from resources.helpers.log_helper import LOGGER


def validate_enterprise_must_exists():
    user_account = get_jwt_identity().get('user_account')
    if not Enterprise.objects(admin_user=user_account).count():
        abort(400, message='Enterprise with account {} does not exist'.format(user_account))


def validate_state_active_enterprise():
    user_account = get_jwt_identity().get('user_account')
    if not Enterprise.objects.get(admin_user=user_account).state.name == 'active':
        abort(400, message='Enterprise is inactive')


def validate_enterprise_must_not_exists(user_account):
    if Enterprise.objects(admin_user=user_account).count():
        abort(400, message='Enterprise with account {} exist'.format(user_account))


def validate_user_member_exist(list_accounts):
    accounts_common = []
    accounts = []  # Lista de todas las cuentas que pueden no existir
    message = ''  # El mensaje a retornar en caso de que algún usuario no exista
    message_common = ''

    for account in list_accounts:
        if CommonUser.objects(account=account).count():
            accounts_common.append(account)
        if not EnterpriseUser.objects(account=account).count():
            accounts.append(account)
    if accounts_common:
        if len(accounts) > 1:
            message = 'Users '
            for item in accounts:
                if item == accounts[len(accounts) - 1]:
                    message = message + '{} '.format(item)

                else:
                    message = message + '{} '.format(item + ',')
        else:
            message = 'User '
            for item in accounts:
                message = message + '{} '.format(item)

        if len(accounts) > 1:
            message = message + 'not exists'
        else:
            message = message + 'not exist'

    if accounts:
        if len(accounts) > 1:
            message = 'Users '
            for item in accounts:
                if item == accounts[len(accounts) - 1]:
                    message = message + '{} '.format(item)

                else:
                    message = message + '{} '.format(item + ',')
        else:
            message = 'User '
            for item in accounts:
                message = message + '{} '.format(item)

        if len(accounts) > 1:
            message = message + 'not exists'
        else:
            message = message + 'not exist'

        abort(400, message=message)


def validate_role_member(list_member_users):
    message = ''
    list_account = []

    for account in list_member_users:
        if EnterpriseUser.objects.get(account=account).role.name != 'member':
            list_account.append(account)

    if len(list_account) == 0:
        return
    elif len(list_account) == 1:
        message = 'User {}'.format(list_account[0]) + ' is not member'
        abort(400, message=message)
    else:
        message = 'Users '
        for item in list_account:
            if item == list_account[len(list_account) - 1]:
                message = message + item
            else:
                message = message + '{}'.format(item + ', ')

        message = message + 'are not member'
        abort(400, message=message)


def validate_member_must_not_exist(user_members):
    if not user_members:
        return

    ok = True
    existing_members = []
    repetition = []
    repetition_flag = True

    for us in user_members:
        if repetition_flag:
            repetition.append(us.get('account'))
        else:
            if us.get('account') in repetition:
                abort(400, message='The users are repeated')
            else:
                repetition.append(us.get('account'))
        repetition_flag = False

        if EnterpriseUser.objects(account=us.get('account')).count():
            existing_members.append(us.get('account'))
            ok = False

    if not ok:
        abort(400, message='The users {} already exists'.format(', '.join(existing_members)))


"""
def validate_type_member_user(list_accounts):
"""
