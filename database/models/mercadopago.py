from datetime import datetime

from database.db import db
from database.models.user import User


class PaymentStatusHistory(db.EmbeddedDocument):
    date = db.DateTimeField(default=lambda: datetime.today())
    status = db.StringField()


class Payment(db.Document):
    payment_id = db.IntField(primary_key=True)
    generation_date = db.DateTimeField(default=lambda: datetime.today())
    user = db.ReferenceField(User)
    concept_id = db.StringField()
    reason = db.StringField()
    price = db.IntField()
    payment_date = db.DateTimeField(default=lambda: datetime.today())
    payment_status = db.StringField()
    status_history = db.EmbeddedDocumentListField(PaymentStatusHistory)
