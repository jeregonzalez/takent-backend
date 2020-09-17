from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.common import Sector
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException
from resources.utils.messages import Message


class SectorApi(Resource):
    def get(self):
        if not request.args.get('name'):
            return Message.ok([sector for sector in Sector.objects()])
        return Message.ok([sector for sector in Sector.objects(name__icontains=request.args.get('name'))])

    def post(self):
        body = request.get_json()

        try:
            sector = Sector(**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.created(sector.name)

    def put(self, id=None):
        if not id or len(id) != 24 or not Sector.objects(id=id).count():
            abort(400, message='Sector not found')
        body = request.get_json()

        if body.get('name') and Sector.objects(name=body.get('name')).count():
            abort(400, message='Sector name exist')
        try:
            Sector.objects.get(id=id).update(**body)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException
        return Message.update()

    def delete(self, id=None):
        if not id or len(id) != 24 or not Sector.objects(id=id).count():
            abort(400, message='Sector not found')

        Sector.objects.get(id=id).delete()
        return Message.delete()
