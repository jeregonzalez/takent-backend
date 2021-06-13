from datetime import datetime
from threading import Thread

import mercadopago
import requests
from flask import request
from flask_restful import Resource, abort
from mongoengine import DoesNotExist

from database.models.mercadopago import Payment
from database.models.parametric_docs import MercadoPagoConcept
from database.models.service import Service
from database.models.user import EnterpriseUser
from resources.helpers import user_helper, enterprise_helper
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
                offer_packs = [MercadoPagoConcept.objects.get(id=_id)]
            except DoesNotExist:
                abort(400, message='Offer pack {} does not exist'.format(_id))
        else:
            offer_packs = [offer_pack for offer_pack in
                           MercadoPagoConcept.objects(id__contains='OFFER').order_by('+offers_quantity')]
        return offer_packs


class PreferredServiceApi(Resource):

    def get(self, _id=None):
        preferred_services = []
        if _id:
            try:
                preferred_services = [MercadoPagoConcept.objects.get(id=_id)]
            except DoesNotExist:
                abort(400, message='Preferred service {} does not exist'.format(_id))
        else:
            preferred_services = [preferred_service for preferred_service in
                                  MercadoPagoConcept.objects(id__contains='SERVICE')]
        return preferred_services


class MercadoPagoApi(Resource):
    method_decorators = {
        'post': [validate_user_exists, authentication_required, validate_headers]
    }

    def post(self):
        body = request.get_json()
        concept_id = body.get('concept_id')
        if not concept_id:
            abort(400, message='concept_id value required')
        try:
            concept_obj = MercadoPagoConcept.objects.get(id=concept_id)
        except DoesNotExist:
            abort(400, message='Concept {} does not exist'.format(concept_id))
        if 'OFFER' in concept_id:
            external_reference = '{}-{}'.format(concept_obj.id, user_helper.get_user_from_jwt(keys='user_account'))
        else:
            service_id = body.get('service_id')
            if not service_id:
                abort(400, message='service_id required')
            external_reference = '{}-{}-{}'.format(service_id, concept_obj.id,
                                                   user_helper.get_user_from_jwt(keys='user_account'))
        mp = mercadopago.MP(ProjectVars.get_project_var('MP_CLIENT_ID'),
                            ProjectVars.get_project_var('MP_CLIENT_SECRET'))
        concept_item = concept_obj.item_template
        preference = {
            'items': [concept_item],
            'external_reference': external_reference,
            'notification_url': ProjectVars.get_project_var('MP_NOTIFICATION_URL')
        }
        email = request.args.get('payer')
        if email:
            preference['payer'] = {
                'email': email
            }
        preference_result = mp.create_preference(preference)
        if preference_result.get('status') != 201:
            raise SaveException('Unable to get preference id')
        return Message.ok(preference_result)


class MPNotificationsApi(Resource):

    def post(self):
        params = request.args
        if params.get('topic') != 'payment':
            return Message.created()
        body = request.get_json()
        notification_url = body.get('resource')
        if not notification_url:
            raise SaveException('Could not find notification url')
        response = requests.get(url=notification_url,
                                params={'access_token': ProjectVars.get_project_var('MP_ACCESS_TOKEN')})
        if response.status_code != 200:
            raise SaveException('Error getting notification')

        def process():
            notification = response.json().get('collection')
            external_reference = notification.get('external_reference').split('-')
            if len(external_reference) == 2:
                service_id = None
                concept_id = external_reference[0]
                user_account = external_reference[1]
            else:
                service_id = external_reference[0]
                concept_id = external_reference[1]
                user_account = external_reference[2]
            kwargs = {
                'payment_id': notification.get('id'),
                'user': user_account,
                'concept_id': concept_id,
                'reason': notification.get('reason'),
                'amount': notification.get('total_paid_amount'),
                'status': notification.get('status'),
                'service_id': service_id
            }
            process_payment(**kwargs)
        Thread(target=process).start()
        return Message.created()


def process_payment(payment_id, user, concept_id, reason, amount, status, service_id=None):
    user = user_helper.get_user(user_account=user)
    payment_exists = bool(Payment.objects(payment_id=payment_id).count())
    if payment_exists:
        payment = Payment.objects.get(payment_id=payment_id)
        new_status = {
            'payment_date': datetime.today(),
            'payment_status': status
        }
        payment.update(**new_status)
        payment.status_history.create(**new_status)
        payment.save()
    else:
        payment = {
            'payment_id': payment_id,
            'user': user,
            'concept_id': concept_id,
            'reason': reason,
            'price': amount,
            'payment_status': status,
            'status_history': [
                {'status': status}
            ]
        }
        Payment(**payment).save()
    if status == 'approved':
        if 'OFFER' in concept_id and isinstance(user, EnterpriseUser):
            enterprise = enterprise_helper.get_enterprise(user_account=user.id)
            offer_pack = MercadoPagoConcept.objects.get(id=concept_id)
            offers_to_add = offer_pack.offers_quantity
            enterprise.update(available_offers=enterprise.available_offers + offers_to_add)
        else:
            service = Service.objects.get(id=service_id)
            service.update(preference=True)
