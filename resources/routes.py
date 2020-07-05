from resources.apis.mongo import MongoApi
from resources.apis.places import CountriesApi, ProvincesApi, CitiesApi
from resources.apis.users import SignUpApi, UserApi


def initialize_routes(api):
    # Mongo
    api.add_resource(MongoApi, '/api/v1/init/mongodb')
    # Places
    api.add_resource(CountriesApi, '/api/v1/countries')
    api.add_resource(ProvincesApi, '/api/v1/provinces')
    api.add_resource(CitiesApi, '/api/v1/cities/<int:province_id>')
    # Users
    api.add_resource(SignUpApi, '/api/v1/signup/<user_type>')
    api.add_resource(UserApi, '/api/v1/user/<user_type>/<user_account>', '/api/v1/user/<user_type>')
