import csv
import os

from flask_restful import Resource

from database.initial_values import data
from database.models.common import Country, City, Province, EducationLevel, LanguageLevel, State, Language
from database.models.enterprise import Enterprise
from database.models.roles import Permission, Role
from database.models.users import EnterpriseUser, CommonUser
from resources.helpers import places_helper


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
    Country.objects.insert([Country(**country) for country in places_helper.get_countries()])

    # Provinces
    argentina = Country.objects.first()
    for province in places_helper.get_provinces():
        argentina.provinces.append(Province(**province))
    argentina.save()

    # Cities
    for city in places_helper.get_cities():
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


def init_languages():
    languages_csv = './database/data/languages.csv'
    if not os.path.exists(languages_csv):
        return
    languages = []
    with open(languages_csv) as file:
        reader = csv.DictReader(file)
        for row in reader:
            language = {'code': row['code'], 'name': row['name']}
            languages.append(language)
    Language.objects.insert([Language(**data_language) for data_language in languages])
