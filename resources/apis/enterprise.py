from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.common import Image
from database.models.enterprise import Enterprise
from resources.helpers import user_helper, enterprise_helper
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_user_is_enterprise, validate_enterprise_exists, validate_enterprise_not_exists
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException, SaveException, \
    UpdateException
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
        enterprise_helper.get_enterprise(user_account=user_helper.get_user_from_jwt().account).deactivate()
        return '', 204


class ProfilePhotoEnterpriseApi(Resource):
    method_decorators = {
        'get': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'post': [validate_enterprise_exists,
                 validate_user_is_enterprise,
                 validate_user_exists, authentication_required, validate_headers],
        'put': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_enterprise_exists, validate_user_is_enterprise,
                   validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        data = {}
        image = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).profile_photo
        if not image:
            abort(400, message='Profile photo does not exist')
        data['id'] = image.id
        data['image'] = image.base64

        return Message.ok(data)

    def post(self, admin_user=None):
        body = request.get_json()
        try:
            image = Image(base64=body.get('profile_photo')).save()
            enterprise = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt())
            if enterprise.profile_photo:
                enterprise.profile_photo.delete()
            enterprise.update(profile_photo=image)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.created('Profile photo')

    def delete(self, admin_user=None):
        profile_photo = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).profile_photo
        if not profile_photo:
            abort(400, message='Profile photo does not exist')
        profile_photo.delete()

        return Message.delete()


class EnterprisePhotosApi(Resource):
    method_decorators = {
        'get': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists, authentication_required,
                validate_headers],
        'post': [validate_enterprise_exists,
                 validate_user_is_enterprise,
                 validate_user_exists, authentication_required, validate_headers],
        'put': [validate_enterprise_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_enterprise_exists, validate_user_is_enterprise,
                   validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        data = []
        photos = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).photos
        if not photos:
            abort(400, message='Not found photos')
        for image in photos:
            aux = {'id': image.id, 'image': image.base64}
            data.append(aux)
        return Message.ok(data)

    def post(self):
        body = request.get_json()

        list_images = []
        for image in body.get('photos'):
            data = Image(base64=image)
            data.save()
            list_images.append(data)

        enterprise = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt())
        photos = enterprise.photos
        photos.extend(list_images)
        enterprise.update(photos=photos)

        return Message.created('Photos')

    def delete(self, id_photo):

        if not Image.objects(id=id_photo).count():
            abort(400, message='Image does not exist')

        image = Image.objects.get(id=id_photo)
        Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt()).update(pull__photos=image)
        image.delete()

        return Message.delete()
