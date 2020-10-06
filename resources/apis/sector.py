from flask_restful import Resource

from database.models.parametric_docs import Sector


class SectorApi(Resource):
    def get(self):
        return [sector for sector in Sector.objects()]
