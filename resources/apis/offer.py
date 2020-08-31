from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.common import State, JobType
from database.models.offer import Offer
from resources.helpers import user_helper, offer_helper
from resources.utils.decorators import authentication_required, validate_user_exists, \
    validate_headers, offer_must_exist, validate_offer_args
from resources.utils.exceptions import SchemaValidationErrorException, \
    MissingRequiredFieldsException


class OfferApi(Resource):
    method_decorators = {
        'get': [validate_offer_args, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'delete': [offer_must_exist, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        filters = request.args.items()
        return [offer for offer in offer_helper.filter_offers(filters)]

    def post(self):
        body = request.get_json()

        body['publication_user'] = user_helper.get_user_from_jwt()

        try:
            Offer(**body).save()
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
        except InvalidQueryError:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return {'message': 'Offer updated'}

    def delete(self, id=None):
        if id:
            offer = Offer.objects.get(id=id, state=State.objects.get(name='active'),
                                      publication_user=user_helper.get_user_from_jwt())
            offer.update(state=State.objects.get(name='inactive'))
            message = '', 204
        else:
            message = {'message': 'No offer selected'}, 400

        return message
