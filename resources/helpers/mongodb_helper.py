import csv
import json
import os

from database.models.parametric_docs import ContractType, EducationLevel, EnterpriseType, ExperienceLevel, Language, \
    LanguageLevel, Permission, Profession, Sector, StateUser, StateOffer, StatePostulant, StateService, \
    StateServiceRequest, MercadoPagoConcept
from database.models.place import Country, City, Province
from resources.helpers import place_helper
from resources.helpers.log_helper import LOGGER

INITIAL_DATA_DIRECTORY = 'database/parametric_docs_data'

MODEL_MAP = {
    'contract_type': ContractType,
    'education_level': EducationLevel,
    'enterprise_type': EnterpriseType,
    'experience_level': ExperienceLevel,
    'language': Language,
    'language_level': LanguageLevel,
    'mercado_pago_concept': MercadoPagoConcept,
    'permission': Permission,
    'profession': Profession,
    'sector': Sector,
    'state_user': StateUser,
    'state_offer': StateOffer,
    'state_postulant': StatePostulant,
    'state_service': StateService,
    'state_service_request': StateServiceRequest
}


def upload_data():
    for file in __get_files():
        model_name, ext = os.path.splitext(os.path.basename(file))
        if not MODEL_MAP.get(model_name):
            LOGGER.info('Model {} not found'.format(model_name))
            continue
        data = __parse(file=file, ext=ext)
        model_obj = MODEL_MAP[model_name]
        model_obj.drop_collection()
        model_obj.objects.insert([model_obj(**item) for item in data])
    __init_countries_provinces_cities()


def __get_files():
    return [os.path.join(INITIAL_DATA_DIRECTORY, file) for file in os.listdir(INITIAL_DATA_DIRECTORY)]


def __parse(file, ext):
    if 'csv' in ext:
        return __parse_csv(file)
    elif 'json' in ext:
        return __parse_json(file)


def __parse_csv(file):
    obj = []
    with open(file, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            obj.append(row)
    return obj


def __parse_json(file):
    with open(file, encoding='utf-8') as file:
        json_data = file.read()
    return json.loads(json_data)


def __init_countries_provinces_cities():
    Country.drop_collection()
    City.drop_collection()
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
