from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, DoesNotExist

from database.models.common import State
from database.models.enterprise import Enterprise
from database.models.users import EnterpriseUser
from resources.errors import SchemaValidationError


class EnterpriseApi(Resource):
    def get(self, admin=None):
        """
        Obtiene una empresa que corresponda con un nombre
        :param enterprise_name: nombre de la empresa a buscar
        """
        if not admin:
            abort(404)

        # Validar que la lista no esté vacía
        if Enterprise.objects.count() == 0:
            return [], 200
        try:
            # Obtengo la empresa que corresponde con el nombre pasado por parámetro
            empresa_ret = Enterprise.objects.get(admin_user=admin)
        except DoesNotExist:
            abort(400, message='User enterprise {} not exists'.format(admin))

        # Se valida que la empresa este activa
        if not empresa_ret.state == State.objects.get(name='active_enterprise'):
            abort(400, message='Enteprise\'s state is inactive')

        # Creo una lista con un diccionario fijando los parámetros que se quieren mostrar
        empresa = [
            {'name': empresa_ret.business_name, 'description': empresa_ret.description,
             'address': empresa_ret.address.to_mongo(),
             'email': empresa_ret.email}]

        # Se retorna la lista de las empresas con el código 200
        return empresa, 200

    def post(self):
        """
        Registra una empresa con todos sus datos
        """
        body = request.get_json()
        try:
            # Se valida que el admin_user ya esté registrado
            validate_enterprise_user_exist(body['admin_user'])
            # Se valida que el estado exista
            validate_state_exist(body['state'])
            # Se valida si la empresa ya se encuentra registrada
            validate_enterprise_exist(body['admin_user'])

            enterprise = Enterprise(**body)
            Enterprise.objects.insert(enterprise)

        except FieldDoesNotExist:
            raise SchemaValidationError

        return {'message': 'Enterprise {} created successfully'.format(enterprise.business_name)}, 201

    def delete(self, admin=None):
        """
        Elimina de forma lógica una empresa
        """
        if not admin:
            abort(404)

        try:
            state_enterprise = State.objects.get(name='inactive_enterprise')
            Enterprise.objects.get(admin_user=admin).update(state=state_enterprise)
        except DoesNotExist:
            abort(400, message='User enterprise {} not exists'.format(admin))

        enterprise = Enterprise.objects.get(admin_user=admin)

        return {'message': 'The enterprise {} has been deleted logically'.format(enterprise.business_name)}, 200

    def put(self, admin=None):
        """
        Actualiza los datos de una empresa
        """
        if not admin:
            abort(404)

        body = request.get_json()

        try:
            if 'admin_user' in body:
                validate_enterprise_user_exist(body['admin_user'])

            validate_enterprise_user_exist(admin)

            if 'state' in body:
                validate_state_exist(body['state'])
                body['state'] = State.objects.get(name=body['state'])

            enterprise = Enterprise.objects.get(admin_user=admin)
            enterprise.update(**body)

        except DoesNotExist:
            abort(400, message='User enterprise {} not exists'.format(admin))

        return {'message': 'Enterprise {} updated successfully'.format(enterprise.business_name)}, 201


def validate_state_exist(name_state):
    if not State.objects(name=name_state).count():
        abort(400, message='State {} not exists'.format(name_state))


def validate_enterprise_user_exist(name_user):
    if not EnterpriseUser.objects(account=name_user):
        abort(400, message='User {} not exists'.format(name_user))


def validate_enterprise_exist(admin):
    if Enterprise.objects(admin_user=admin):
        abort(400, message='Enterprise with admin {} exists'.format(admin))
