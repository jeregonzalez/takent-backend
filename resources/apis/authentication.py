import datetime

from flask import request
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from flask_restful import Resource, abort
from jwt import ExpiredSignatureError

from database.models.user import CommonUser
from resources.helpers import auth_helper, user_helper
from resources.utils.exceptions import AuthorizationTokenExpiredException, UnauthorizedException


class AuthenticationApi(Resource):
    def post(self):
        body = request.get_json()
        if not body:
            try:
                verify_jwt_in_request()
            except ExpiredSignatureError:
                raise AuthorizationTokenExpiredException
            except Exception:
                raise UnauthorizedException
            user = user_helper.get_user_from_jwt()
        else:
            user_account = body.get('account')
            user_password = body.get('password')
            if not user_account or not user_password:
                abort(400, message='Missing fields account or password')
            if not user_helper.user_exists(user_account=user_account):
                abort(400, message='User {} not exists'.format(user_account))
            user = user_helper.get_user(user_account=user_account)
            authorized = auth_helper.check_password(hash_pw=user.password, password=user_password)
            if not authorized:
                abort(401, message='Account or password invalid')
            if user.state.name in ['inactive', 'deleted']:
                kwargs = {'message': 'User {} is not active'.format(user_account)}
                if not hasattr(user, 'permission') or user.permission.name != 'member':
                    kwargs['state'] = user.state.name
                abort(400, **kwargs)
        expires = datetime.timedelta(hours=4)
        user_type = 'common' if isinstance(user, CommonUser) else 'enterprise'
        identity = {'user_type': user_type, 'user_account': user.account}
        if user_type == 'enterprise':
            identity['permission'] = user.permission.name
        access_token = create_access_token(identity=identity,
                                           expires_delta=expires)
        return {'token': access_token}, 200
