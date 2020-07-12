from resources.apis.enterprise import EnterpriseApi
from resources.apis.authentication import AuthenticationApi
from resources.apis.mongo import MongoApi
from resources.apis.places import CountriesApi, ProvincesApi, CitiesApi
from resources.apis.users import CommonUserApi, EnterpriseUserApi, ImageApi, CurriculumApi


def initialize_routes(api):
    # Mongo
    api.add_resource(MongoApi, '/api/v1/init/mongodb')
    # Places
    api.add_resource(CountriesApi, '/api/v1/countries')
    api.add_resource(ProvincesApi, '/api/v1/provinces')
    api.add_resource(CitiesApi, '/api/v1/cities/<int:province_id>')
    # Users
    api.add_resource(CommonUserApi, '/api/v1/user/common')
    api.add_resource(EnterpriseUserApi, '/api/v1/user/enterprise')
    api.add_resource(ImageApi, '/api/v1/user/common/profile_photo')
    api.add_resource(CurriculumApi, '/api/v1/user/common/curriculum')
    # Enterprise
    api.add_resource(EnterpriseApi, '/api/v1/enterprise', '/api/v1/enterprise/<admin>')
    # Authentication
    api.add_resource(AuthenticationApi, '/api/v1/authentication')
