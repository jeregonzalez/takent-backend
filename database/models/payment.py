from datetime import datetime

from database.db import db
from database.models.user import User


class Payment(db.Document):
    external_reference = db.StringField(primary_key=True)
    user = db.ReferenceField(User)
    offer_pack = db.StringField()
    quantity = db.IntField()
    price = db.IntField()
    generation_date = db.DateTimeField(default=lambda: datetime.today())
    payment_date = db.DateTimeField()
    preference_id = db.StringField()
    payment_id = db.IntField()
    payment_status = db.StringField()
    payment_status_detail = db.StringField()
