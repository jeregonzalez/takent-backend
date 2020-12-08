from resources.apis.member_user import MemberUserApi, MemberUsersByEnterprise
from resources.apis.education import EducationLevelApi
from resources.apis.enterprise import EnterpriseApi, ProfilePhotoEnterpriseApi, EnterpriseImagesApi
from resources.apis.authentication import AuthenticationApi
from resources.apis.enterprise_type import EnterpriseTypeApi
from resources.apis.language import LanguageApi, LanguageLevelApi
from resources.apis.mercadopago import MercadoPagoApi, OfferPackApi, MPNotificationsApi, PreferredServiceApi
from resources.apis.development import MongoApi
from resources.apis.place import CountriesApi, ProvincesApi, CitiesApi
from resources.apis.postulant import PostulantApi, PostulateApi, StatePostulantApi
from resources.apis.sector import SectorApi
from resources.apis.profession import ProfessionApi
from resources.apis.service import ServiceApi, ServiceImagesApi
from resources.apis.service_request import ServiceRequestApi, NewServiceRequestApi
from resources.apis.user import ImageApi, CurriculumApi, UserApi, PasswordRecoverApi, ChangePasswordApi, \
    UserExistsValidationApi, ActivateAccountApi, UserAttributesListApi
from resources.apis.offer import OfferApi, OfferImagesApi
from resources.apis.user_and_enterprise import UserAndEnterpriseApi


def initialize_routes(api):
    # Development apis
    api.add_resource(MongoApi, '/api/v1/init/mongodb')
    # Places
    api.add_resource(CountriesApi, '/api/v1/countries')
    api.add_resource(ProvincesApi, '/api/v1/provinces')
    api.add_resource(CitiesApi, '/api/v1/cities/<int:province_id>')
    # Parametric documents
    api.add_resource(LanguageApi, '/api/v1/language')
    api.add_resource(LanguageLevelApi, '/api/v1/language_level')
    api.add_resource(EducationLevelApi, '/api/v1/education_level')
    api.add_resource(ProfessionApi, '/api/v1/profession')
    api.add_resource(SectorApi, '/api/v1/sector')
    api.add_resource(EnterpriseTypeApi, '/api/v1/enterprise_type')
    # Authentication
    api.add_resource(AuthenticationApi, '/api/v1/authentication')
    # Users
    api.add_resource(UserApi, '/api/v1/user/<user_type>')
    api.add_resource(ImageApi, '/api/v1/user/common/profile_photo')
    api.add_resource(CurriculumApi, '/api/v1/user/common/curriculum')
    api.add_resource(UserExistsValidationApi, '/api/v1/user/exists')
    api.add_resource(ActivateAccountApi, '/api/v1/user/activate')
    api.add_resource(UserAttributesListApi, '/api/v1/user/common/<attribute_name>/<_id>',
                     '/api/v1/user/common/<attribute_name>')
    api.add_resource(MemberUserApi, '/api/v1/member_user', '/api/v1/member_user/<account>')
    api.add_resource(MemberUsersByEnterprise, '/api/v1/members')
    # Password
    api.add_resource(PasswordRecoverApi, '/api/v1/user/common/recover_password',
                     '/api/v1/user/enterprise/recover_password')
    api.add_resource(ChangePasswordApi, '/api/v1/user/common/change_password',
                     '/api/v1/user/enterprise/change_password')
    # Enterprise
    api.add_resource(EnterpriseApi, '/api/v1/enterprise')
    api.add_resource(ProfilePhotoEnterpriseApi, '/api/v1/enterprise/profile_photo')
    api.add_resource(EnterpriseImagesApi, '/api/v1/enterprise/images')
    # Offer
    api.add_resource(OfferApi, '/api/v1/offer/<id_offer>', '/api/v1/offer')
    api.add_resource(OfferImagesApi, '/api/v1/offer/<id_offer>/images')
    # Postulant
    api.add_resource(PostulantApi, '/api/v1/offer/<id_offer>/postulant',
                     '/api/v1/offer/<id_offer>/postulant/<id_postulant>')
    # Postulate
    api.add_resource(PostulateApi, '/api/v1/postulate/<id_offer>')
    # Contact postulant
    api.add_resource(StatePostulantApi, '/api/v1/offer/<id_offer>/postulant/<id_postulant>/<action>')
    # Enterprise and admin user
    api.add_resource(UserAndEnterpriseApi, '/api/v1/user_and_enterprise')
    # Mercado Pago
    api.add_resource(OfferPackApi, '/api/v1/offer_pack')
    api.add_resource(PreferredServiceApi, '/api/v1/preferred_service')
    api.add_resource(MercadoPagoApi, '/api/v1/mercadopago/generate_payment')
    api.add_resource(MPNotificationsApi, '/api/v1/mercadopago/notification')
    # Services
    api.add_resource(ServiceApi, '/api/v1/service/<service_id>', '/api/v1/service')
    api.add_resource(ServiceImagesApi, '/api/v1/service/<service_id>/images')
    # Service Request
    api.add_resource(ServiceRequestApi, '/api/v1/service/<service_id>/request',
                     '/api/v1/service/<service_id>/request/<service_request_id>')
    # Request service
    api.add_resource(NewServiceRequestApi, '/api/v1/request_service/<service_id>')
