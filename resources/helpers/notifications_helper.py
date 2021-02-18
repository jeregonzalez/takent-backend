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
        if not isinstance(self.user, list):
            self.user = [self.user]
        for user in self.user:
            notification.Notification(user=user,
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


class RequestAssessmentNotification(Notification):

    type = 'request_assessment'
    title = 'Valoración de servicio obtenido'
    description = 'Calificá el servicio "{}" que recibiste recientemente'

    def __init__(self, user, service_name):
        super().__init__(user)
        self.description = self.description.format(service_name)


class SuggestPreferredServiceNotification(Notification):

    type = 'suggest_preferred_service'
    title = 'Sugerencia: hacé tu servicio preferencial'
    description = 'Acabás de publicar el servicio llamado "{}", hacelo preferencial para obtener más visibilidad!'

    def __init__(self, user, service_name):
        super().__init__(user)
        self.description = self.description.format(service_name)


class FewAvailablePublicationsNotification(Notification):

    type = 'few_available_publications'
    title = 'Publicaciones disponibles'
    description = 'Tenés pocas publicaciones disponibles! Comprá más aprovechando nuestras promociones!'

    def __init__(self, user):
        super().__init__(user)


class StatePostulationChangedNotification(Notification):

    type = 'state_postulation_changed'
    title = 'Cambio de estado de postulación'
    description = 'Tu postulación a la oferta "{}" cambió al estado "{}"'

    STATE_MAP = {
        'pending': 'Pendiente',
        'pre_selected': 'Preseleccionado',
        'contacted': 'Contactado',
        'discarded': 'Descartado'
    }

    DESCRIPTION_DISCARDED = 'No has sido seleccionado para la oferta "{}". ' \
                            'No te desanimes, todavía quedan muchas oportunidades para vos!'

    def __init__(self, user, offer_name, state_name):
        super().__init__(user)
        self.description = self.description.format(offer_name, self.STATE_MAP[state_name]) \
            if state_name != 'discarded' else self.DESCRIPTION_DISCARDED.format(offer_name)


class SuggestInfoCompletionNotification(Notification):

    type = 'suggest_info_completion'
    title = 'Datos personales'
    description = 'Te sugerimos completar tus datos ({}) para tener una mayor visibilidad!'

    INFO_MAP = {
        'education': 'académicos',
        'experience': 'laborales',
        'skill': 'aptitudes',
        'curriculum': 'CV',
        'language': 'idiomas'
    }

    def __init__(self, user, missing_info):
        super().__init__(user)
        self.description = self.description.format(', '.join([self.INFO_MAP.get(item) for item in missing_info]))


class OffersNearingToFinishNotification(Notification):

    type = 'offers_nearing_to_finish'
    title = 'Oferta a finalizar'
    description = 'Tu publicación "{}" está próxima a finalizar!'

    def __init__(self, user, offer_name):
        super().__init__(user)
        self.description = self.description.format(offer_name)


class SuggestRegisterNewMemberNotification(Notification):

    type = 'suggest_register_new_member'
    title = 'Sugerencia: registrá colaboradores'
    description = 'Tenés la posibilidad de registrar colaboradores para que te ayuden en tu trabajo diario. ' \
                  'No esperés más!'

    def __init__(self, user):
        super().__init__(user)


class SuggestPublishNewOfferNotification(Notification):

    type = 'suggest_publish_new_offer'
    title = 'Sugerencia: publicá una oferta'
    description = 'Hace mucho no publicás una oferta, aprovechá el momento y publicá una nueva!'

    def __init__(self, user):
        super().__init__(user)


class SuggestOfferNotification(Notification):

    type = 'suggest_offer'
    title = 'Búsqueda recomendada'
    description = 'foo'
