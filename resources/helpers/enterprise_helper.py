from database.models.enterprise import Enterprise

from resources.helpers import user_helper


def enterprise_exists(user_account):
    user = user_helper.get_user(user_account=user_account, user_type='enterprise')
    if user.role.name == 'admin':
        exist = bool(Enterprise.objects(admin_user=user.account).count())
    else:
        exist = bool(Enterprise.objects(member_users=user.account).count())
    return exist


def get_enterprise(user_account=None):
    if user_account:
        user = user_helper.get_user(user_account=user_account, user_type='enterprise')
    else:
        user = user_helper.get_user_from_jwt()
    if user.role.name == 'admin':
        enterprise = Enterprise.objects.get(admin_user=user.account)
    else:
        enterprise = Enterprise.objects.get(member_users=user.account)
    return enterprise
