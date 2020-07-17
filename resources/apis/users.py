from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.common import Image, State, ActivationTicket, CurriculumVitae
from database.models.enterprise import Enterprise
from database.models.roles import Role
from database.models.users import EnterpriseUser
from resources.helpers import password_helper
from resources.helpers.auth_helper import hash_password
from resources.helpers.email_helper.email_helper import EmailAdmin, EmailActivation, EmailChangePassword
from resources.helpers.log_helper import LOGGER
from resources.helpers.user_helper import get_user, USER_TYPES, get_user_type
from resources.utils.decorators import validate_headers, authentication_required, user_must_not_exist, \
    user_must_exist, user_must_be_common
from resources.utils.exceptions import MissingRequiredFieldsException, SchemaValidationErrorException, \
    UserNotExistsException


class UserApi(Resource):
    method_decorators = {
        'get': [user_must_exist, authentication_required, validate_headers],
        'post': [user_must_not_exist, validate_headers],
        'put': [user_must_exist, authentication_required, validate_headers],
        'delete': [user_must_exist, authentication_required, validate_headers]
    }

    def get(self, user_type=None):
        return get_user()

    def post(self, user_type=None):
        body = request.get_json()
        if body.get('password'):
            body['password'] = hash_password(body['password'])
        try:
            new_user = USER_TYPES[user_type](**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        activation_ticket = ActivationTicket(account=new_user.account, user_type=user_type)
        activation_ticket.save()
        LOGGER.info(activation_ticket.id)
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()
        return {'message': 'User {} created successfully'.format(new_user.account)}, 201

    def put(self, user_type=None):
        body = request.get_json()
        get_user().update(**body)
        return '', 204

    def delete(self, user_type=None):
        user = get_user()
        if get_user_type(user.account) == 'common':
            user.update(state=State.objects.get(name='inactive'))
        elif user.role == Role.objects.get(name='member'):
            user.update(state=State.objects.get(name='inactive'))
        else:
            user.update(state=State.objects.get(name='inactive'))
            ent = Enterprise.objects.get(admin_user=user.account)

            for member in ent.member_users:
                if member.state.name == 'inactive':
                    continue
                EnterpriseUser.objects.get(account=member.account).update(
                    state=State.objects.get(name='inactive'))

            def send_emails():
                for mb in ent.member_users:
                    email = EmailAdmin(destination_email=mb.account)
                    email.send_email()

            email_process = Thread(target=send_emails)
            email_process.start()
            ent.update(state=State.objects.get(name='inactive'))

        return '', 204


class ImageApi(Resource):
    method_decorators = {
        'get': [user_must_exist, user_must_be_common, authentication_required, validate_headers],
        'post': [user_must_exist, user_must_be_common, authentication_required, validate_headers],
        'delete': [user_must_exist, user_must_be_common, authentication_required, validate_headers]
    }

    def get(self):
        user = get_user()
        if not user.profile_photo:
            return {'message': 'User {} does not have profile photo'.format(user.account)}, 200
        return {'profile_photo': user.profile_photo.base64}, 200

    def post(self):
        profile_photo = request.get_json().get('profile_photo')
        if not profile_photo:
            abort(400, message='No image sent')
        user = get_user()
        new_image = Image(base64=profile_photo)
        new_image.save()
        user.update(profile_photo=new_image)
        return {'message': 'Profile photo uploaded successfully'}, 201

    def delete(self):
        user = get_user()
        user.profile_photo.delete()
        user.save()
        return '', 204


class CurriculumApi(Resource):
    method_decorators = {
        'get': [user_must_exist, user_must_be_common, authentication_required, validate_headers],
        'post': [user_must_exist, user_must_be_common, authentication_required, validate_headers],
        'delete': [user_must_exist, user_must_be_common, authentication_required, validate_headers]
    }

    def get(self):
        user = get_user()
        if not user.curriculum:
            return {'message': 'User {} does not have curriculum'.format(user.account)}, 200
        return {'curriculum': user.curriculum.base64}, 200

    def post(self):
        curriculum = request.get_json().get('curriculum')
        if not curriculum:
            abort(400, message='No curriculum sent')
        user = get_user()
        new_curriculum = CurriculumVitae(base64=curriculum)
        new_curriculum.save()
        user.update(curriculum=new_curriculum)
        return {'message': 'Curriculum uploaded successfully'}, 201

    def delete(self):
        user = get_user()
        user.curriculum.delete()
        user.save()
        return '', 204


class PasswordRecoverApi(Resource):

    method_decorators = {
        'post': [validate_headers]
    }

    def post(self):
        body = request.get_json()
        user_account = body.get('account')
        if not user_account:
            raise MissingRequiredFieldsException
        user_type = get_user_type(user_account=user_account)
        if not user_type:
            raise UserNotExistsException(user_account)
        new_password = password_helper.get_random_alphanumeric_string(10)
        user = get_user(user_type=user_type, user_account=user_account)
        user.update_password(new_password=hash_password(new_password))
        Thread(target=lambda: EmailChangePassword(destination_email=user_account,
                                                  new_password=new_password).send_email()).start()
        return {'message': 'New password generated'}, 200


class ChangePasswordApi(Resource):

    method_decorators = {
        'post': [user_must_exist, authentication_required, validate_headers]
    }

    def post(self):
        body = request.get_json()
        new_password = body.get('new_password')
        if not new_password:
            raise MissingRequiredFieldsException
        new_password = hash_password(new_password)
        get_user().update_password(new_password=new_password)
        return {'message': 'Password changed correctly'}, 200


class UserExistsValidationApi(Resource):

    def get(self):
        user_account = request.args.get('account')
        if not user_account:
            abort(400, message='Param account is needed')
        exists = bool(get_user_type(user_account=user_account))
        return {'exists': exists}, 200


class ActivateAccountApi(Resource):
    method_decorators = {
        'post': [validate_headers]
    }

    # TODO Temporalmente, la request va a ser un get cuya URL se va a adjuntar en el mail de activación
    def get(self):
        # activation_ticket = request.get_json().get('ticket')
        activation_ticket = request.args.get('ticket')
        if not activation_ticket:
            abort(400, message='Enter a ticket')
        if not ActivationTicket.objects(id=activation_ticket).count():
            abort(400, message='Ticket {} does not exist'.format(activation_ticket))
        ticket = ActivationTicket.objects.get(id=activation_ticket)
        LOGGER.info(ticket)
        user = get_user(user_type=ticket.user_type, user_account=ticket.account)
        user.activate()
        ticket.delete()
        return {'message': 'Account {} activated'.format(user.account)}, 200
