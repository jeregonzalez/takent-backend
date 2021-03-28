from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields, validate

from database.models.user import CommonUser
from resources.helpers import user_helper, geolocation_helper
from resources.utils.decorators import validate_headers, authentication_required, validate_user_exists

OBJ_TYPES = ['offers', 'services']


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
        near_entities: list = geolocation_helper.get_near_offers(user=user, **params) if obj_type == 'offers' else \
            geolocation_helper.get_near_services(user=user, **params)
        response = {
            'are_near': bool(near_entities),
            'quantity': len(near_entities),
            'params': params
        }
        return response
