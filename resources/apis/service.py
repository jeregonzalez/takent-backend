from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError, InvalidQueryError

from database.models.common import Image
from database.models.parametric_docs import StateService
from database.models.service import Service
from resources.helpers import service_helper, user_helper, notifications_config_helper
from resources.helpers.design_patterns.state.service import ServiceStateManager
from resources.helpers.notifications_helper import SuggestPreferredServiceNotification
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_exists, \
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
        user = user_helper.get_user_from_jwt()
        body = request.get_json()
        body['publication_user'] = user
        images = body.get('images')
        if images:
            del body['images']
        try:
            new_service = Service(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        images_obj = []
        if images:
            for image in images:
                new_image = Image(base64=image).save()
                images_obj.append(new_image)
            if images_obj:
                new_service.update(images=images_obj)

        if new_service.state.name == 'active' and notifications_config_helper.is_notification_active(
                user=user, notification_type='suggest_preferred_service'):
            SuggestPreferredServiceNotification(entity=new_service.id,
                                                user=user,
                                                service_name=new_service.title).save()

        return {'_id': new_service.id}, 201

    def put(self, service_id=None):
        service = Service.objects.get(id=service_id)
        body = request.get_json()
        if body.get('state'):
            state = body.get('state')
            if state not in [state.name for state in StateService.objects]:
                raise UpdateException('State {} not exists'.format(state))
            state_manager = ServiceStateManager(service.state.name)
            try:
                state_manager.change(state=state)
            except Exception as e:
                raise UpdateException(e)
            body['state'] = StateService.objects.get(name=state_manager.state.name)
        try:
            service.update(**body)
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

    def get(self, service_id):
        quantity = request.args.get('quantity')
        offer = Service.objects.get(id=service_id)
        images = [image.base64 for image in offer.images if image.base64]
        return images[:int(quantity)] if quantity else images

    def post(self, service_id):
        images = request.get_json().get('images')
        if not images:
            abort(400, message='No images sent')
        service = Service.objects.get(id=service_id)
        if service.images:
            for image in service.images:
                image.delete()
        images_obj = []
        for image in images:
            new_image = Image(base64=image).save()
            images_obj.append(new_image)
        service.update(images=images_obj)
        return Message.created()

    def delete(self, service_id):
        service = Service.objects.get(id=service_id)
        if service.images:
            for image in service.images:
                service.images.remove(image)
                image.delete()
            service.save()
        return Message.deleted()
