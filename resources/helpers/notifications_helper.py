from abc import ABC

from database.models import notification


class Notification(ABC):

    user = None
    type = None
    title = None
    description = None

    def __init__(self, user):
        self.user = user

    def save(self):
        notification.Notification(user=self.user,
                                  type=self.type,
                                  title=self.title,
                                  description=self.description).save()


class RequestedServiceNotification(Notification):

    type = 'requested_service'
    title = 'Nueva solicitud de servicio'
    description = 'Recibiste una nueva solicitud para el servicio "{}"'

    def __init__(self, user, service_name):
        super().__init__(user)
        self.description = self.description.format(service_name)


class SuggestPreferredService(Notification):

    type = 'suggest_preferred_service'
    title = 'Sugerencia: hacé tu servicio preferencial'
    description = 'Acabás de publicar el servicio llamado "{}", hacelo preferencial para obtener más visibilidad!'

    def __init__(self, user, service_name):
        super().__init__(user)
        self.description = self.description.format(service_name)
