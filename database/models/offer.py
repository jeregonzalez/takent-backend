from datetime import datetime

from database.db import db
from .common import State, JobType, UserLanguage
from .user import CommonUser, EnterpriseUser


class PostulantOffer(db.Document):
    postulant = db.ReferenceField(CommonUser)
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='En seleccion'))


class Offer(db.Document):
    title = db.StringField(required=True, max_length=100)
    description = db.StringField(max_length=500)
    publication_date = db.DateTimeField(default=lambda: datetime.today())
    publication_user = db.ReferenceField(EnterpriseUser)
    photo = db.ListField(db.ImageField())
    experience_offer = db.StringField(default='Ninguna Experiencia')
    postulant = db.ListField(db.ReferenceField('PostulantOffer'))
    job_type = db.ReferenceField(JobType, default=lambda: JobType.objects.get(name='Jornada completa'))
    sector = db.StringField()
    language = db.EmbeddedDocumentListField(UserLanguage, default=[
        UserLanguage(name='ESPAÑOL', writing_level='Nativo', reading_level='Nativo')])
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))
