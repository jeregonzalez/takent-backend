from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.common import ActivationTicket
from database.models.enterprise import Enterprise
from database.models.role import Role
from database.models.user import EnterpriseUser
from resources.helpers import user_helper, auth_helper
from resources.helpers.email_helper.email_helper import EmailActivation
from resources.helpers.log_helper import LOGGER
from resources.utils.decorators import validate_headers, validate_user_not_exists, \
    validate_user_password
from resources.utils.exceptions import MissingRequiredFieldsException, \
    SchemaValidationErrorException


class AdminUserEnterpriseApi(Resource):
    method_decorators = {
        'post': [validate_user_password, validate_user_not_exists, validate_headers]
    }

    def post(self, user_type=None):
        body = request.get_json()

        if body.get('user').get('password'):
            body['user']['password'] = auth_helper.hash_password(body['user']['password'])
        try:
            if 'birth_date' not in body.get('user'):
                raise SchemaValidationErrorException
            if body.get('user').get('role'):
                if body.get('user').get('role') != 'admin':
                    abort(400, message='Role must be admin')
            else:
                body['user']['role'] = 'admin'
            new_user = user_helper.USER_TYPES['enterprise'](**body.get('user'))
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        activation_ticket = ActivationTicket(account=new_user.account, user_type='enterprise').save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()

        ################Enterprise##################
        aux = []
        if body.get('enterprise').get('member_users'):
            aux = body['enterprise']['member_users']
            exist, existing_users = user_helper.users_exist(user_accounts=[member_user.get('account')
                                                                           for member_user in aux])
            if exist:
                new_user.delete()
                abort(400, message='Users {} already exist'.format(','.join(existing_users)))
            del body['enterprise']['member_users']
        try:
            new_user.save()
            body['enterprise']['admin_user'] = new_user
            new_enterprise = Enterprise(**body.get('enterprise')).save()
            if aux:
                member_users = aux
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
                print(saved_users)
                new_enterprise.update(member_users=saved_users)
        except FieldDoesNotExist:
            new_user.delete()
            raise SchemaValidationErrorException
        except ValidationError as e:
            LOGGER.info(e)
            new_user.delete()
            raise MissingRequiredFieldsException
        except Exception:
            new_user.delete()
            abort(400)
        return {'message': 'User {} and Enterprise {} created successfully'.format(new_user.account, new_enterprise.business_name)}, 201