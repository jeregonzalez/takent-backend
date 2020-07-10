from database.db import db
from resources.helpers.auth_helper import hash_password
from .common import Address, Education, Experience, Skill, UserLanguage
from .roles import Role


class User(db.Document):
    account = db.EmailField(primary_key=True)
    password = db.StringField(required=True, min_length=6)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)

    meta = {
        'abstract': True,
    }

    def save(self, *args, **kwargs):
        self.password = hash_password(self.password)
        return super(User, self).save(*args, **kwargs)


class CommonUser(User):
    address = db.EmbeddedDocumentField(Address)
    curriculum = db.FileField()
    profile_photo = db.ImageField()
    birth_date = db.DateTimeField()
    description = db.StringField()
    education = db.EmbeddedDocumentListField(Education)
    experience = db.EmbeddedDocumentListField(Experience)
    skill = db.EmbeddedDocumentListField(Skill)
    language = db.EmbeddedDocumentListField(UserLanguage)


class EnterpriseUser(User):
    role = db.ReferenceField(Role, required=True)
