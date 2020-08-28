from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError, Q

from database.models.common import State, JobType
from database.models.offer import Offer
from resources.helpers import user_helper
from resources.utils.decorators import authentication_required, validate_user_exists, validate_headers, \
    offer_id_state_must_exist, offer_must_exist, state_must_exist, validate_attributes
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException


class OfferApi(Resource):
    method_decorators = {
        'get': [offer_id_state_must_exist, validate_user_exists, validate_attributes,
                authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'delete': [offer_must_exist, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        offers = []
        attr = request.args.to_dict()
        attr['publication_user'] = user_helper.get_user_from_jwt()
        states = {'1': 'active', '2': 'inactive', '3': 'in_selection', '4': 'finished', '5': 'deleted'}
        aux = []
        response = []

        if attr.get('state'):
            aux = attr['state'].split(',')

        if attr.get('title'):
            attr['title__icontains'] = attr.pop('title')

        if attr.get('description'):
            attr['description__icontains'] = attr.pop('description')

        if attr.get('experience_offer'):
            attr['experience_offer__icontains'] = attr.pop('experience_offer')

        if attr.get('job_type'):
            if JobType.objects(name=attr['job_type']):
                attr['job_type'] = JobType.objects.get(name=attr['job_type'])

        if attr.get('language'):
            language = attr['language']
            attr['language__match'] = attr.pop('language')
            attr['language__match'] = {'name__icontains': language}

        if not attr:
            response = Offer.objects(publication_user=user_helper.get_user_from_jwt()).order_by('-publication_date')
        else:
            if attr.get('state'):
                for st in aux:
                    attr['state'] = State.objects.get(name=states[st])
                    response.extend(Offer.objects(**attr).order_by('-publication_date'))
            else:
                response = Offer.objects(**attr).order_by('-publication_date')

        if not response:
            return {'message': 'No results found'}, 200

        for offer in response:
            offers.append(offer)

        return offers, 200

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
        except FieldDoesNotExist:
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
