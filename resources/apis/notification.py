from flask import request
from flask_restful import Resource
from mongoengine import DoesNotExist, InvalidQueryError, ValidationError

from database.models.notification import Notification
from resources.helpers import user_helper
from resources.utils.decorators import validate_headers, authentication_required, \
    validate_user_exists
from resources.utils.exceptions import GetException, UpdateException
from resources.utils.messages import Message


class NotificationApi(Resource):

    method_decorators = [validate_user_exists, authentication_required, validate_headers]

    def get(self, _id=None):
        user = user_helper.get_user_from_jwt()

        if _id:
            try:
                return Notification.objects.get(id=_id, user=user)
            except DoesNotExist as e:
                raise GetException(e)

        notifications = Notification.objects(user=user).order_by('-date')[:15]

        return notifications

    def post(self):
        user = user_helper.get_user_from_jwt()
        Notification.objects(user=user).update(viewed=True)
        return Message.created()

    def put(self, _id=None):
        user = user_helper.get_user_from_jwt()
        if not _id or not bool(Notification.objects(id=_id, user=user)):
            raise UpdateException('{} notification does not exist'.format(_id))
        try:
            body = request.get_json()
            Notification.objects.get(id=_id).update(**body)
        except (InvalidQueryError, ValidationError) as e:
            raise UpdateException(e)
        return Message.updated()
