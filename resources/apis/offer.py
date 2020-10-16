from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError, DoesNotExist

from database.models.common import Image
from database.models.offer import Offer
from database.models.parametric_docs import StateOffer
from resources.helpers import user_helper, offer_helper, enterprise_helper
from resources.helpers.design_patterns.state.offer import OfferStateManager
from resources.utils.decorators import authentication_required, validate_user_exists, validate_headers, \
    validate_offer_exists
from resources.utils.exceptions import SaveException, UpdateException, GetException
from resources.utils.messages import Message


class OfferApi(Resource):
    method_decorators = {
        'get': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, id_offer=None):
        if id_offer:
            offers = Offer.objects.get(id=id_offer)
        else:
            ok, bad_keys = offer_helper.validate_filter_keys(keys=list(request.args.keys()))
            if not ok:
                raise GetException('{} are not valid keys'.format(bad_keys))
            user_info = user_helper.get_user_from_jwt(keys=['user_account', 'user_type'])
            filters = list(request.args.items())
            if user_info['user_type'] == 'enterprise':
                filters.append(
                    ('enterprise', str(enterprise_helper.get_enterprise(user_account=user_info['user_account']).id)))
            else:
                filters.append(('state', 'active'))
            offers = offer_helper.filter_offers(filters=filters)
        return offers

    def post(self):
        body = request.get_json()
        body['publication_user'] = user_helper.get_user_from_jwt()
        body['enterprise'] = enterprise_helper.get_enterprise()
        images = body.get('images')
        if images:
            del body['images']
        try:
            new_offer = Offer(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        images_obj = []
        if images:
            for image in images:
                new_image = Image(base64=image).save()
                images_obj.append(new_image)
            if images_obj:
                new_offer.update(images=images_obj)
        return Message.created()

    def put(self, id_offer=None):
        offer = Offer.objects.get(id=id_offer)
        body = request.get_json()
        if body.get('state'):
            state = body.get('state')
            if state not in [state.name for state in StateOffer.objects]:
                raise UpdateException('State {} not exists'.format(state))
            state_manager = OfferStateManager(offer.state.name)
            try:
                state_manager.change(state=state)
            except Exception as e:
                raise UpdateException(e)
            body['state'] = StateOffer.objects.get(name=state_manager.state.name)
        try:
            offer.update(**body)
        except (InvalidQueryError, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, id_offer=None):
        Offer.objects.get(id=id_offer).delete()
        return Message.deleted()


class OfferImagesApi(Resource):
    method_decorators = {
        'get': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_offer_exists, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, id_offer):
        quantity = request.args.get('quantity')
        offer = Offer.objects.get(id=id_offer)
        images = [image.base64 for image in offer.images if image.base64]
        return images[:int(quantity)] if quantity else images

    def post(self, id_offer):
        images = request.get_json().get('images')
        if not images:
            abort(400, message='No images sent')
        offer = Offer.objects.get(id=id_offer)
        if offer.images:
            for image in offer.images:
                image.delete()
        images_obj = []
        for image in images:
            new_image = Image(base64=image).save()
            images_obj.append(new_image)
        offer.update(images=images_obj)
        return Message.created()

    def delete(self, id_offer):
        offer = Offer.objects.get(id=id_offer)
        if offer.images:
            for image in offer.images:
                offer.images.remove(image)
                image.delete()
            offer.save()
        return Message.deleted()
