import datetime

from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource, abort

from resources.helpers.auth_helper import check_password
from resources.helpers.log_helper import LOGGER
from resources.helpers.user_helper import validate_user_exists, USER_TYPES


class AuthenticationApi(Resource):
    def post(self, user_type=None):
        if user_type not in USER_TYPES.keys():
            abort(404)
        body = request.get_json()
        user_account = body.get('account')
        user_password = body.get('password')
        if not user_account or not user_password:
            abort(400, message='Missing fields account or password')
        validate_user_exists(user_type=user_type, user_account=user_account)
        user = USER_TYPES[user_type].objects.get(account=user_account)
        LOGGER.debug(user.account)
        LOGGER.debug(user.password)
        authorized = check_password(hash_pw=user.password, password=user_password)
        if not authorized:
            abort(403, message='Account or password invalid')
        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=user.account, expires_delta=expires)
        return {'token': access_token}, 200
