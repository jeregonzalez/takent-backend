from datetime import date

from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields, validates_schema, ValidationError

from resources.helpers import statistics_helper
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_exists, validate_user_is_enterprise

STATISTICS_FUNCTIONS_MAP = {
    'offers_per_month': statistics_helper.get_offers_per_month,
    'most_popular_offers': statistics_helper.get_offers_with_greater_postulants_amount,
    'offers_by_state': statistics_helper.get_offers_by_state,
    'postulants_by_age': statistics_helper.get_postulants_age,
    'postulants_by_month_and_state': statistics_helper.get_postulants_by_state_by_month
}


class StatisticSchema(Schema):
    date_from = fields.Date('%d/%m/%Y')
    date_to = fields.Date('%d/%m/%Y')

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data.get('date_from') and data.get('date_to') and data['date_from'] > data['date_to']:
            raise ValidationError('date_from must be lower than date_to')
        if data.get('date_to') and data['date_to'] > date.today():
            raise ValidationError('date_to must be lower or equal to current date')


schema = StatisticSchema()


class StatisticsApi(Resource):
    method_decorators = {
        'get': [validate_user_is_enterprise, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, statistic_name):
        args = request.args
        errors: dict = schema.validate(args)
        if errors:
            abort(400, errors=errors)
        params = schema.load(args)
        statistic_func = STATISTICS_FUNCTIONS_MAP.get(statistic_name)
        if not statistic_func:
            abort(404)
        return statistic_func(**params)
