import mercadopago
from flask import request
from flask_restful import Resource, abort
from mongoengine import DoesNotExist

from database.models.parametric_docs import OfferPack
from resources.helpers.log_helper import LOGGER
from resources.utils.decorators import authentication_required, validate_user_exists, \
    validate_user_is_enterprise, validate_headers
from resources.utils.messages import Message
from resources.utils.project_vars import ProjectVars


class OfferPackApi(Resource):

    def get(self, _id=None):
        offer_packs = []
        if _id:
            try:
                offer_packs = [OfferPack.objects.get(id=_id)]
            except DoesNotExist:
                abort(400, message='Offer pack {} does not exist'.format(_id))
        else:
            offer_packs = [offer_pack for offer_pack in OfferPack.objects]
        return offer_packs


class MercadoPagoApi(Resource):

    method_decorators = {
        'post': [validate_user_is_enterprise, validate_user_exists, authentication_required, validate_headers]
    }

    def post(self):
        body = request.get_json()
        offer_pack = body.get('offer_pack')
        if not offer_pack:
            abort(400, message='offer_pack value required')
        try:
            offer_pack_obj = OfferPack.objects.get(id=offer_pack)
        except DoesNotExist:
            abort(400, message='offer_pack {} does not exist'.format(offer_pack))
        mp = mercadopago.MP(ProjectVars.get_project_var('MP_CLIENT_ID'),
                            ProjectVars.get_project_var('MP_CLIENT_SECRET'))
        offer_pack_item = offer_pack_obj.item_template
        offer_pack_item['quantity'] = body.get('quantity') if body.get('quantity') else 1
        LOGGER.info(offer_pack_item)
        preference = {
            'items': [offer_pack_item]
        }
        preference_result = mp.create_preference(preference)
        return Message.ok(preference_result)
