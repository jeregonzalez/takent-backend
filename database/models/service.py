from datetime import datetime

from database.db import db
from database.models.common import Image, Address
from database.models.parametric_docs import StateService
from database.models.user import CommonUser


class ServiceRequest(db.Document):
    request_date = db.DateTimeField(default=lambda: datetime.today())
    score = db.IntField()
    user = db.ReferenceField(CommonUser)


class Service(db.Document):
    title = db.StringField()
    sector = db.StringField()
    cost = db.FloatField()
    preference = db.BooleanField()
    images = db.ListField(db.ReferenceField(Image))
    description = db.StringField()
    address = db.EmbeddedDocumentField(Address)
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(CommonUser)
    service_requests = db.ListField(db.ReferenceField(ServiceRequest))
    state = db.ReferenceField(StateService, default=lambda: StateService.objects.get(name='active'))
