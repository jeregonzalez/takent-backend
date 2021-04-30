from datetime import datetime

from database.db import db
from database.models.common import Image, Address
from database.models.parametric_docs import StateService, StateServiceRequest
from database.models.user import CommonUser
from resources.helpers import user_helper


class StateServiceRequestHistory(db.EmbeddedDocument):
    date = db.DateTimeField(default=lambda: datetime.today())
    state = db.StringField()
    user = db.StringField()


class ServiceRequest(db.Document):
    request_date = db.DateTimeField(default=lambda: datetime.today())
    score = db.IntField()
    user = db.ReferenceField(CommonUser)
    state = db.ReferenceField(StateServiceRequest, default=lambda: StateServiceRequest.objects.get(name='pending'))
    states_history = db.EmbeddedDocumentListField(StateServiceRequestHistory)

    def save(self, *args, **kwargs):
        self.states_history.create(state=self.state.name, user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(ServiceRequest, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        state = kwargs.get('state')
        if state:
            kwargs['push__states_history'] = StateServiceRequestHistory(
                state=state.name, user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(ServiceRequest, self).update(*args, **kwargs)


class StateServiceHistory(db.EmbeddedDocument):
    date = db.DateTimeField(default=lambda: datetime.today())
    state = db.StringField()
    user = db.StringField()


class Service(db.Document):
    title = db.StringField()
    sector = db.StringField()
    cost = db.FloatField()
    preference = db.BooleanField(default=False)
    images = db.ListField(db.ReferenceField(Image))
    description = db.StringField()
    address = db.EmbeddedDocumentField(Address)
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(CommonUser)
    service_requests = db.ListField(db.ReferenceField(ServiceRequest))
    state = db.ReferenceField(StateService, default=lambda: StateService.objects.get(name='active'))
    states_history = db.EmbeddedDocumentListField(StateServiceRequestHistory)

    def save(self, *args, **kwargs):
        self.states_history.create(state=self.state.name, user=user_helper.get_user_from_jwt(keys='user_account'))
        return super(Service, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        state = kwargs.get('state')
        if state:
            user = user_helper.get_user_from_jwt(keys='user_account') or 'bot'
            kwargs['push__states_history'] = StateServiceRequestHistory(state=state.name, user=user)
        return super(Service, self).update(*args, **kwargs)
