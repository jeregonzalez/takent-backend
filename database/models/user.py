from mongoengine import NULLIFY

from database.db import db
from database.models.common import Image, Address
from database.models.common_user import UserCurriculumVitae, UserEducation, UserExperience, UserSkill, UserLanguage
from database.models.parametric_docs import Permission, StateUser
from resources.utils.exceptions import ImmutableFieldsException


class User(db.Document):
    account = db.EmailField(primary_key=True)
    password = db.StringField(required=True)
    name = db.StringField(required=True)
    surname = db.StringField(required=True)
    birth_date = db.DateTimeField()
    phone = db.IntField()
    state = db.ReferenceField(StateUser, default=lambda: StateUser.objects.get(name='inactive'))

    meta = {
        'abstract': True,
    }

    def update(self, *args, **kwargs):
        if any(field in ['account', 'password'] for field in kwargs.keys()):
            raise ImmutableFieldsException
        return super(User, self).update(*args, **kwargs)

    def update_password(self, new_password):
        super(User, self).update(password=new_password)

    def activate(self):
        active_state = StateUser.objects.get(name='active')
        return super(User, self).update(state=active_state)

    def deactivate(self):
        inactive_state = StateUser.objects.get(name='inactive')
        return super(User, self).update(state=inactive_state)


class CommonUser(User):
    description = db.StringField()
    curriculum = db.ReferenceField(UserCurriculumVitae, reverse_delete_rule=NULLIFY)
    profile_photo = db.ReferenceField(Image, reverse_delete_rule=NULLIFY)
    address = db.EmbeddedDocumentField(Address)
    education = db.EmbeddedDocumentListField(UserEducation)
    experience = db.EmbeddedDocumentListField(UserExperience)
    skill = db.EmbeddedDocumentListField(UserSkill)
    language = db.EmbeddedDocumentListField(UserLanguage)


class EnterpriseUser(User):
    position = db.StringField()
    permission = db.ReferenceField(Permission, default=lambda: Permission.objects.get(name='admin'))


class ActivationTicket(db.Document):
    account = db.EmailField(required=True)
    user_type = db.StringField(required=True)


class RecoveryTicket(db.Document):
    account = db.EmailField(required=True)
    user_type = db.StringField(required=True)
