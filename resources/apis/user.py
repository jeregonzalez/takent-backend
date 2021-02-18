from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.common import Image
from database.models.common_user import UserCurriculumVitae
from database.models.offer import Offer
from database.models.parametric_docs import StateUser, StateService, StateOffer, Permission
from database.models.service import Service
from database.models.user import ActivationTicket, CommonUser, RecoveryTicket, EnterpriseUser
from resources.helpers import password_helper, user_helper, auth_helper, enterprise_helper
from resources.helpers.email_helper.email_helper import EmailActivation, \
    EmailChangePassword, EmailRecovery
from resources.helpers.notifications_helper import SuggestRegisterNewMemberNotification
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_is_common, validate_user_exists, validate_user_not_exists, validate_user_password, \
    validate_user_is_enterprise, validate_permission_is_admin
from resources.utils.exceptions import MissingRequiredFieldsException, \
    SchemaValidationErrorException, SaveException, UpdateException, GetException
from resources.utils.messages import Message


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
            new_user.save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        activation_ticket = ActivationTicket(account=new_user.account, user_type=user_type).save()
        Thread(target=lambda: EmailActivation(destination_email=new_user.account,
                                              ticket_hash=activation_ticket.id).send_email()).start()
        return Message.created()

    def put(self, user_type=None):
        body = request.get_json()
        try:
            user_helper.get_user_from_jwt().update(**body)
        except (FieldDoesNotExist, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, user_type=None):
        user = user_helper.get_user_from_jwt()
        user.update(state=StateUser.objects.get(name='deleted'))
        if isinstance(user, CommonUser):
            finished = StateService.objects.get(name='finished')
            services = Service.objects(publication_user=user, state=StateService.objects.get(name='active'))
            for service in services:
                service.update(state=finished)
        elif user.permission.name == 'admin':
            enterprise = enterprise_helper.get_enterprise(user_account=user.account)
            finished = StateOffer.objects.get(name='finished')
            offers = Offer.objects(enterprise=enterprise)
            for offer in offers:
                offer.update(state=finished)
            for member_user in enterprise.member_users:
                member_user.delete()
        elif user.permission.name == 'member':
            user.delete()
        return Message.deleted()


class ImageApi(Resource):
    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user = CommonUser.objects.get(account=user_id)
            except DoesNotExist as e:
                raise GetException(e)
        else:
            user = user_helper.get_user_from_jwt()
        return {'profile_photo': user.profile_photo.base64 if user.profile_photo else None}

    def post(self):
        profile_photo = request.get_json().get('profile_photo')
        if not profile_photo:
            abort(400, message='No image sent')
        user = user_helper.get_user_from_jwt()
        if user.profile_photo:
            user.profile_photo.delete()
        new_image = Image(base64=profile_photo).save()
        user.update(profile_photo=new_image)
        return Message.created()

    def delete(self):
        user = user_helper.get_user_from_jwt()
        if user.profile_photo:
            user.profile_photo.delete()
            user.save()
        return Message.deleted()


class CurriculumApi(Resource):
    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user = CommonUser.objects.get(account=user_id)
            except DoesNotExist as e:
                raise GetException(e)
        elif user_helper.get_user_from_jwt(keys='user_type') == 'enterprise':
            abort(400, message='Missing user id')
        else:
            user = user_helper.get_user_from_jwt()
        return user.curriculum if user.curriculum else {}

    def post(self, user_id=None):
        body = request.get_json()
        user = user_helper.get_user_from_jwt()
        try:
            new_curriculum = UserCurriculumVitae(**body)
            new_curriculum.save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        user.update(curriculum=new_curriculum)
        return Message.created()

    def delete(self, user_id=None):
        user = user_helper.get_user_from_jwt()
        if user.curriculum:
            user.curriculum.delete()
            user.save()
        return Message.deleted()


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

        if isinstance(user, EnterpriseUser) and user.permission.name == 'admin':
            SuggestRegisterNewMemberNotification(user=user).save()

        return {'user': user.account}, 200


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

        def sort_func(e):
            return e.start_date

        if attribute_name in ['experience', 'education']:
            attribute_list.sort(key=sort_func, reverse=True)
        return attribute_list

    def post(self, attribute_name, _id=None):
        user = user_helper.get_user_from_jwt()
        body = request.get_json()
        if not hasattr(user, attribute_name):
            abort(400, message='Attribute {} not exists'.format(attribute_name))
        attribute_list = getattr(user, attribute_name)
        try:
            attribute_list.create(**body)
            attribute_list.save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()

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
        return Message.updated()

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
        return Message.deleted()


class RecoverAccountApi(Resource):

    def post(self):
        account = request.get_json().get('account')
        if not account:
            abort(400, message='Account required')
        user = user_helper.get_user(user_account=account, fail_ok=True)
        if not user or user.state.name != 'deleted':
            abort(400, message='Account {} is not deleted'.format(account))
        user_type = 'common' if isinstance(user, CommonUser) else 'enterprise'
        recovery_ticket = RecoveryTicket(account=account, user_type=user_type).save()
        Thread(target=lambda: EmailRecovery(destination_email=account,
                                            ticket_hash=recovery_ticket.id).send_email()).start()
        return Message.ok()

    def get(self):
        recovery_ticket = request.args.get('ticket')
        if not recovery_ticket:
            abort(400, message='Ticket required')
        if not RecoveryTicket.objects(id=recovery_ticket).count():
            abort(400, message='Ticket {} not exists'.format(recovery_ticket))
        ticket = RecoveryTicket.objects.get(id=recovery_ticket)
        user = user_helper.get_user(user_type=ticket.user_type, user_account=ticket.account)
        user.update(state=StateUser.objects.get(name='active'))
        ticket.delete()
        return {'user': user.account}, 200


class DoAdminApi(Resource):

    method_decorators = {
        'post': [validate_permission_is_admin, validate_user_is_enterprise, validate_user_exists,
                 authentication_required, validate_headers]
    }

    def post(self):
        enterprise = enterprise_helper.get_enterprise()
        username = request.get_json().get('account')

        if not [member_user for member_user in enterprise.member_users if member_user.account == username]:
            abort(400, message='User {} does not exist in the list of member users'.format(username))

        admin_user = enterprise.admin_user
        target_user = EnterpriseUser.objects.get(account=username)

        admin_user.update(permission=Permission.objects.get(name='member'))
        target_user.update(permission=Permission.objects.get(name='admin'))

        enterprise.update(push__member_users=enterprise.admin_user)
        enterprise.update(admin_user=target_user)
        enterprise.update(pull__member_users=target_user)
        return Message.created()
