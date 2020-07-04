from flask_restful import Resource

from database.initial_values import data
from database.models.common import Country, Province, City, EducationLevel, LanguageLevel
from database.models.roles import Permission, Role
from resources.helpers import places_helper


class MongoApi(Resource):
    def get(self):
        # Init permissions
        init_permissions(data.get('permission'))

        # Init roles
        init_roles(data.get('role'))

        # Init Countries, Provinces, Cities
        init_countries_provinces_cities()

        # Init education levels
        init_education_levels(data.get('education_level'))

        # Init language levels
        init_language_levels(data.get('language_level'))

        return {'message': 'Success'}, 200


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
