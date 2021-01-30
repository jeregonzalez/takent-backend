from flask_restful import Resource

from database.models.offer import Postulant, Offer
from resources.helpers import user_helper
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_exists, validate_user_is_common


class PostulationApi(Resource):

    method_decorators = [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]

    def get(self):
        user = user_helper.get_user_from_jwt()
        postulations = Postulant.objects(postulant=user)
        result = []
        for postulation in postulations:
            offer = Offer.objects.get(postulants=postulation)
            result.append({
                'title': offer.title,
                'description': offer.description,
                'position': offer.position,
                'enterprise': offer.enterprise.fantasy_name,
                'address': offer.enterprise.address.format_response(),
                'postulation_date': postulation.postulation_date,
                'state': postulation.state.name
            })
        return result
