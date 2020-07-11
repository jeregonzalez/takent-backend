from database.db import db
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

    def save(self, *args, **kwargs):
        if self.address and self.address.city:
            self.address.province = self.address.city.province_id
        return super(CommonUser, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        if 'address' in kwargs.keys() and kwargs.get('address').city:
            kwargs['province'] = kwargs.get('address').city
        return super(CommonUser, self).update(*args, **kwargs)


class EnterpriseUser(User):
    role = db.ReferenceField(Role, required=True)
