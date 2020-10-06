from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.common import Image
from database.models.common_user import UserCurriculumVitae
from database.models.parametric_docs import State
from database.models.user import EnterpriseUser, CommonUser, ActivationTicket
from resources.helpers import password_helper, user_helper, enterprise_helper, auth_helper
from resources.helpers.email_helper.email_helper import EmailAdmin, EmailActivation, \
    EmailChangePassword
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_is_common, \
    validate_user_exists, validate_user_not_exists, validate_user_password
from resources.utils.exceptions import MissingRequiredFieldsException, \
    SchemaValidationErrorException


class UserApi(Resource):
    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_not_exists, validate_user_password, validate_headers],
        'put': [validate_user_exists, validate_user_password, authentication_required, validate_headers],
        'delete': [validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, user_type=None):
        return user_helper.get_user_from_jwt()

    def post(self, user_type=None):
        body = request.get_json()
        if body.get('password'):
            body['password'] = auth_helper.hash_password(body['password'])

        try:
            new_user = user_helper.USER_TYPES[user_type](**body)
            if not 'birth_date' in body:
                if type(new_user) == EnterpriseUser:
                    if 'member' != new_user.role.name:
                        raise SchemaValidationErrorException
                else:
                    raise SchemaValidationErrorException

            new_user.save()

        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        activation_ticket = ActivationTicket(account=new_user.account, user_type=user_type).save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()
        return {'message': 'User {} created successfully'.format(new_user.account)}, 201

    def put(self, user_type=None):
        body = request.get_json()
        user_helper.get_user_from_jwt().update(**body)
        return '', 204

    def delete(self, user_type=None):
        user = user_helper.get_user_from_jwt()
        user.update(state=State.objects.get(name='inactive'))
        if isinstance(user, EnterpriseUser) and user.role.name == 'admin':
            if not enterprise_helper.enterprise_exists(user_account=user.account):
                return '', 204
            enterprise = enterprise_helper.get_enterprise(user_account=user.account)
            enterprise.deactivate()

            def send_emails():
                for member_user in enterprise.member_users:
                    EmailAdmin(destination_email=member_user.account).send_email()

            Thread(target=send_emails).start()
        return '', 204


