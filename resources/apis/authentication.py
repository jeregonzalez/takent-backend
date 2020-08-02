import datetime

from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource, abort

from database.models.user import CommonUser
from resources.helpers import auth_helper, user_helper


class AuthenticationApi(Resource):
    def post(self):
        body = request.get_json()
        user_account = body.get('account')
        user_password = body.get('password')
        if not user_account or not user_password:
            abort(400, message='Missing fields account or password')
        if not user_helper.user_exists(user_account=user_account):
            abort(400, message='User {} not exists'.format(user_account))
        user = user_helper.get_user(user_account=user_account)
        if user.state.name == 'inactive':
            abort(400, message='User {} is inactive'.format(user_account))
        authorized = auth_helper.check_password(hash_pw=user.password, password=user_password)
        if not authorized:
            abort(401, message='Account or password invalid')
        expires = datetime.timedelta(hours=4)
        user_type = 'common' if isinstance(user, CommonUser) else 'enterprise'
        access_token = create_access_token(identity={'user_type': user_type, 'user_account': user.account},
                                           expires_delta=expires)
        return {'token': access_token}, 200
