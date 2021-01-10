from flask_restful import Resource, abort

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


class StatisticsApi(Resource):
    method_decorators = {
        'get': [validate_user_is_enterprise, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, statistic_name):
        statistic_func = STATISTICS_FUNCTIONS_MAP.get(statistic_name)
        if not statistic_func:
            abort(404)
        return statistic_func()
