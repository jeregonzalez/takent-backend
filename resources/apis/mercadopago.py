import mercadopago
import requests
from flask import request
from flask_restful import Resource, abort
from mongoengine import DoesNotExist

from database.models.parametric_docs import OfferPack
from database.models.payment import Payment
from database.models.user import EnterpriseUser
from resources.helpers import user_helper, password_helper, enterprise_helper
from resources.utils.decorators import authentication_required, validate_user_exists, \
    validate_headers
from resources.utils.exceptions import SaveException
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
        'post': [validate_user_exists, authentication_required, validate_headers]
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
        preference = {
            'items': [offer_pack_item],
            'external_reference': password_helper.get_random_alphanumeric_string(length=24),
            'payer': {
                'email': 'test_user_88688921@testuser.com'
            }
        }
        preference_result = mp.create_preference(preference)
        if preference_result.get('status') != 201:
            raise SaveException('Unable to get preference id')
        new_payment = {
            'external_reference': preference_result.get('response').get('external_reference'),
            'user': user_helper.get_user_from_jwt(),
            'offer_pack': offer_pack_obj.id,
            'quantity': offer_pack_item.get('quantity'),
            'price': offer_pack_item.get('unit_price') * offer_pack_item.get('quantity'),
            'preference_id': preference_result.get('response').get('id')
        }
        Payment(**new_payment).save()
        return Message.ok(preference_result)


class MPNotificationsApi(Resource):

    def post(self):
        body = request.get_json()
        notification_url = body.get('resource')
        if not notification_url:
            raise SaveException('Could not find notification url')
        response = requests.get(url=notification_url,
                                params={'access_token': ProjectVars.get_project_var('MP_ACCESS_TOKEN')})
        if response.status_code != 200:
            raise SaveException('Error getting notification')
        notification = response.json()
        external_reference = notification.get('collection').get('external_reference')
        payment = Payment.objects.get(external_reference=external_reference)
        payment.update(payment_status='approved')
        user = payment.user
        if isinstance(user, EnterpriseUser):
            enterprise = enterprise_helper.get_enterprise(user_account=user.id)
            offer_pack = OfferPack.objects.get(id=payment.offer_pack)
            offers_to_add = offer_pack.offers_quantity * payment.quantity
            enterprise.update(available_offers=enterprise.available_offers + offers_to_add)
        else:
            pass
        return Message.created()
