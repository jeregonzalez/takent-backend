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
        {'name': 'inactive', 'description': 'Inactive entity'},
        {'name': 'in_selection', 'description': 'Offer in selection process'},
        {'name': 'finished', 'description': 'Offer finished'},
        {'name': 'deleted', 'description': 'Offer or user deleted logically'}
    ],
    'job_type': [
        {'name': 'Jornada completa'},
        {'name': 'Jornada parcial'},
        {'name': 'Por temporada'},
        {'name': 'Por obra'}
    ]
}