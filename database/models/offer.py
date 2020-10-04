from datetime import datetime

from mongoengine import NULLIFY

from database.db import db
from .common import State, Address, Image
from .enterprise import Enterprise
from .user import CommonUser, EnterpriseUser


class PostulantOffer(db.Document):
    postulant = db.ReferenceField(CommonUser)
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='in_selection'))


class Offer(db.Document):
    title = db.StringField(required=True, max_length=100)
    position = db.StringField(required=True)
    description = db.StringField(max_length=500)
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(EnterpriseUser)
    images = db.ListField(db.ReferenceField(Image))
    experience = db.StringField(required=True)
    postulants = db.ListField(db.ReferenceField(PostulantOffer))
    job_type = db.StringField(required=True)
    sector = db.StringField(required=True)
    language = db.ListField(db.StringField())
    address = db.EmbeddedDocumentField(Address)
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))
    duration = db.IntField(default=30)
    enterprise = db.ReferenceField(Enterprise)
