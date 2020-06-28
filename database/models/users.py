from database.db import db
from .common import Address, Education, Experience, Skill, UserLanguage
from .roles import Role


class User(db.Document):
    account = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True, min_length=6)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)
    meta = {
        'abstract': True,
    }


class CommonUser(User):
    address = db.EmbeddedDocumentField(Address)
    curriculum = db.FileField()
    birth_date = db.DateTimeField()
    profile_photo = db.FileField()
    description = db.StringField()
    education = db.EmbeddedDocumentListField(Education)
    experience = db.EmbeddedDocumentListField(Experience)
    skill = db.EmbeddedDocumentListField(Skill)
    language = db.EmbeddedDocumentListField(UserLanguage)


class EnterpriseUser(User):
    role = db.ReferenceField(Role)
