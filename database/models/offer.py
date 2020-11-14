from datetime import datetime

from database.db import db
from resources.helpers import user_helper
from .common import Address, Image
from .enterprise import Enterprise
from .parametric_docs import StateOffer, StatePostulant
from .user import CommonUser, EnterpriseUser


class StatePostulantHistory(db.EmbeddedDocument):
    date = db.DateTimeField(default=lambda: datetime.today())
    state = db.StringField()
    user = db.StringField()


class Postulant(db.Document):
    postulation_date = db.DateTimeField(default=lambda: datetime.today())
    postulant = db.ReferenceField(CommonUser)
    state = db.ReferenceField(StatePostulant, default=lambda: StatePostulant.objects.get(name='pending'))
    states_history = db.EmbeddedDocumentListField(StatePostulantHistory)

    def save(self, *args, **kwargs):
        self.states_history.create(state=self.state.name, user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(Postulant, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        state = kwargs.get('state')
        if state:
            kwargs['push__states_history'] = StatePostulantHistory(state=state.name,
                                                                   user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(Postulant, self).update(*args, **kwargs)


class OfferLanguage(db.EmbeddedDocument):
    language = db.StringField()
    certificate = db.BooleanField()


class StateOfferHistory(db.EmbeddedDocument):
    date = db.DateTimeField(default=lambda: datetime.today())
    state = db.StringField()
    user = db.StringField()


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
    state = db.ReferenceField(StateOffer, default=lambda: StateOffer.objects.get(name='active'))
    enterprise = db.ReferenceField(Enterprise)
    states_history = db.EmbeddedDocumentListField(StateOfferHistory)

    def save(self, *args, **kwargs):
        self.states_history.create(state=self.state.name, user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(Offer, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        state = kwargs.get('state')
        if state:
            kwargs['push__states_history'] = StateOfferHistory(state=state.name,
                                                               user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(Offer, self).update(*args, **kwargs)
