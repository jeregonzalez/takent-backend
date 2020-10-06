from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, ValidationError

from database.models.parametric_docs import EnterpriseType
from resources.utils.exceptions import SchemaValidationErrorException, MissingRequiredFieldsException
from resources.utils.messages import Message


class EnterpriseTypeApi(Resource):
    def get(self):
        if not request.args.get('name'):
            return Message.ok([type for type in EnterpriseType.objects()])
        return Message.ok([type for type in EnterpriseType.objects(name__icontains=request.args.get('name'))])

    def post(self):
        body = request.get_json()

        try:
            enterprise_type = EnterpriseType(**body).save()
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.created(enterprise_type.name)

    def put(self, id=None):
        if not id or len(id) != 24 or not EnterpriseType.objects(id=id).count():
            abort(400, mesagge='Enterprise type not found')
        body = request.get_json()

        if body.get('name') and EnterpriseType.objects(name=body.get('name')).count():
            abort(400, message='Enterprise type name exist')
        enterprise_type = EnterpriseType.objects.get(id=id)
        try:
            enterprise_type.update(**body, id=enterprise_type.id)
        except FieldDoesNotExist:
            raise SchemaValidationErrorException
        except ValidationError:
            raise MissingRequiredFieldsException

        return Message.update()

    def delete(self, id=None):
        if not id or len(id) != 24 or not EnterpriseType.objects(id=id).count():
            abort(400, mesagge='Enterprise type not found')
        EnterpriseType.objects.get(id=id).delete()

        return Message.delete()