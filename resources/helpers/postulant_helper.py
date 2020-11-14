from database.models.offer import Postulant


def postulant_exists(_id):
    return bool(Postulant.objects(id=_id).count())
