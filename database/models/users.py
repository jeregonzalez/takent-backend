from database.db import db
from resources.utils.exceptions import ImmutableFieldsException
from .common import Address, Education, Experience, Skill, UserLanguage, Image
from .roles import Role


class User(db.Document):
    account = db.EmailField(primary_key=True)
    password = db.StringField(required=True, min_length=6)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)

    meta = {
        'abstract': True,
    }

    def update(self, *args, **kwargs):
        if any(field in ['account', 'password'] for field in kwargs.keys()):
            raise ImmutableFieldsException
        return super(User, self).update(*args, **kwargs)


class CommonUser(User):
    birth_date = db.DateTimeField(required=True)
    address = db.EmbeddedDocumentField(Address)
    curriculum = db.FileField()
    profile_photo = db.ReferenceField(Image)
    description = db.StringField()
    education = db.EmbeddedDocumentListField(Education)
    experience = db.EmbeddedDocumentListField(Experience)
    skill = db.EmbeddedDocumentListField(Skill)
    language = db.EmbeddedDocumentListField(UserLanguage)


class EnterpriseUser(User):
    role = db.ReferenceField(Role, required=True)
