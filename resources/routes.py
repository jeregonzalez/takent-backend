from resources.apis.allowed_user import AllowedUserApi
from resources.apis.education import EducationLevelApi
from resources.apis.enterprise import EnterpriseApi
from resources.apis.authentication import AuthenticationApi
from resources.apis.enterprise_type import EnterpriseTypeApi
from resources.apis.language import LanguageApi, LanguageLevelApi
from resources.apis.mongo import MongoApi
from resources.apis.place import CountriesApi, ProvincesApi, CitiesApi
from resources.apis.sector import SectorApi
from resources.apis.user import ImageApi, CurriculumApi, UserApi, PasswordRecoverApi, ChangePasswordApi, \
    UserExistsValidationApi, ActivateAccountApi, UserAttributesListApi
from resources.apis.offer import OfferApi
from resources.apis.reactivation_offer import ReactivateOfferApi


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
    api.add_resource(UserExistsValidationApi, '/api/v1/user/exists')
    api.add_resource(ActivateAccountApi, '/api/v1/user/activate')
    api.add_resource(UserAttributesListApi, '/api/v1/user/common/<attribute_name>/<_id>',
                     '/api/v1/user/common/<attribute_name>')
    # Enterprise
    api.add_resource(EnterpriseApi, '/api/v1/enterprise')
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
    api.add_resource(OfferApi, '/api/v1/offer', '/api/v1/offer/<id>')
    api.add_resource(ReactivateOfferApi, '/api/v1/reactivation/<id>')
    api.add_resource(AllowedUserApi, '/api/v1/allowed', '/api/v1/allowed/<account>')
    api.add_resource(SectorApi, '/api/v1/sector', '/api/v1/sector/<id>')
    api.add_resource(EnterpriseTypeApi, '/api/v1/enterprise_type', '/api/v1/enterprise_type/<id>')