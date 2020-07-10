from flask import request, Response
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, NotUniqueError, ValidationError

from database.models.users import CommonUser, EnterpriseUser
from resources.errors import SchemaValidationError, AccountAlreadyExistsError

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


class CommonUserApi(Resource):
    def get(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        return CommonUser.objects.exclude('password', 'profile_photo').get(account=user_account).to_mongo()

    def post(self):
        body = request.get_json()
        validate_user_not_exists(user_type='common', user_account=body.get('account'))
        try:
            new_user = CommonUser(**body).save()
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        return {'message': 'Common user {} created successfully'.format(new_user.id)}, 201

    def put(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        body = request.get_json()
        if any(field in ['account', 'password'] for field in body.keys()):
            abort(403, message='Account or password fields cannot be updated')
        CommonUser.objects.get(account=user_account).update(**body)
        return '', 204

    def delete(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        CommonUser.objects.get(account=user_account).delete()
        return '', 204


class EnterpriseUserApi(Resource):
    def get(self, user_account):
        validate_user_exists(user_type='enterprise', user_account=user_account)
        return EnterpriseUser.objects.exclude('password').get(account=user_account).to_mongo()

    def post(self):
        body = request.get_json()
        validate_user_not_exists(user_type='common', user_account=body.get('account'))
        try:
            new_user = EnterpriseUser(**body).save()
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        return {'message': 'Enterprise user {} created successfully'.format(new_user.id)}, 201

    def put(self, user_account=None):
        validate_user_exists(user_type='enterprise', user_account=user_account)
        body = request.get_json()
        if any(field in ['account', 'password'] for field in body.keys()):
            abort(403, message='Account or password fields cannot be updated')
        EnterpriseUser.objects.get(account=user_account).update(**body)
        return '', 204

    def delete(self, user_account=None):
        validate_user_exists(user_type='enterprise', user_account=user_account)
        EnterpriseUser.objects.get(account=user_account).delete()
        return '', 204


class ImageApi(Resource):
    def get(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        user = CommonUser.objects.get(account=user_account)
        if not user.profile_photo:
            abort(200, message='User {} does not have profile photo'.format(user_account))
        return Response(user.profile_photo.read(), mimetype=user.profile_photo.content_type, status=200)

    def post(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
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
    def get(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        user = CommonUser.objects.get(account=user_account)
        if not user.curriculum:
            abort(200, message='User {} does not have curriculum'.format(user_account))
        return Response(user.curriculum.read(), mimetype=user.curriculum.content_type, status=200)

    def post(self, user_account=None):
        validate_user_exists(user_type='common', user_account=user_account)
        if not request.files or not request.files.get('curriculum'):
            abort(400, message='No curriculum sent')
        user = CommonUser.objects.get(account=user_account)
        new_curriculum = request.files.get('curriculum')
        if user.curriculum:
            user.curriculum.delete()
        user.curriculum.put(new_curriculum, content_type=new_curriculum.content_type)
        user.save()
        return {'message': 'Curriculum uploaded successfully'}, 201


def validate_user_exists(user_type, user_account):
    if not user_account:
        abort(400, message='You must enter an user')
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if not exist:
        abort(400, message='User {} does not exist'.format(user_account))


def validate_user_not_exists(user_type, user_account):
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if exist:
        abort(400, message='User {} already exists'.format(user_account))
