from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.offer import Offer
from resources.helpers import user_helper, offer_helper, enterprise_helper
from resources.utils.decorators import authentication_required, validate_user_exists, validate_headers, \
    validate_offer_exists
from resources.utils.exceptions import SaveException, UpdateException
from resources.utils.messages import Message


class OfferApi(Resource):

    method_decorators = {
        'get': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, id_offer=None):
        if id_offer:
            offers = Offer.objects.get(id=id_offer)
        else:
            if any(key not in offer_helper.get_fields() for key, value in request.args.items()):
                abort(400, message='Any attribute in the filter is invalid')
            filters = list(request.args.items())
            offers = offer_helper.filter_offers(filters)
        return Message.ok(message=offers)

    def post(self):
        body = request.get_json()
        body['publication_user'] = user_helper.get_user_from_jwt()
        body['enterprise'] = enterprise_helper.get_enterprise()
        try:
            Offer(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()

    def put(self, id_offer=None):
        body = request.get_json()
        try:
            Offer.objects.get(id=id_offer).update(**body)
        except (InvalidQueryError, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, id_offer=None):
        Offer.objects.get(id=id_offer).delete()
        return Message.deleted()
