from threading import Thread

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.offer import Offer, Postulant
from database.models.parametric_docs import StatePostulant
from resources.helpers import user_helper, enterprise_helper
from resources.helpers.email_helper.email_helper import EmailContacted, EmailPreselected, EmailDiscarded
from resources.helpers.design_patterns.state.postulant import PostulantStateManager
from resources.helpers.notifications_helper import StatePostulationChangedNotification
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_offer_exists, validate_user_is_enterprise, validate_user_is_common, validate_postulant_exists
from resources.utils.exceptions import SaveException, \
    UpdateException
from resources.utils.messages import Message


class PostulantApi(Resource):
    method_decorators = {
        'get': [validate_postulant_exists, validate_offer_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'post': [validate_user_exists, validate_user_is_enterprise, authentication_required, validate_headers],
        'put': [validate_postulant_exists, validate_offer_exists, validate_user_is_enterprise, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_postulant_exists, validate_offer_exists, validate_user_is_enterprise, validate_user_exists,
                   authentication_required, validate_headers]
    }

    def get(self, id_offer=None, id_postulant=None):
        offer = Offer.objects.get(id=id_offer)
        postulants = offer.postulants
        if id_postulant:
            postulants = list(filter(lambda x: str(x.id) == id_postulant, postulants))[0]
        return postulants

    def put(self, id_offer=None, id_postulant=None):
        body = request.get_json()
        try:
            if body.get('state'):
                body['state'] = StatePostulant.objects.get(name=body['state'])
            Postulant.objects.get(id=id_postulant).update(**body)
        except (DoesNotExist, FieldDoesNotExist, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, id_offer=None, id_postulant=None):
        offer = Offer.objects.get(id=id_offer)
        postulant = Postulant.objects.get(id=id_postulant)
        offer.update(pull__postulants=postulant)
        postulant.delete()
        return Message.deleted()


class PostulateApi(Resource):
    method_decorators = {
        'post': [validate_offer_exists, validate_user_is_common, validate_user_exists, authentication_required,
                 validate_headers]
    }

    def post(self, id_offer=None):
        offer = Offer.objects.get(id=id_offer)
        if any(postulant.postulant == user_helper.get_user_from_jwt() for postulant in offer.postulants):
            abort(400, message='Already postulated')
        postulant_info = {
            'postulant': user_helper.get_user_from_jwt()
        }
        try:
            postulant = Postulant(**postulant_info)
            postulant.save()
            offer.update(push__postulants=postulant)
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()


class StatePostulantApi(Resource):
    ACTION_STATE_MAP = {
        'pre_select': 'pre_selected',
        'contact': 'contacted',
        'discard': 'discarded'
    }

    method_decorators = {
        'post': [validate_postulant_exists, validate_offer_exists, validate_user_is_enterprise, validate_user_exists,
                 authentication_required, validate_headers]
    }

    def post(self, id_offer=None, id_postulant=None, action=None):
        state = self.ACTION_STATE_MAP.get(action)
        if not state or state not in [state.name for state in StatePostulant.objects]:
            raise SaveException('State {} not exists'.format(state))
        body = request.get_json()
        offer = Offer.objects.get(id=id_offer)
        postulant = Postulant.objects.get(id=id_postulant)
        enterprise = enterprise_helper.get_enterprise()
        state_manager = PostulantStateManager(postulant, enterprise)
        try:
            state_manager.change(state=state)
        except Exception as e:
            raise SaveException(e)
        if action == 'pre_select':
            target = lambda: EmailPreselected(destination_email=postulant.postulant.id,
                                              enterprise_name=enterprise.fantasy_name,
                                              user_name=postulant.postulant.name,
                                              offer_name=offer.title).send_email()
        elif action == 'contact':
            target = lambda: EmailContacted(destination_email=postulant.postulant.id,
                                            enterprise_name=enterprise.fantasy_name,
                                            user_name=postulant.postulant.name,
                                            email_contact=enterprise.contact_email,
                                            comment=body.get('comment'),
                                            offer_name=offer.title).send_email()
        else:
            target = lambda: EmailDiscarded(destination_email=postulant.postulant.id,
                                            enterprise_name=enterprise.fantasy_name,
                                            user_name=postulant.postulant.name,
                                            offer_name=offer.title).send_email()
        Thread(target=target).start()

        if postulant.state.name in ('pre_selected', 'contacted'):
            StatePostulationChangedNotification(user=postulant.postulant,
                                                offer_name=offer.title,
                                                state_name=postulant.state.name)

        return Message.created()
