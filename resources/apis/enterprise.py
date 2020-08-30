from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.enterprise import Enterprise
from database.models.role import Role
from database.models.user import EnterpriseUser
from resources.helpers import user_helper, enterprise_helper, auth_helper
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_user_is_enterprise, validate_enterprise_exists, validate_enterprise_not_exists, validate_role_is_admin, \
    validate_user_password
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException


class EnterpriseApi(Resource):
    method_decorators = {
        'get': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'post': [validate_role_is_admin, validate_user_password, validate_enterprise_not_exists, validate_user_is_enterprise,
                 validate_user_exists, authentication_required, validate_headers],
        'put': [validate_role_is_admin, validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_role_is_admin, validate_enterprise_exists, validate_user_is_enterprise,
                   validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        user_account = user_helper.get_user_from_jwt(keys='user_account')
        return enterprise_helper.get_enterprise(user_account=user_account), 200

    def post(self):
        body = request.get_json()
        body['admin_user'] = user_helper.get_user_from_jwt()
        if body.get('member_users'):
            member_users = body.get('member_users')
            exist, existing_users = user_helper.users_exist(user_accounts=[member_user.get('account')
                                                                           for member_user in member_users])
            if exist:
                abort(400, message='Users {} already exist'.format(','.join(existing_users)))
            saved_users = []
            for member_user in member_users:
                member_user['password'] = auth_helper.hash_password(member_user.get('password'))
                member_user['role'] = Role.objects.get(name='member')
                saved_users.append(EnterpriseUser(**member_user).save())
            body['member_users'] = saved_users

        try:
            new_enterprise = Enterprise(**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return {'message': 'Enterprise {} created'.format(new_enterprise.business_name)}, 201

    def put(self):
        body = request.get_json()
        enterprise = enterprise_helper.get_enterprise(user_account=user_helper.get_user_from_jwt().account)
        if body.get('member_users'):
            raise SchemaValidationErrorException
        try:
            enterprise.update(**body)
        except InvalidQueryError:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return '', 204

    def delete(self):
        enterprise_helper.get_enterprise(user_account=user_helper.get_user_from_jwt().account).deactivate()
        return '', 204
