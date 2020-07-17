import time

from flask import request
from flask_restful import Resource, abort
from mongoengine import FieldDoesNotExist, DoesNotExist, NotUniqueError

from database.models.roles import Role
from resources.helpers.log_helper import LOGGER

from database.models.common import State
from database.models.enterprise import Enterprise
from database.models.users import EnterpriseUser
from resources.helpers.user_helper import get_user
from resources.helpers.auth_helper import hash_password
from resources.utils.exceptions import MissingRequiredFieldsException, SchemaValidationErrorException, \
    UserAlreadyExistsException
from resources.utils.decorators import validate_headers, authentication_required, \
    enterprise_must_exist, enterprise_must_not_exist, user_member_must_exist, \
    enterprise_state_must_active, user_must_be_enterprise, user_members_must_not_exist
from resources.helpers.user_helper import validate_enterprise_user_exist


class EnterpriseApi(Resource):
    method_decorators = {
        'get': [enterprise_state_must_active, enterprise_must_exist, authentication_required],
        'post': [user_members_must_not_exist, enterprise_must_not_exist, user_must_be_enterprise, authentication_required,
                 validate_headers],
        'put': [user_members_must_not_exist, user_must_be_enterprise, enterprise_must_exist,
                authentication_required, validate_headers],
        'delete': [enterprise_must_exist, authentication_required, validate_headers]
    }

    def get(self):
        """
        Obtiene una empresa que corresponda con un nombre
        :param admin: nombre de la empresa a buscar
        """

        empresa_ret = Enterprise.objects.get(admin_user=get_user().account)

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
            body['admin_user'] = get_user()

            if 'member_users' in body and body['member_users']:
                member_users = []
                for member_user in body['member_users']:
                    member_user['role'] = Role.objects.get(name='member')
                    member_user['password'] = hash_password(member_user.get('password'))

                    try:
                        enterprise_user = EnterpriseUser(**member_user).save()
                    except NotUniqueError:
                        raise UserAlreadyExistsException(enterprise_user.account)

                    member_users.append(enterprise_user)

                body['member_users'] = member_users

            enterprise = Enterprise(**body)
            enterprise.save()

        except FieldDoesNotExist:
            raise MissingRequiredFieldsException

        return {'message': 'Enterprise {} created successfully'.format(enterprise.business_name)}, 201

    def delete(self):
        """
        Elimina de forma lógica una empresa
        """
        ent = Enterprise.objects.get(admin_user=get_user().account)
        ent.update(state=State.objects.get(name='inactive'))

        return {'message': 'The enterprise {} has been deleted logically'.format(ent.business_name)}, 200

    def put(self):
        """
        Actualiza los datos de una empresa
        """
        body = request.get_json()
        enterprise = Enterprise.objects.get(admin_user=get_user())
        try:
            if 'state' in body:
                body['state'] = State.objects.get(name=body['state'])

            if 'member_users' in body and body['member_users']:
                raise SchemaValidationErrorException

            enterprise.update(**body)

        except DoesNotExist:
            abort(400, message='User enterprise {} not exists'.format(body['admin_user']))

        return {'message': 'Enterprise {} updated successfully'.format(enterprise.business_name)}, 201
