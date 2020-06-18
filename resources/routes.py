from resources.auth import SignUpApi, LoginApi


def initialize_routes(api):
    api.add_resource(SignUpApi, '/api/v1/authentication/signup')
    api.add_resource(LoginApi, '/api/v1/authentication/login')
