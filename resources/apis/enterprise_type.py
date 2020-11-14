from flask_restful import Resource

from database.models.parametric_docs import EnterpriseType


class EnterpriseTypeApi(Resource):
    def get(self):
        return [enterprise_type for enterprise_type in EnterpriseType.objects]
