from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.common import Image, State, ActivationTicket, CurriculumVitae
from database.models.enterprise import Enterprise
from database.models.role import Role
from database.models.user import EnterpriseUser
from resources.helpers import password_helper, user_helper, enterprise_helper, auth_helper
from resources.helpers.email_helper.email_helper import EmailAdmin, EmailActivation, EmailChangePassword
from resources.helpers.enterprise_helper import enterprise_exists
from resources.utils.decorators import validate_headers, authentication_required, validate_user_is_common, \
    validate_user_exists, validate_user_not_exists, validate_user_password, validate_user_birth_date, \
    validate_enterprise_not_exists
from resources.utils.exceptions import MissingRequiredFieldsException, SchemaValidationErrorException


class AdminUserEnterpriseApi(Resource):
    method_decorators = {
        'post': [validate_user_password, validate_user_birth_date, validate_user_not_exists, validate_headers]
    }

    def post(self, user_type=None):
        body = request.get_json()
        if body.get('user').get('password'):
            body['user']['password'] = auth_helper.hash_password(body['user']['password'])

        try:
            if not 'birth_date' in body.get('user'):
                raise SchemaValidationErrorException
            if body.get('user').get('role'):
                if body.get('user').get('role') != 'admin':
                    abort(400, message='Role must be admin')
            else:
                body['user']['role'] = 'admin'
            new_user = user_helper.USER_TYPES['enterprise'](**body.get('user'))

            new_user.save()

        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        activation_ticket = ActivationTicket(account=new_user.account, user_type='enterprise').save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()

        ################Enterprise##################
        body['enterprise']['admin_user'] = EnterpriseUser.objects.get(account=new_user.account)
        if enterprise_helper.enterprise_exists(user_account=body['enterprise']['admin_user'].account):
            new_user.delete()
            abort(400, message='User {} already has an enterprise associated'.format(body['enterprise']['admin_user'].account))
        if body.get('enterprise').get('member_users'):
            member_users = body.get('enterprise').get('member_users')
            exist, existing_users = user_helper.users_exist(user_accounts=[member_user.get('account')
                                                                           for member_user in member_users])
            if exist:
                new_user.delete()
                abort(400, message='Users {} already exist'.format(','.join(existing_users)))
            saved_users = []
            for member_user in member_users:
                member_user['password'] = auth_helper.hash_password(member_user.get('password'))
                member_user['role'] = Role.objects.get(name='member')
                saved_users.append(EnterpriseUser(**member_user).save())
            body['enterprise']['member_users'] = saved_users

        try:
            new_enterprise = Enterprise(**body.get('enterprise')).save()
        except FieldDoesNotExist:
            new_user.delete()
            raise SchemaValidationErrorException
        except ValidationError:
            new_user.delete()
            raise MissingRequiredFieldsException
        except Exception:
            new_user.delete()
            abort(400)
        return {'message': 'User {} and Enterprise {} created successfully'.format(new_user.account, new_enterprise.business_name)}, 201