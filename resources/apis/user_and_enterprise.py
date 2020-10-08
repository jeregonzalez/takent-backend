from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.enterprise import Enterprise
from database.models.user import EnterpriseUser, ActivationTicket
from resources.helpers import auth_helper
from resources.helpers.email_helper.email_helper import EmailActivation
from resources.utils.decorators import validate_headers, validate_user_not_exists, \
    validate_user_password
from resources.utils.exceptions import SaveException
from resources.utils.messages import Message


class UserAndEnterpriseApi(Resource):
    method_decorators = {
        'post': [validate_user_password, validate_user_not_exists, validate_headers]
    }

    def post(self):
        body = request.get_json()
        user = body.get('user')
        enterprise = body.get('enterprise')
        if not user or not enterprise:
            abort(400, message='User and enterprise needed')
        if user.get('password'):
            user['password'] = auth_helper.hash_password(user['password'])
        try:
            new_user = EnterpriseUser(**user)
            new_user.validate()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)

        enterprise['admin_user'] = new_user
        try:
            new_enterprise = Enterprise(**enterprise)
            new_enterprise.validate()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)

        new_user.save()
        new_enterprise.save()
        activation_ticket = ActivationTicket(account=new_user.account, user_type='enterprise').save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()
        return Message.created()
