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
        {'name': 'active', 'description': 'Active entity'},
        {'name': 'inactive', 'description': 'Inactive entity'}
    ]
}
