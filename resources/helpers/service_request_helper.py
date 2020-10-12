from database.models.service import ServiceRequest


def service_request_exists(_id):
    return bool(ServiceRequest.objects(id=_id).count())
