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
        {'name': 'Terciario'},
        {'name': 'Grado'},
        {'name': 'Posgrado'}
    ],
    'language_level': [
        {'name': 'Básico'},
        {'name': 'Intermedio'},
        {'name': 'Avanzado'},
        {'name': 'Nativo'}
    ],
    'state': [
        {'name': 'active', 'description': 'Active entity'},
        {'name': 'inactive', 'description': 'Inactive entity'},
        {'name': 'in_selection', 'description': 'Offer in selection process'},
        {'name': 'finished', 'description': 'Offer finished'},
        {'name': 'deleted', 'description': 'Offer or user deleted logically'}
    ],
    'job_type': [
        {'name': 'Jornada Completa'},
        {'name': 'Jornada Parcial'},
        {'name': 'Por Temporada'},
        {'name': 'Por Obra'},
        {'name': 'Pasantía'},
        {'name': 'Por Hora'}
    ],
    'enterprise_type': [
        {'name': 'Reclutamiento y selección'},
        {'name': 'Empleador directo'}
    ],
    'experience_offer': [
        {'name': 'Experiencia Escasa'},
        {'name': 'Algo de Experiencia'},
        {'name': 'Experiencia Intermedia'},
        {'name': 'Mucha Experiencia'}

    ]
}