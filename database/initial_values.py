# Datos con los que inicializar la base de datos, cada entrada del diccionario es una coleccion

data = {
    'permission': [
        {'name': 'admin', 'description': 'Permissions to do anything'},
        {'name': 'member', 'description': 'Permissions to only query data'}
    ],
    'role': [
        {'name': 'admin', 'description': 'Permissions to do anything', 'permissions': ['admin']},
        {'name': 'member', 'description': 'Permissions to only query data', 'permissions': ['member']}
    ],
    'education_level': [
        {'name': 'Primario'},
        {'name': 'Secundario'},
        {'name': 'Grado'},
        {'name': 'Posgrado'},
        {'name': 'Master'},
        {'name': 'Terciario'}
    ],
    'language_level': [
        {'name': 'Básico'},
        {'name': 'Intermedio'},
        {'name': 'Básico profesional'},
        {'name': 'Completo profesional'},
        {'name': 'Nativo o bilingüe'}
    ],
    'state': [
        {'name': 'active', 'description': 'Active entity', 'scope': 'enterprise'},
    ],
    'scope': [
        {'name': 'enterprise', 'description': 'Account of enterprise with active state'}
    ],
    'enterprise_users': [
        {'account': 'usertakent@gmail.com', 'password': '123', 'name': 'takent', 'surname': 'app', 'role': 'admin'},
        {'account': 'rodri@gmail.com', 'password': '456', 'name': 'rodri', 'surname': 'EL CAPO', 'role': 'member'},
        {'account': 'jere@gmail.com', 'password': '678', 'name': 'jere', 'surname': 'EL DEVELOPER', 'role': 'member'}
    ]
}
