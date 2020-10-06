from datetime import datetime

from database.db import db
from .common import State, Address, Image
from .enterprise import Enterprise
from .user import CommonUser, EnterpriseUser


class Applicant(db.Document):
    applicant = db.ReferenceField(CommonUser)
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='in_selection'))


class Offer(db.Document):
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(EnterpriseUser)
    title = db.StringField(required=True, max_length=100)
    position = db.StringField(required=True)
    sector = db.StringField(required=True)
    experience = db.StringField(required=True)
    job_type = db.StringField(required=True)
    description = db.StringField(max_length=500)
    language = db.DictField()
    address = db.EmbeddedDocumentField(Address)
    enterprise = db.ReferenceField(Enterprise)
    images = db.ListField(db.ReferenceField(Image))
    applicants = db.ListField(db.ReferenceField(Applicant))
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))
