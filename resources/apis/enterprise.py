from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError, DoesNotExist

from database.models.common import Image
from database.models.enterprise import Enterprise
from resources.helpers import user_helper, enterprise_helper
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_user_is_enterprise, validate_enterprise_exists, validate_enterprise_not_exists
from resources.utils.exceptions import SaveException, UpdateException, GetException
from resources.utils.messages import Message


class EnterpriseApi(Resource):
    method_decorators = {
        'get': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'post': [validate_enterprise_not_exists, validate_user_is_enterprise, validate_user_exists,
                 authentication_required, validate_headers],
        'put': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                   authentication_required, validate_headers]
    }

    def get(self):
        user_account = user_helper.get_user_from_jwt(keys='user_account')
        return enterprise_helper.get_enterprise(user_account=user_account)

    def post(self):
        body = request.get_json()
        body['admin_user'] = user_helper.get_user_from_jwt()
        try:
            Enterprise(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()

    def put(self):
        body = request.get_json()
        enterprise = enterprise_helper.get_enterprise(user_account=user_helper.get_user_from_jwt(keys='user_account'))
        try:
            enterprise.update(**body)
        except (InvalidQueryError, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self):
        enterprise_helper.get_enterprise(user_account=user_helper.get_user_from_jwt().account).delete()
        return '', 204


class ProfilePhotoEnterpriseApi(Resource):
    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                 validate_headers],
        'put': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'delete': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                   authentication_required, validate_headers]
    }

    def get(self):
        id_enterprise = request.args.get('id')
        if id_enterprise:
            try:
                enterprise = Enterprise.objects.get(id=id_enterprise)
            except DoesNotExist as e:
                raise GetException(e)
        else:
            if get_jwt_identity().get('user_type') != 'enterprise':
                abort(400, message='User must be enterprise')
            if not enterprise_helper.enterprise_exists(user_account=get_jwt_identity().get('user_account')):
                abort(400, message='User {} does not have an enterprise associated'
                      .format(get_jwt_identity().get('user_account')))
            user = user_helper.get_user_from_jwt(keys='user_account')
            enterprise = enterprise_helper.get_enterprise(user_account=user)
        return {'profile_photo': enterprise.profile_photo.base64 if enterprise.profile_photo else None}

    def post(self):
        profile_photo = request.get_json().get('profile_photo')
        if not profile_photo:
            abort(400, message='No image sent')
        user = user_helper.get_user_from_jwt(keys='user_account')
        enterprise = enterprise_helper.get_enterprise(user_account=user)
        if enterprise.profile_photo:
            enterprise.profile_photo.delete()
        new_image = Image(base64=profile_photo).save()
        enterprise.update(profile_photo=new_image)
        return Message.created()

    def delete(self):
        user = user_helper.get_user_from_jwt(keys='user_account')
        enterprise = enterprise_helper.get_enterprise(user_account=user)
        if enterprise.profile_photo:
            enterprise.profile_photo.delete()
            enterprise.save()
        return Message.deleted()


class EnterpriseImagesApi(Resource):
    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                 validate_headers],
        'put': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'delete': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                   authentication_required, validate_headers]
    }

    def get(self):
        id_enterprise = request.args.get('id')
        if id_enterprise:
            try:
                enterprise = Enterprise.objects.get(id=id_enterprise)
            except DoesNotExist as e:
                raise GetException(e)
        else:
            if get_jwt_identity().get('user_type') != 'enterprise':
                abort(400, message='User must be enterprise')
            if not enterprise_helper.enterprise_exists(user_account=get_jwt_identity().get('user_account')):
                abort(400, message='User {} does not have an enterprise associated'
                      .format(get_jwt_identity().get('user_account')))
            user = user_helper.get_user_from_jwt(keys='user_account')
            enterprise = enterprise_helper.get_enterprise(user_account=user)
        return [image.base64 for image in enterprise.images if image.base64]

    def post(self):
        images = request.get_json().get('images')
        if not images:
            abort(400, message='No images sent')
        user = user_helper.get_user_from_jwt(keys='user_account')
        enterprise = enterprise_helper.get_enterprise(user_account=user)
        if enterprise.images:
            enterprise.images.delete()
        images_obj = []
        for image in images:
            new_image = Image(base64=image).save()
            images_obj.append(new_image)
        enterprise.update(images=images_obj)
        return Message.created()

    def delete(self):
        user = user_helper.get_user_from_jwt(keys='user_account')
        enterprise = enterprise_helper.get_enterprise(user_account=user)
        if enterprise.images:
            for image in enterprise.images:
                enterprise.images.remove(image)
                image.delete()
            enterprise.save()
        return Message.deleted()
