from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.feedback import Feedback
from resources.utils.exceptions import SaveException
from resources.utils.messages import Message


class FeedbackSchema(Schema):
    email = fields.Email(required=True)
    text = fields.String(required=True)


schema = FeedbackSchema()


class FeedbackApi(Resource):

    def post(self):
        body = request.get_json()
        errors: dict = schema.validate(body)
        if errors:
            abort(400, errors=errors)
        body = schema.load(body)
        try:
            Feedback(**body).save()
        except (FieldDoesNotExist, ValidationError) as e:
            raise SaveException(e)
        return Message.created()
