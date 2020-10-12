from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist, InvalidQueryError

from database.models.common import Image
from database.models.parametric_docs import StateService
from database.models.service import Service
from resources.helpers import service_helper, user_helper
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_service_exists, validate_user_is_common
from resources.utils.exceptions import GetException, SaveException, UpdateException
from resources.utils.messages import Message


class ServiceApi(Resource):
    method_decorators = {
        'get': [validate_service_exists, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_is_common, validate_user_exists, authentication_required, validate_headers],
        'put': [validate_service_exists, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_service_exists, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, service_id=None):
        if service_id:
            services = Service.objects.get(id=service_id)
        else:
            ok, bad_keys = service_helper.validate_filter_keys(keys=list(request.args.keys()))
            if not ok:
                raise GetException('{} are not valid keys'.format(bad_keys))
            filters = list(request.args.items())
            services = service_helper.filter_services(filters=filters)
        return services

    def post(self):
        body = request.get_json()
        body['publication_user'] = user_helper.get_user_from_jwt()
        try:
            Service(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()

    def put(self, service_id=None):
        body = request.get_json()
        if body.get('state'):
            try:
                body['state'] = StateService.objects.get(name=body['state'])
            except DoesNotExist as e:
                return UpdateException(e)
        try:
            Service.objects.get(id=service_id).update(**body)
        except (InvalidQueryError, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, service_id=None):
        Service.objects.get(id=service_id).delete()
        return Message.deleted()


class ServiceImagesApi(Resource):
    method_decorators = {
        'get': [validate_service_exists, validate_user_exists, authentication_required, validate_headers],
        'post': [validate_service_exists, validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_service_exists, validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, id_offer):
        quantity = request.args.get('quantity')
        offer = Service.objects.get(id=id_offer)
        images = [image.base64 for image in offer.images if image.base64]
        return images[:int(quantity)] if quantity else images

    def post(self, id_offer):
        images = request.get_json().get('images')
        if not images:
            abort(400, message='No images sent')
        service = Service.objects.get(id=id_offer)
        if service.images:
            for image in service.images:
                image.delete()
        images_obj = []
        for image in images:
            new_image = Image(base64=image).save()
            images_obj.append(new_image)
        service.update(images=images_obj)
        return Message.created()

    def delete(self, id_offer):
        service = Service.objects.get(id=id_offer)
        if service.images:
            for image in service.images:
                service.images.remove(image)
                image.delete()
            service.save()
        return Message.deleted()
