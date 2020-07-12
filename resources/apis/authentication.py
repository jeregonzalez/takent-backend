import datetime

from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource, abort

from resources.helpers.auth_helper import check_password
from resources.helpers.user_helper import USER_TYPES, get_user_type


class AuthenticationApi(Resource):
    def post(self):
        body = request.get_json()
        user_account = body.get('account')
        user_password = body.get('password')
        if not user_account or not user_password:
            abort(400, message='Missing fields account or password')
        user_type = get_user_type(user_account)
        if not user_type:
            abort(400, message='User {} does not exist'.format(user_type))
        user = USER_TYPES[user_type].objects.get(account=user_account)
        authorized = check_password(hash_pw=user.password, password=user_password)
        if not authorized:
            abort(403, message='Account or password invalid')
        expires = datetime.timedelta(hours=4)
        access_token = create_access_token(identity={'user_type': user_type, 'user_account': user.account},
                                           expires_delta=expires)
        return {'token': access_token}, 200
