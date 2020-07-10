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
    api.add_resource(CommonUserApi, '/api/v1/user/common', '/api/v1/user/common/<user_account>')
    api.add_resource(EnterpriseUserApi, '/api/v1/user/enterprise', '/api/v1/user/enterprise/<user_account>')
    api.add_resource(ImageApi, '/api/v1/user/common/profile_photo/<user_account>')
    api.add_resource(CurriculumApi, '/api/v1/user/common/curriculum/<user_account>')
