from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, NotUniqueError, ValidationError

from database.models.users import CommonUser, EnterpriseUser
from resources.errors import SchemaValidationError, AccountAlreadyExistsError

USER_TYPES = {
    'common': CommonUser,
    'enterprise': EnterpriseUser
}


class SignUpApi(Resource):
    def post(self, user_type):
        """
        Método para crear un nuevo usuario, tanto empresa como común
        :param user_type: Tipo de usuario, común o empresa
        :return:
        """
        validate_user_type(user_type)
        body = request.get_json()
        try:
            new_user = USER_TYPES[user_type](**body).save()
        except (FieldDoesNotExist, ValidationError):
            raise SchemaValidationError
        except NotUniqueError:
            raise AccountAlreadyExistsError
        return {'message': 'User {} created successfully'.format(new_user.id)}, 201


class UserApi(Resource):

    def get(self, user_type, user_account=None):
        """
        Método para obtener usuarios, tanto comunes como empresa,
        existiendo la posibilidad de filtrar por nombre de cuenta
        :param user_type: tipo de usuario, comun o empresa
        :param user_account: parametro opcional que permite obtener un solo usuario
        :return:
        """
        validate_user_type(user_type)
        if user_account:
            validate_user_exists(user_type, user_account)
            return USER_TYPES[user_type].objects.exclude('password').get(account=user_account).to_mongo()
        return [user.to_mongo() for user in USER_TYPES[user_type].objects.exclude('password').all()], 200

    # TODO Falta terminar de desarrollar toda la logica
    def put(self, user_type, user_account=None):
        """
        Método para modificar uno o mas campos de un usuario determinado
        :param user_type: tipo de usuario
        :param user_account: nombre de cuenta
        :return:
        """
        validate_user_type(user_type)
        validate_user_exists(user_type, user_account)
        body = request.get_json()
        USER_TYPES[user_type].objects.get(account=user_account).update(**body)
        return '', 200

    # TODO Falta terminar de desarrollar la logica, y hacer borrado logico en vez de fisico
    def delete(self, user_type, user_account=None):
        """
        Metodo para eliminar un usuario determinado
        :param user_type:
        :param user_account:
        :return:
        """
        validate_user_type(user_type)
        validate_user_exists(user_type, user_account)
        USER_TYPES[user_type].objects.get(account=user_account).delete()
        return '', 200


def validate_user_type(user_type):
    """
    Valida si el tipo de usuario existe
    :param user_type: tipo de usuario
    :return:
    """
    if user_type not in USER_TYPES.keys():
        abort(404)


def validate_user_exists(user_type, user_account):
    """
    Valida si un usuario existe en la base de datos
    :param user_type: tipo de usuario
    :param user_account: nombre de cuenta
    :return:
    """
    if not user_account:
        abort(400, message='You must enter an user')
    exist = USER_TYPES[user_type].objects(account=user_account).count()
    if not exist:
        abort(400, message='User {} does not exist'.format(user_account))
