from flask_restful import Resource

from resources.helpers import mongodb_helper
from resources.utils.messages import Message


class MongoApi(Resource):
    def get(self):
        mongodb_helper.upload_data()
        return Message.ok()
