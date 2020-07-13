import datetime
import json

from bson import ObjectId
from flask_mongoengine import Document

from database.models.users import User

HIDE_FIELDS = ['password', 'profile_photo', 'curriculum']


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, User):
            response = obj.to_mongo()
            for field in HIDE_FIELDS:
                response.pop(field, None)
            return response
        if issubclass(obj.__class__, Document):
            return obj.to_mongo()
        elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
