from threading import Thread

from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.parametric_docs import Permission
from database.models.user import EnterpriseUser, ActivationTicket
from resources.helpers import user_helper, auth_helper, enterprise_helper
from resources.helpers.email_helper.email_helper import EmailActivation
from resources.utils.decorators import validate_headers, authentication_required, validate_user_password, \
    validate_user_exists, validate_user_not_exists, validate_user_is_enterprise, validate_member_user_exists, \
    validate_permission_is_admin, validate_enterprise_exists
from resources.utils.exceptions import SaveException, UpdateException
from resources.utils.messages import Message


class MemberUserApi(Resource):
    method_decorators = {
        'get': [validate_member_user_exists, validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'post': [validate_enterprise_exists, validate_user_not_exists, validate_user_password, validate_permission_is_admin,
                 validate_user_is_enterprise, validate_user_exists, authentication_required, validate_headers],
        'put': [validate_member_user_exists, validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, validate_user_password,
                authentication_required, validate_headers],
        'delete': [validate_member_user_exists, validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                   authentication_required, validate_headers]
    }

    def get(self, account=None):
        return user_helper.get_member_user(user_account=account)

    def post(self, account=None):
        body = request.get_json()
        body['permission'] = Permission.objects.get(name='member')
        if body.get('password'):
            body['password'] = auth_helper.hash_password(body['password'])
        try:
            new_user = EnterpriseUser(**body)
            new_user.save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        enterprise = enterprise_helper.get_enterprise()
        enterprise.update(push__member_users=new_user)
        activation_ticket = ActivationTicket(account=new_user.account, user_type='enterprise').save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()
        return Message.created()

    def put(self, account=None):
        body = request.get_json()
        try:
            user_helper.get_member_user(user_account=account).update(**body)
        except (FieldDoesNotExist, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, account=None):
        user = user_helper.get_member_user(user_account=account)
        enterprise = enterprise_helper.get_enterprise()
        enterprise.update(pull__member_users=user)
        user.delete()
        return Message.deleted()


class MemberUsersByEnterprise(Resource):
    method_decorators = {
        'get': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers]
    }

    def get(self):
        enterprise = enterprise_helper.get_enterprise()
        return Message.ok([user for user in enterprise.member_users])
