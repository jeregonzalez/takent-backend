from flask_restful import Resource

from database.models.parametric_docs import Profession


class ProfessionApi(Resource):
    def get(self):
        return [profession for profession in Profession.objects]