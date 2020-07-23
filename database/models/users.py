from mongoengine import NULLIFY

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

    def update_password(self, new_password):
        super(User, self).update(password=new_password)


class CommonUser(User):
    birth_date = db.DateTimeField(required=True)
    address = db.EmbeddedDocumentField(Address)
    curriculum = db.FileField()
    profile_photo = db.ReferenceField(Image, reverse_delete_rule=NULLIFY)
    description = db.StringField()
    education = db.EmbeddedDocumentListField(Education)
    experience = db.EmbeddedDocumentListField(Experience)
    skill = db.EmbeddedDocumentListField(Skill)
    language = db.EmbeddedDocumentListField(UserLanguage)
    phone = db.IntField()
    floor = db.IntField()
    apartment = db.StringField()


class EnterpriseUser(User):
    role = db.ReferenceField(Role, required=True)
