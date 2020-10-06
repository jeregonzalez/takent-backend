from datetime import datetime

from database.db import db
from .common import Address, Image
from .enterprise import Enterprise
from .parametric_docs import State
from .user import CommonUser, EnterpriseUser


class Postulant(db.Document):
    postulation_date = db.DateTimeField()
    postulant = db.ReferenceField(CommonUser)
    state = db.ReferenceField(State)


class OfferLanguage(db.EmbeddedDocument):
    language = db.StringField()
    certificate = db.BooleanField()


class Offer(db.Document):
    title = db.StringField(required=True, max_length=100)
    position = db.StringField(required=True)
    description = db.StringField(max_length=500)
    images = db.ListField(db.ReferenceField(Image))
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(EnterpriseUser)
    sector = db.StringField(required=True)
    experience = db.StringField(required=True)
    contract_type = db.StringField(required=True)
    language = db.EmbeddedDocumentField(OfferLanguage)
    address = db.EmbeddedDocumentField(Address)
    postulants = db.ListField(db.ReferenceField(Postulant))
    state = db.ReferenceField(State)
    enterprise = db.ReferenceField(Enterprise)
