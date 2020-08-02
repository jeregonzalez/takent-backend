import datetime
import json

from bson import ObjectId
from flask_mongoengine import Document

from database.models.user import User, CommonUser

HIDE_FIELDS = ['password', 'profile_photo', 'curriculum']


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, User):
            response = obj.to_mongo()
            for field in HIDE_FIELDS:
                response.pop(field, None)
            if isinstance(obj, CommonUser) and obj.address and obj.address.city:
                response['address'] = obj.address.format_response()
            return response
        elif issubclass(obj.__class__, Document):
            return obj.to_mongo()
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
