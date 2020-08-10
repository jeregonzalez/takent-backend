from flask import request
from flask_restful import Resource

from database.models.common import State
from database.models.offer import Offer
from resources.utils.decorators import authentication_required, validate_user_exists, validate_headers, offer_must_exist


class ReactivateOfferApi(Resource):
    method_decorators = {
        'post': [offer_must_exist, validate_user_exists, authentication_required, validate_headers]
    }

    def post(self, id=None):
        body = request.get_json()
        dict = {}

        offer = Offer.objects.get(id=id)

        if offer.state.name == 'in_selection':
            offer.update(state=State.objects.get(name='active'))

            return {'message': 'Offer reactivated successfully'}, 201
        elif offer.state.name == 'finished':
            offer.state = State.objects.get(name='active')
            offer.postulant = []
            if body:
                dict = offer.to_mongo()
                del dict['_id']

                for elem in body:
                    dict[elem] = body[elem]
                Offer(**dict).save()
                offer.update(state=State.objects.get(name='deleted'))

                return {'message': 'Offer reactivated successfully'}, 201
            else:
                dict = offer.to_mongo()
                del dict['_id']
                Offer(**dict).save()
                offer.update(state=State.objects.get(name='deleted'))

                return {'message': 'Offer reactivated successfully'}, 201

        return {'message': 'The state is not finished or in selection'}, 201
