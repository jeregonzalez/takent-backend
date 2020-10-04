import datetime

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.common import State, Image
from database.models.enterprise import Enterprise
from database.models.offer import Offer
from resources.helpers import user_helper, offer_helper
from resources.utils.decorators import authentication_required, validate_user_exists, \
    validate_headers, offer_must_exist, validate_offer_args
from resources.utils.exceptions import SchemaValidationErrorException, \
    MissingRequiredFieldsException
from resources.utils.messages import Message


class OfferApi(Resource):
    method_decorators = {
        'get': [validate_offer_args, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'delete': [offer_must_exist, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self):
        filters = list(request.args.items())
        offers = []
        i = 0
        for offer in offer_helper.filter_offers(filters):
            json_offer = offer.to_mongo()
            json_offer['postulants_quantity'] = len(offer.postulants)
            json_offer['remaining_days'] = offer.duration - (datetime.datetime.today() - offer.publication_date).days
            offers.append(json_offer)
        return Message.ok(response=offers)

    def post(self):
        body = request.get_json()
        body['publication_user'] = user_helper.get_user_from_jwt()

        if Enterprise.objects(admin_user=user_helper.get_user_from_jwt()).count():
            enterprise = Enterprise.objects.get(admin_user=user_helper.get_user_from_jwt())
            body['enterprise'] = enterprise
        else:
            for enterprise in Enterprise.objects(state=State.objects.get(name='active')):
                if user_helper.get_user_from_jwt() in enterprise.admin_user:
                    body['enterprise'] = enterprise
                    break

        try:
            list_images = []
            for image in body.get('images'):
                data = Image(base64=image)
                data.save()
                list_images.append(data)

            body['images'] = list_images

            Offer(**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return {'message': 'Offer created successfully'}, 201

    def put(self, id_offer=None):
        body = request.get_json()
        if 'publication_user' in body:
            return {'message': 'Publication user cannot be modified'}
        try:
            if 'state' in body:
                body['state'] = State.objects.get(name=body['state'])
            Offer.objects.get(id=id_offer).update(**body)
        except InvalidQueryError:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return {'message': 'Offer updated'}

    def delete(self, id_offer=None):
        if id:
            offer = Offer.objects.get(id=id_offer, state=State.objects.get(name='active'),
                                      publication_user=user_helper.get_user_from_jwt())
            offer.update(state=State.objects.get(name='inactive'))
            message = '', 204
        else:
            message = {'message': 'No offer selected'}, 400
        return message


class OfferImagesApi(Resource):
    method_decorators = {
        'get': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'post': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'put': [offer_must_exist, validate_user_exists, authentication_required, validate_headers],
        'delete': [offer_must_exist, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, id_offer):
        data = []
        images = Offer.objects.get(id=id_offer).images
        if not images:
            abort(400, message='Not found images')
        for image in images:
            aux = {'id': image.id, 'image': image.base64}
            data.append(aux)
        return Message.ok(data)

    def post(self, id_offer):
        body = request.get_json()

        list_images = []
        for image in body.get('images'):
            data = Image(base64=image)
            data.save()
            list_images.append(data)

        offer = Offer.objects.get(id=id_offer)
        images = offer.images
        images.extend(list_images)
        offer.update(images=images)

        return Message.added('Images')

    def delete(self, id_offer, id_image):
        # id_offer es id_image

        if not Image.objects(id=id_image).count():
            abort(400, message='Image does not exist')

        image = Image.objects.get(id=id_image)
        Offer.objects.get(id=id_offer).update(pull__images=image)
        image.delete()

        return Message.delete()