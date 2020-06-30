from resources.apis.auth import SignUpApi, LoginApi
from resources.apis.mongo import MongoManagerApi


def initialize_routes(api):
    api.add_resource(SignUpApi, '/api/v1/authentication/signup')
    api.add_resource(LoginApi, '/api/v1/authentication/login')
    api.add_resource(MongoManagerApi, '/api/v1/init/mongodb')
