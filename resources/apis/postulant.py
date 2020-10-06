from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist

from database.models.offer import Offer, Postulant
from database.models.parametric_docs import State
from resources.helpers import user_helper
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException
from resources.utils.messages import Message


class PostulantApi(Resource):
    # method_decorators = {
    #     'get': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
    #     'post': [validate_user_exists, authentication_required, validate_headers],
    #     'put': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
    #     'delete': [validate_user_exists, authentication_required, validate_headers]
    # }

    def get(self, id_offer=None):
        offer = Offer.objects.get(id=id_offer)
        data = []
        for postulant in offer.postulants:
            aux = {'id': postulant.id, 'account': postulant.postulant.to_mongo(), 'state': postulant.state.to_mongo()}
            del aux['account']['password']
            data.append(aux)

        return Message.ok(data)

    def post(self, id_offer=None):
        body = {}
        try:
            offer = Offer.objects.get(id=id_offer)
            body['postulant'] = user_helper.get_user_from_jwt()
            postulant = Postulant(**body).save()
            offer.update(push__postulants=postulant)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.ok(postulant.postulant.account)

    def put(self, id_postulant=None):
        body = request.get_json()

        try:
            body['state'] = State.objects.get(name=body['state'])
            Postulant.get(id=id_postulant).update(**body)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        except DoesNotExist:
            abort(400, message='State does not exist')

        return Message.update()

    def delete(self, id_offer):
        # id offer es el id del postulante
        try:
            Postulant.objects.get(id=id_offer).delete()
        except DoesNotExist:
            abort(400, message='Postulant does not exist')
        return Message.delete()
