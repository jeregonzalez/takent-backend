from resources.apis.education import EducationLevelApi
from resources.apis.enterprise import EnterpriseApi
from resources.apis.authentication import AuthenticationApi
from resources.apis.languages import LanguageApi, LanguageLevelApi
from resources.apis.mongo import MongoApi
from resources.apis.places import CountriesApi, ProvincesApi, CitiesApi
from resources.apis.users import ImageApi, CurriculumApi, UserApi, PasswordRecoverApi, ChangePasswordApi


def initialize_routes(api):
    # Mongo
    api.add_resource(MongoApi, '/api/v1/init/mongodb')
    # Places
    api.add_resource(CountriesApi, '/api/v1/countries')
    api.add_resource(ProvincesApi, '/api/v1/provinces')
    api.add_resource(CitiesApi, '/api/v1/cities/<int:province_id>')
    # Users
    api.add_resource(UserApi, '/api/v1/user/<user_type>')
    api.add_resource(ImageApi, '/api/v1/user/common/profile_photo')
    api.add_resource(CurriculumApi, '/api/v1/user/common/curriculum')
    # Enterprise
    api.add_resource(EnterpriseApi, '/api/v1/enterprise', '/api/v1/enterprise/<admin>')
    # Authentication
    api.add_resource(AuthenticationApi, '/api/v1/authentication')
    # Language
    api.add_resource(LanguageApi, '/api/v1/language')
    api.add_resource(LanguageLevelApi, '/api/v1/language_level')
    # Education
    api.add_resource(EducationLevelApi, '/api/v1/education_level')
    # Password
    api.add_resource(PasswordRecoverApi, '/api/v1/user/common/recover_password',
                     '/api/v1/user/enterprise/recover_password')
    api.add_resource(ChangePasswordApi, '/api/v1/user/common/change_password',
                     '/api/v1/user/enterprise/change_password')
