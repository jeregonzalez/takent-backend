from typing import Union

from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields, validate

from database.models.user import CommonUser
from resources.helpers import user_helper, geolocation_helper, notifications_config_helper, notifications_helper
from resources.helpers.notifications_helper import NearOffersNotification, NearServicesNotification
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists

OBJ_TYPES = ['offers', 'services']
NOTIFICATION_DISTANCE_LIMIT = 500
NOTIFICATION_DAYS_LIMIT = 4


class GeolocationSchema(Schema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    radius = fields.Float(missing=300)
    filter_by_preferred = fields.Boolean(missing=True)


schema = GeolocationSchema()


class GeolocationApi(Resource):

    method_decorators = {
        'get': [validate_user_exists, authentication_required, validate_headers],
        'post': [validate_user_exists, authentication_required, validate_headers],
        'put': [validate_user_exists, authentication_required, validate_headers],
        'delete': [validate_user_exists, authentication_required, validate_headers]
    }

    def get(self, obj_type: str) -> dict:
        if obj_type not in OBJ_TYPES:
            abort(404)
        errors: dict = schema.validate(request.args)
        if errors:
            abort(400, errors=errors)
        params: dict = schema.load(request.args)

        user: CommonUser = user_helper.get_user_from_jwt()

        notification_error: str = validate_send_notification(
            user,
            'near_{}'.format(obj_type),
            (params.get('latitude'), params.get('longitude'))
        )
        if notification_error:
            return {'validation_error': notification_error}

        near_entities: list = geolocation_helper.get_near_offers(user=user, **params) if obj_type == 'offers' else \
            geolocation_helper.get_near_services(user=user, **params)
        response = {
            'are_near': bool(near_entities),
            'quantity': len(near_entities),
            'params': params
        }
        if response.get('are_near'):
            (NearOffersNotification if obj_type == 'offers' else NearServicesNotification)(user=user,
                                                                                           info=response).save()
        return response


def validate_send_notification(user: CommonUser, notification_type: str, current_location: tuple) -> Union[None, str]:
    is_notification_active = notifications_config_helper.is_notification_active(user=user,
                                                                                notification_type=notification_type)
    if not is_notification_active:
        return 'notifications for {} are disabled'.format(notification_type)

    days_from_last_notification: int = notifications_helper.get_days_from_last_notification(user, notification_type)
    location_from_last_notification = notifications_helper.get_location_from_last_notification(user, notification_type)
    is_near: bool = geolocation_helper.is_near(
        current_location, location_from_last_notification, NOTIFICATION_DISTANCE_LIMIT
    )

    if is_near and days_from_last_notification < NOTIFICATION_DAYS_LIMIT:
        return 'too near from last notification location'
