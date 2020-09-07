from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.common import State
from database.models.enterprise import Enterprise
from database.models.role import Role
from database.models.user import EnterpriseUser
from resources.helpers import user_helper, auth_helper
from resources.utils.decorators import authentication_required, validate_headers, validate_enterprise_exists, \
    validate_user_password, allowed_user_not_exists, allowed_user_exists, role_must_be_admin
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException
from resources.utils.messages import Message


class AllowedUserApi(Resource):
    method_decorators = {
        'get': [role_must_be_admin, authentication_required, validate_headers],
        'post': [role_must_be_admin, validate_user_password, allowed_user_not_exists,
                 validate_enterprise_exists, authentication_required, validate_headers],
        'put': [allowed_user_exists, authentication_required, validate_headers],
        'delete': [authentication_required, validate_headers]
    }

    def get(self):
        if not request.args.get('account'):
            if not Enterprise.objects(admin_user=user_helper.get_user_from_jwt()).count():
                abort(400, message='Admin user not exists')
            return Message.ok(response=[user for user in Enterprise.objects.get(
                admin_user=user_helper.get_user_from_jwt()).member_users])

        member_users = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).member_users
        return Message.ok([user for user in set(member_users).intersection(
            set(EnterpriseUser.objects(account__icontains=request.args.get('account'))))])

    def post(self):
        body = request.get_json()
        try:
            if not 'role' in body:
                body['role'] = Role.objects.get(name='member')

            if 'password' in body:
                body['password'] = auth_helper.hash_password(body['password'])

            body['state'] = State.objects.get(name='active')
            user = EnterpriseUser(**body).save()
            Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).update(push__member_users=user)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.added(user.name)

    def put(self, account):
        body = request.get_json()
        try:
            if not 'role' in body:
                body['role'] = Role.objects.get(name='member')

            if not account:
                abort(400, message='Field account is empty')

            if user_helper.get_user_from_jwt().role.name == 'member':
                EnterpriseUser.objects.get(account=user_helper.get_user_from_jwt().account).update(**body)

            else:
                if not EnterpriseUser.objects(account=account).count():
                    abort(400, message='User does not exists')
                EnterpriseUser.objects.get(account=account).update(**body)

        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.update()

    def delete(self, account):
        enterprise_user = None
        if user_helper.get_user_from_jwt().role.name == 'member':
            enterprise_user = user_helper.get_user_from_jwt()
            Enterprise.objects.get(member_users=enterprise_user).update(pull__member_users=enterprise_user)

        else:
            if not EnterpriseUser.objects(account=account).count():
                abort(400, message='User does not exits')

            enterprise_user = EnterpriseUser.objects.get(account=account)
            Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).update(
                pull__member_users=enterprise_user)

        enterprise_user.delete()
        return Message.delete()
