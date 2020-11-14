from flask_restful import Resource

from database.models.parametric_docs import Sector


class SectorApi(Resource):
    def get(self):
        return Sector.objects.order_by('+name')
