from datetime import datetime

from database.db import db
from database.models.user import User

NOTIFICATION_TYPES = [
    'requested_service',
    'request_assessment',
    'suggest_preferred_service',
    'few_available_publications',
    'state_postulation_changed',
    'suggest_info_completion',
    'offers_nearing_to_finish',
    'suggest_register_new_member',
    'suggest_publish_new_offer',
    'suggest_offer',
    'near_offers',
    'near_services'
]


class Notification(db.Document):
    date = db.DateTimeField(default=lambda: datetime.today())
    user = db.ReferenceField(User)
    type = db.StringField(choices=NOTIFICATION_TYPES)
    title = db.StringField()
    description = db.StringField()
    viewed = db.BooleanField(default=False)
    entity = db.StringField()
    info = db.DictField()


class NotificationsConfiguration(db.Document):
    user = db.ReferenceField(User, primary_key=True)

    meta = {
        'abstract': True
    }


class NearNotification(db.EmbeddedDocument):
    active = db.BooleanField(default=False)
    radius = db.IntField(default=300)


class NotificationsConfigurationCommonUser(NotificationsConfiguration):
    requested_service = db.BooleanField(default=True)
    request_assessment = db.BooleanField(default=True)
    suggest_preferred_service = db.BooleanField(default=True)
    state_postulation_changed = db.BooleanField(default=True)
    suggest_info_completion = db.BooleanField(default=True)
    near_offers = db.EmbeddedDocumentField(NearNotification, default=NearNotification())
    near_services = db.EmbeddedDocumentField(NearNotification, default=NearNotification())


class NotificationsConfigurationEnterpriseUser(NotificationsConfiguration):
    few_available_publications = db.BooleanField(default=True)
    offers_nearing_to_finish = db.BooleanField(default=True)
    suggest_register_new_member = db.BooleanField(default=True)
    suggest_publish_new_offer = db.BooleanField(default=True)
