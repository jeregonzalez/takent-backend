from flask_restful import Resource

from database.models.service import Service
from resources.helpers import user_helper
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_exists
from resources.utils.exceptions import GetException


class AssessmentStatisticsApi(Resource):

    method_decorators = [validate_user_exists, authentication_required, validate_headers]

    def get(self, account):
        if not user_helper.user_exists(user_account=account, user_type='common'):
            raise GetException('User {} does not exist'.format(account))

        user = user_helper.get_user(user_account=account)
        services = Service.objects(publication_user=user)
        total_score = 0
        total_assessments = 0
        for service in services:
            for service_request in service.service_requests:
                if not service_request.score:
                    continue
                total_assessments += 1
                total_score += service_request.score
        average_score = total_score / total_assessments if total_assessments != 0 else 0
        result = {
            'total_assessments': total_assessments,
            'average_score': average_score
        }
        return result
