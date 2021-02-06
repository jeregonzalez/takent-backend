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
    'suggest_offer'
]


class Notification(db.Document):
    date = db.DateTimeField(default=lambda: datetime.today())
    user = db.ReferenceField(User)
    type = db.StringField(choices=NOTIFICATION_TYPES)
    title = db.StringField()
    description = db.StringField()
    viewed = db.BooleanField(default=False)
