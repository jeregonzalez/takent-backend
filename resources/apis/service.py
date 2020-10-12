from flask import request
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, ValidationError, DoesNotExist, InvalidQueryError

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
