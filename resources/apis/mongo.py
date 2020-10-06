import csv
import os

from flask_restful import Resource

from database.initial_values import data
from database.models.common import Country, City, Province, EducationLevel, LanguageLevel, State, Language, JobType, \
    EnterpriseType, Sector, Profession, ExperienceOffer
from database.models.enterprise import Enterprise
from database.models.mercadopago import OfferPack
from database.models.permission import Permission, Role
from database.models.user import EnterpriseUser, CommonUser
from resources.helpers import place_helper


class MongoApi(Resource):
    def get(self):
        """
        Metodo utilizado para iniciar la base de datos desde cero, para evitar errores ejecutar db.dropDatabase()
        en la consola de mongo
        :return:
        """
        init_permissions(data.get('permission'))
        init_roles(data.get('role'))
        init_countries_provinces_cities()
        init_education_levels(data.get('education_level'))
        init_language_levels(data.get('language_level'))
        init_states(data.get('state'))
        init_languages()
        init_job_type(data.get('job_type'))
        init_enterprise_type(data.get('enterprise_type'))
        init_sector()
        init_professions()
        init_experience_offer(data.get('experience_offer'))
        init_offer_pack(data.get('offer_pack'))
        return {'message': 'Database initialized correctly'}, 200


def init_permissions(permissions):
    Permission.objects.delete()
    Permission.objects.insert([
        Permission(**permission) for permission in permissions
    ])


def init_roles(roles):
    Role.objects.delete()
    for role in roles:
        role['permissions'] = [Permission.objects.get(name=permission)
                               for permission in role.get('permissions')]
    Role.objects.insert([
        Role(**role) for role in roles
    ])


def init_countries_provinces_cities():
    Country.objects.delete()
    City.objects.delete()

    # Countries
    Country.objects.insert([Country(**country) for country in place_helper.get_countries()])

    # Provinces
    argentina = Country.objects.first()
    for province in place_helper.get_provinces():
        argentina.provinces.append(Province(**province))
    argentina.save()

    # Cities
    for city in place_helper.get_cities():
        new_city = City(**city)
        new_city.save()
        province = list(filter(lambda obj: obj.code == city.get('province_id'), argentina.provinces))[0]
        province.cities.append(new_city)
    argentina.save()


def init_education_levels(education_levels):
    EducationLevel.objects.delete()
    EducationLevel.objects.insert([
        EducationLevel(**education_level) for education_level in education_levels
    ])


def init_language_levels(language_levels):
    LanguageLevel.objects.delete()
    LanguageLevel.objects.insert([
        LanguageLevel(**language_level) for language_level in language_levels
    ])


def init_states(states):
    State.objects.delete()
    State.objects.insert([
        State(**state) for state in states
    ])


def init_enterprise_users(enterprise_users):
    EnterpriseUser.objects.delete()
    for enterprise_user in enterprise_users:
        enterprise_user['state'] = State.objects.get(name='active')
        enterprise_user['role'] = Role.objects.get(name=enterprise_user['role'])
        for eu in enterprise_users:
            EnterpriseUser(**eu).save()


def init_common_users(common_users):
    CommonUser.objects.delete()
    CommonUser.objects.insert([
        CommonUser(**common_user) for common_user in common_users
    ])


def init_enterprises(enterprises):
    Enterprise.objects.delete()
    for enterprise in enterprises:
        enterprise['state'] = State.objects.get(name='active')
        enterprise['admin_user'] = EnterpriseUser.objects.get(account=enterprise['admin_user'])
        enterprise['member_users'] = [EnterpriseUser.objects.get(account=member)
                                      for member in enterprise.get('member_users')]
    Enterprise.objects.insert([
        Enterprise(**enterprise) for enterprise in enterprises
    ])


def init_professions():
    professions_csv = './database/data/professions.csv'
    if not os.path.exists(professions_csv):
        return

    professions = []
    with open(professions_csv, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            profession = {'id': row['ID'], 'name': row['Name']}
            professions.append(profession)

    Profession.objects.insert([Profession(**data_profession) for data_profession in professions])


def init_languages():
    languages_csv = './database/data/languages.csv'
    if not os.path.exists(languages_csv):
        return
    languages = []
    with open(languages_csv, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            language = {'code': row['code'], 'name': row['name']}
            languages.append(language)
    Language.objects.insert([Language(**data_language) for data_language in languages])


def init_job_type(job_types):
    JobType.objects.delete()

    for job_type in job_types:
        JobType.objects.insert(JobType(**job_type))


def init_enterprise_type(enterprise_types):
    EnterpriseType.objects.delete()

    EnterpriseType.objects.insert([EnterpriseType(**enterprise_type) for enterprise_type in enterprise_types])


def init_sector():
    Sector.objects.delete()
    sectors_csv = './database/data/sectors.csv'
    if not os.path.exists(sectors_csv):
        return
    sectors = []
    with open(sectors_csv, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            sector = {'name': row['name']}
            sectors.append(sector)
    Sector.objects.insert([Sector(**data_sector) for data_sector in sectors])


def init_experience_offer(experiences):
    ExperienceOffer.objects.delete()
    ExperienceOffer.objects.insert([ExperienceOffer(**exp) for exp in experiences])


def init_offer_pack(offer_packs):
    OfferPack.objects.delete()
    OfferPack.objects.insert([OfferPack(**offer_pack) for offer_pack in offer_packs])
