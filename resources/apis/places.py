from flask_restful import Resource

from database.models.common import Country, City


class CountriesApi(Resource):
    def get(self):
        """
        Obtener todos los paises
        :return:
        """
        countries = []
        for country in Country.objects.only('code', 'name'):
            countries.append({'code': country.code, 'name': country.name})
        return countries, 200


class ProvincesApi(Resource):
    def get(self):
        """
        Obtener todas las provincias de Argentina
        :return:
        """
        if not Country.objects.count():
            return [], 200
        provinces = []
        for province in Country.objects.first().provinces:
            provinces.append({'code': province.code, 'name': province.name})
        return provinces, 200


class CitiesApi(Resource):
    def get(self, province_id):
        """
        Obtener todas las localidades de una provincia determinada
        :param province_id:
        :return:
        """
        cities = []
        for city in City.objects(province_id=province_id):
            cities.append({'code': city.code, 'name': city.name})
        return cities, 200
