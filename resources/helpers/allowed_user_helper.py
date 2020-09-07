from flask_restful import abort

from database.models.enterprise import Enterprise


def validate_allowed_user_not_exists(admin_user, account):
    if Enterprise.objects(admin_user=admin_user, member_users=account).count():
        abort(400, message='User does exist')


def validate_allowed_user_exists(admin_user, account):
    if not Enterprise.objects(admin_user=admin_user, member_users=account).count():
        abort(400, message='User does not exist')