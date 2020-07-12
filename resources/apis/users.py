from flask import request, Response
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, NotUniqueError, ValidationError

from database.models.users import CommonUser, EnterpriseUser
from resources.helpers.auth_helper import hash_password
from resources.helpers.user_helper import get_user_account
from resources.utils.decorators import validate_headers, common_user_must_exist, authentication_required, \
    enterprise_user_must_exist, user_must_not_exist
from resources.utils.exceptions import MissingRequiredFieldsException, UserAlreadyExistsException


class CommonUserApi(Resource):

    method_decorators = {
        'get': [common_user_must_exist, authentication_required, validate_headers],
        'post': [user_must_not_exist, validate_headers],
        'put': [common_user_must_exist, authentication_required, validate_headers],
        'delete': [common_user_must_exist, authentication_required, validate_headers]
    }

    def get(self):
        user_account = get_user_account()
        return CommonUser.objects.exclude('password', 'profile_photo').get(account=user_account).to_mongo()

    def post(self):
        body = request.get_json()
        if body.get('password'):
            body['password'] = hash_password(body['password'])
        try:
            new_user = CommonUser(**body).save()
        except (FieldDoesNotExist, ValidationError):
            raise MissingRequiredFieldsException
        except NotUniqueError:
            raise UserAlreadyExistsException(new_user.id)
        return {'message': 'Common user {} created successfully'.format(new_user.id)}, 201

    def put(self):
        user_account = get_user_account()
        body = request.get_json()
        if any(field in ['account', 'password'] for field in body.keys()):
            abort(403, message='Account or password fields cannot be updated')
        CommonUser.objects.get(account=user_account).update(**body)
        return '', 204

    def delete(self):
        user_account = get_user_account()
        CommonUser.objects.get(account=user_account).delete()
        return '', 204


class EnterpriseUserApi(Resource):

    method_decorators = {
        'get': [enterprise_user_must_exist, authentication_required, validate_headers],
        'post': [user_must_not_exist, validate_headers],
        'put': [enterprise_user_must_exist, authentication_required, validate_headers],
        'delete': [enterprise_user_must_exist, authentication_required, validate_headers]
    }

    def get(self):
        user_account = get_user_account()
        return EnterpriseUser.objects.exclude('password').get(account=user_account).to_mongo()

    def post(self):
        body = request.get_json()
        if body.get('password'):
            body['password'] = hash_password(body['password'])
        try:
            new_user = EnterpriseUser(**body).save()
        except (FieldDoesNotExist, ValidationError):
            raise MissingRequiredFieldsException
        except NotUniqueError:
            raise UserAlreadyExistsException(new_user.id)
        return {'message': 'Enterprise user {} created successfully'.format(new_user.id)}, 201

    def put(self):
        user_account = get_user_account()
        body = request.get_json()
        if any(field in ['account', 'password'] for field in body.keys()):
            abort(403, message='Account or password fields cannot be updated')
        EnterpriseUser.objects.get(account=user_account).update(**body)
        return '', 204

    def delete(self):
        user_account = get_user_account()
        EnterpriseUser.objects.get(account=user_account).delete()
        return '', 204


class ImageApi(Resource):

    method_decorators = {
        'get': [common_user_must_exist, authentication_required],
        'post': [common_user_must_exist, authentication_required]
    }

    def get(self):
        user_account = get_user_account()
        user = CommonUser.objects.get(account=user_account)
        if not user.profile_photo:
            return {'message': 'User {} does not have profile photo'.format(user_account)}, 200
        return Response(user.profile_photo.read(), mimetype=user.profile_photo.content_type, status=200)

    def post(self):
        user_account = get_user_account()
        if not request.files or not request.files.get('profile_photo'):
            abort(400, message='No image sent')
        user = CommonUser.objects.get(account=user_account)
        new_photo = request.files.get('profile_photo')
        if user.profile_photo:
            user.profile_photo.delete()
        user.profile_photo.put(new_photo, content_type=new_photo.content_type)
        user.save()
        return {'message': 'Profile photo uploaded successfully'}, 201


class CurriculumApi(Resource):

    method_decorators = {
        'get': [common_user_must_exist, authentication_required],
        'post': [common_user_must_exist, authentication_required]
    }

    def get(self):
        user_account = get_user_account()
        user = CommonUser.objects.get(account=user_account)
        if not user.curriculum:
            return {'message': 'User {} does not have curriculum'.format(user_account)}, 200
        return Response(user.curriculum.read(), mimetype=user.curriculum.content_type, status=200)

    def post(self):
        user_account = get_user_account()
        if not request.files or not request.files.get('curriculum'):
            abort(400, message='No curriculum sent')
        user = CommonUser.objects.get(account=user_account)
        new_curriculum = request.files.get('curriculum')
        if user.curriculum:
            user.curriculum.delete()
        user.curriculum.put(new_curriculum, content_type=new_curriculum.content_type)
        user.save()
        return {'message': 'Curriculum uploaded successfully'}, 201