class ImageApi(Resource):
    method_decorators = {
        'get': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        user = user_helper.get_user_from_jwt()
        if not user.profile_photo:
            return {'message': 'User {} does not have profile photo'.format(user.account)}, 200
        return {'profile_photo': user.profile_photo.base64}, 200

    def post(self):
        profile_photo = request.get_json().get('profile_photo')
        if not profile_photo:
            abort(400, message='No image sent')
        user = user_helper.get_user_from_jwt()
        user.profile_photo.delete()
        new_image = Image(base64=profile_photo).save()
        user.update(profile_photo=new_image)
        return {'message': 'Profile photo uploaded successfully'}, 201

    def delete(self):
        user = user_helper.get_user_from_jwt()
        user.profile_photo.delete()
        user.save()
        return '', 204


class CurriculumApi(Resource):
    method_decorators = {
        'get': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        user = user_helper.get_user_from_jwt()
        if not user.curriculum:
            return {'message': 'User {} does not have curriculum'.format(user.account)}, 200
        return user.curriculum, 200

    def post(self):
        body = request.get_json()
        user = user_helper.get_user_from_jwt()
        try:
            new_curriculum = UserCurriculumVitae(**body)
            new_curriculum.save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        user.update(curriculum=new_curriculum)
        return {'message': 'Curriculum uploaded successfully'}, 201

    def delete(self):
        user = user_helper.get_user_from_jwt()
        user.curriculum.delete()
        user.save()
        return '', 204


class PasswordRecoverApi(Resource):
    method_decorators = {
        'post': [validate_user_exists, validate_headers]
    }

    def post(self):
        body = request.get_json()
        user_account = body.get('account')
        if not user_account:
            raise MissingRequiredFieldsException
        new_password = password_helper.get_random_alphanumeric_string(10)
        user = user_helper.get_user(user_account=user_account)
        user.update_password(new_password=auth_helper.hash_password(new_password))
        Thread(target=lambda: EmailChangePassword(destination_email=user_account,
                                                  new_password=new_password).send_email()).start()
        return {'message': 'New password generated'}, 200


class ChangePasswordApi(Resource):
    method_decorators = {
        'post': [validate_user_exists, validate_user_password, authentication_required, validate_headers]
    }

    def post(self):
        body = request.get_json()
        new_password = body.get('new_password')
        if not new_password:
            raise MissingRequiredFieldsException
        new_password = auth_helper.hash_password(new_password)
        user_helper.get_user_from_jwt().update_password(new_password=new_password)
        return {'message': 'Password changed correctly'}, 200


class UserExistsValidationApi(Resource):
    def get(self):
        user_account = request.args.get('account')
        if not user_account:
            abort(400, message='Param account is needed')
        return {'exists': user_helper.user_exists(user_account=user_account)}, 200


class ActivateAccountApi(Resource):
    method_decorators = {
        'post': [validate_headers]
    }

    # TODO Temporalmente, la request va a ser un get cuya URL se va a adjuntar en el mail de activación
    def get(self):
        # activation_ticket = request.get_json().get('ticket')
        activation_ticket = request.args.get('ticket')
        if not activation_ticket:
            abort(400, message='Ticket required')
        if not ActivationTicket.objects(id=activation_ticket).count():
            abort(400, message='Ticket {} not exists'.format(activation_ticket))
        ticket = ActivationTicket.objects.get(id=activation_ticket)
        user = user_helper.get_user(user_type=ticket.user_type, user_account=ticket.account)
        user.activate()
        ticket.delete()
        return {'message': 'Account {} activated'.format(user.account)}, 200


class UserAttributesListApi(Resource):
    method_decorators = {
        'get': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'put': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, attribute_name, _id=None):
        user = user_helper.get_user_from_jwt()
        if not hasattr(user, attribute_name):
            abort(400, message='Attribute {} not exists'.format(attribute_name))
        attribute_list = getattr(user, attribute_name)
        if _id:
            try:
                attribute_list = attribute_list.get(id=_id)
            except DoesNotExist:
                attribute_list = []
        return attribute_list, 200

    def post(self, attribute_name, _id=None):
        user = user_helper.get_user_from_jwt()
        body = request.get_json()
        if not hasattr(user, attribute_name):
            abort(400, message='Attribute {} not exists'.format(attribute_name))
        attribute_list = getattr(user, attribute_name)
        attribute_list.create(**body)
        attribute_list.save()
        return {'message': '{} added successfully'.format(attribute_name)}, 201

    def put(self, attribute_name, _id=None):
        user = user_helper.get_user_from_jwt()
        body = request.get_json()
        if not hasattr(user, attribute_name):
            abort(400, message='Attribute {} not exists'.format(attribute_name))
        if not _id:
            abort(400, message='Object id needed')
        attribute_list = getattr(user, attribute_name)
        attribute_element = None
        try:
            attribute_element = attribute_list.get(id=_id)
        except DoesNotExist:
            abort(400, message='{} with id {} not exists'.format(attribute_name, _id))
        for key, value in body.items():
            setattr(attribute_element, key, value)
        try:
            attribute_element.validate()
        except ValidationError:
            raise SchemaValidationErrorException
        attribute_list.save()
        return '', 204

    def delete(self, attribute_name, _id=None):
        user = user_helper.get_user_from_jwt()
        if not hasattr(user, attribute_name):
            abort(400, message='Attribute {} not exists'.format(attribute_name))
        attribute_list = getattr(user, attribute_name)
        if not _id:
            abort(400, message='Object id needed')
        try:
            attribute_list.get(id=_id)
        except DoesNotExist:
            abort(400, message='{} with id {} not exists'.format(attribute_name, _id))
        delete_condition = {'pull__{}__id'.format(attribute_name): _id}
        user.update(**delete_condition)
        return '', 204
