from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.offer import Offer, Postulant
from database.models.parametric_docs import StatePostulant
from resources.helpers import user_helper
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
            postulants = filter(lambda x: x.id == id_postulant, postulants)
        return postulants

    def put(self, id_offer=None, id_postulant=None):
        body = request.get_json()
        try:
            if body.get('state'):
                body['state'] = StatePostulant.objects.get(id=body['state'])
            Postulant.objects.get(id=id_postulant).update(**body)
        except (DoesNotExist, FieldDoesNotExist, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, id_offer=None, id_postulant=None):
        offer = Offer.objects.get(id=id_offer)
        offer.update(pull__postulants=id_postulant)
        offer.save()
        Postulant.objects.get(id=id_postulant).delete()
        return Message.deleted()


class PostulateApi(Resource):
    method_decorators = {
        'post': [validate_offer_exists, validate_user_is_common, validate_user_exists, authentication_required,
                 validate_headers]
    }

    def post(self, id_offer=None):
        offer = Offer.objects.get(id=id_offer)
        postulant_info = {
            'postulant': user_helper.get_user_from_jwt()
        }
        print(postulant_info)
        try:
            postulant = Postulant(**postulant_info)
            postulant.save()
            offer.update(push__postulants=postulant)
            offer.save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()
