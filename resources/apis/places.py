import json

from flask import Response
from flask_restful import Resource

from database.models.common import Country, City


class CountriesApi(Resource):
    def get(self):
        countries = []
        for country in Country.objects.only('code', 'name'):
            countries.append({'code': country.code, 'name': country.name})
        return Response(json.dumps(countries), mimetype="application/json", status=200)


class ProvincesApi(Resource):
    def get(self):
        if not Country.objects.count():
            return Response(json.dumps([]), mimetype="application/json", status=200)
        provinces = []
        for province in Country.objects.first().provinces:
            provinces.append({'code': province.code, 'name': province.name})
        return Response(json.dumps(provinces), mimetype="application/json", status=200)


class CitiesApi(Resource):
    def get(self, province_id):
        cities = []
        for city in City.objects(province_id=province_id):
            cities.append({'code': city.code, 'name': city.name})
        return Response(json.dumps(cities), mimetype="application/json", status=200)
