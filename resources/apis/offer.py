from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.common import State, JobType
from database.models.offer import Offer
from resources.helpers.user_helper import get_user
from resources.utils.decorators import authentication_required, user_must_exist, validate_headers, \
    offer_active_must_exist, offer_must_exist
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException


class OfferApi(Resource):
    method_decorators = {
        'get': [offer_active_must_exist, user_must_exist, authentication_required, validate_headers],
        'post': [user_must_exist, authentication_required, validate_headers],
        'put': [offer_must_exist, user_must_exist, authentication_required, validate_headers],
        'delete': [offer_must_exist, user_must_exist, authentication_required, validate_headers]
    }

    def get(self, id=None):

        offers = []

        if id:
            offers.append(Offer.objects.get(id=id, state=State.objects.get(name='active'), publication_user=get_user()))
        else:
            for offer in Offer.objects(state=State.objects.get(name='active'), publication_user=get_user()):
                offers.append(offer)

        return offers, 200

    def post(self):
        body = request.get_json()

        body['publication_user'] = get_user()

        try:
            offer = Offer(**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return {'message': 'Offer created successfully'}, 201

    def put(self, id=None):
        body = request.get_json()

        if 'publication_user' in body:
            return {'message': 'Publication user cannot be modified'}

        try:
            if 'state' in body:
                body['state'] = State.objects.get(name=body['state'])

            if 'job_type' in body:
                body['job_type'] = JobType.objects.get(name=body['job_type'])

            Offer.objects.get(id=id).update(**body)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return {'message': 'Offer updated'}

    def delete(self, id=None):

        message = {}
        if id:
            offer = Offer.objects.get(id=id, state=State.objects.get(name='active'), publication_user=get_user())
            offer.update(state=State.objects.get(name='inactive'))
            message = '', 204
        else:
            message = {'message': 'No offer selected'}, 400

        return message
