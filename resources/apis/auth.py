import datetime

from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, NotUniqueError, DoesNotExist

from database.models.users import User
from resources.errors import SchemaValidationError, AccountAlreadyExistsError, InternalServerError, UnauthorizedError


class SignUpApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            return {'id': str(user.id)}, 200
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        except Exception:
            raise InternalServerError


class LoginApi(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(account=body.get('account'))
            authorized = user.check_password(body.get('password'))

            if not authorized:
                raise UnauthorizedError

            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)
            return {'token': access_token}, 200
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception:
            raise InternalServerError

    
class SignUpUser(Resource):

    def post(self):
        try:
            body = request.get_json()
            enterprise = Enterprise(**body)
            enterprise.save()
            return {'id': str(enterprise.id)} , 200
        
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        except Exception:
            raise InternalServerError
