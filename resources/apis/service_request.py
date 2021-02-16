from flask import request
from flask_restful import Resource
from mongoengine import DoesNotExist, FieldDoesNotExist, ValidationError

from database.models.parametric_docs import StateServiceRequest
from database.models.service import Service, ServiceRequest
from resources.helpers import user_helper
from resources.helpers.design_patterns.state.service_request import ServiceRequestStateManager
from resources.helpers.notifications_helper import RequestedServiceNotification
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists, \
    validate_user_is_common, validate_service_exists, validate_service_request_exists
from resources.utils.exceptions import UpdateException, SaveException
from resources.utils.messages import Message


class ServiceRequestApi(Resource):
    method_decorators = {
        'get': [validate_service_request_exists, validate_service_exists, validate_user_is_common, validate_user_exists,
                authentication_required, validate_headers],
        'post': [validate_user_exists, validate_user_is_common, authentication_required, validate_headers],
        'put': [validate_service_request_exists, validate_service_exists, validate_user_is_common, validate_user_exists,
                authentication_required, validate_headers],
        'delete': [validate_service_request_exists, validate_service_exists, validate_user_is_common,
                   validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, service_id=None, service_request_id=None):
        service = Service.objects.get(id=service_id)
        service_requests = service.service_requests
        if service_request_id:
            service_requests = list(filter(lambda x: str(x.id) == service_request_id, service_requests))[0]
        return service_requests

    def put(self, service_id=None, service_request_id=None):
        body = request.get_json()
        service_request = ServiceRequest.objects.get(id=service_request_id)
        try:
            if body.get('state'):
                state = body.get('state')
                if state not in [state.name for state in StateServiceRequest.objects]:
                    raise UpdateException('State {} not exists'.format(state))
                state_manager = ServiceRequestStateManager(service_request.state.name)
                try:
                    state_manager.change(state=state)
                except Exception as e:
                    raise UpdateException(e)
                body['state'] = StateServiceRequest.objects.get(name=state_manager.state.name)
            ServiceRequest.objects.get(id=service_request_id).update(**body)
        except (DoesNotExist, FieldDoesNotExist, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()

    def delete(self, service_id=None, service_request_id=None):
        service = Service.objects.get(id=service_id)
        service_request = ServiceRequest.objects.get(id=service_request_id)
        service.update(pull__service_requests=service_request)
        service_request.delete()
        return Message.deleted()


class NewServiceRequestApi(Resource):
    method_decorators = {
        'post': [validate_service_exists, validate_user_is_common, validate_user_exists, authentication_required,
                 validate_headers]
    }

    def post(self, service_id=None):
        service = Service.objects.get(id=service_id)
        user_info = {
            'user': user_helper.get_user_from_jwt()
        }
        try:
            service_request = ServiceRequest(**user_info)
            service_request.save()
            service.update(push__service_requests=service_request)
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)

        RequestedServiceNotification(user=service.publication_user, service_name=service.title).save()

        return Message.created()


class MyServiceRequestsApi(Resource):

    method_decorators = [validate_user_is_common, validate_user_exists, authentication_required, validate_headers]

    def get(self):
        user = user_helper.get_user_from_jwt()
        service_requests = ServiceRequest.objects(user=user, score=None)
        result = []
        for service_request in service_requests:
            service = Service.objects.get(service_requests=service_request)
            result.append({
                '_id': service_request.id,
                'request_date': service_request.request_date,
                'state': service_request.state.name,
                'score': service_request.score,
                'states_history': service_request.states_history,
                'service': service
            })
        return result
