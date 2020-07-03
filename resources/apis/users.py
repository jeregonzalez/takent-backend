from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, NotUniqueError

from database.models.users import CommonUser, EnterpriseUser
from resources.errors import SchemaValidationError, AccountAlreadyExistsError

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


class SignUpApi(Resource):
    def post(self, user_type):
        if user_type not in USER_TYPES.keys():
            abort(404)
        body = request.get_json()
        try:
            new_user = USER_TYPES[user_type](**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        return {'message': 'User {} created successfully'.format(new_user.id)}, 200
