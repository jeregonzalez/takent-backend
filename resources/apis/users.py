from flask import request, Response
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, NotUniqueError, ValidationError

from resources.helpers.auth_helper import hash_password
from resources.helpers.log_helper import LOGGER
from resources.helpers.user_helper import get_user, USER_TYPES
from resources.utils.decorators import validate_headers, authentication_required, user_must_not_exist, \
    user_must_exist, user_must_be_common
from resources.utils.exceptions import MissingRequiredFieldsException, UserAlreadyExistsException, \
    SchemaValidationErrorException


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
        new_user = None
        if body.get('password'):
            body['password'] = hash_password(body['password'])
        try:
            LOGGER.debug(user_type)
            new_user = USER_TYPES[user_type](**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        except NotUniqueError:
            raise UserAlreadyExistsException(new_user.account)
        return {'message': 'User {} created successfully'.format(new_user.id)}, 201

    def put(self, user_type=None):
        body = request.get_json()
        get_user().update(**body)
        return '', 204

    def delete(self, user_type=None):
        get_user().delete()
        return '', 204


class ImageApi(Resource):

    method_decorators = {
        'get': [user_must_exist, user_must_be_common, authentication_required],
        'post': [user_must_exist, user_must_be_common, authentication_required]
    }

    def get(self):
        user = get_user()
        if not user.profile_photo:
            return {'message': 'User {} does not have profile photo'.format(user.account)}, 200
        return Response(user.profile_photo.read(), mimetype=user.profile_photo.content_type, status=200)

    def post(self):
        if not request.files or not request.files.get('profile_photo'):
            abort(400, message='No image sent')
        user = get_user()
        new_photo = request.files.get('profile_photo')
        if user.profile_photo:
            user.profile_photo.delete()
        user.profile_photo.put(new_photo, content_type=new_photo.content_type)
        user.save()
        return {'message': 'Profile photo uploaded successfully'}, 201


class CurriculumApi(Resource):

    method_decorators = {
        'get': [user_must_exist, user_must_be_common, authentication_required],
        'post': [user_must_exist, user_must_be_common, authentication_required]
    }

    def get(self):
        user = get_user()
        if not user.curriculum:
            return {'message': 'User {} does not have curriculum'.format(user.account)}, 200
        return Response(user.curriculum.read(), mimetype=user.curriculum.content_type, status=200)

    def post(self):
        if not request.files or not request.files.get('curriculum'):
            abort(400, message='No curriculum sent')
        user = get_user()
        new_curriculum = request.files.get('curriculum')
        if user.curriculum:
            user.curriculum.delete()
        user.curriculum.put(new_curriculum, content_type=new_curriculum.content_type)
        user.save()
        return {'message': 'Curriculum uploaded successfully'}, 201
