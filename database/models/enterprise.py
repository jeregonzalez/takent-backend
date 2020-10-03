from mongoengine import NULLIFY

from database.db import db
from database.models.common import Address, State, Image
from database.models.user import EnterpriseUser


class Enterprise(db.Document):
    fantasy_name = db.StringField(required=True)
    business_name = db.StringField(required=True)
    address = db.EmbeddedDocumentField(Address)
    phone = db.IntField()
    email = db.EmailField()
    profile_photo = db.ReferenceField(Image, reverse_delete_rule=NULLIFY)
    photos = db.ListField(db.ReferenceField(Image))
    description = db.StringField()
    admin_user = db.ReferenceField(EnterpriseUser, required=True)
    member_users = db.ListField(db.ReferenceField(EnterpriseUser))
    enterprise_type = db.StringField()
    sector = db.StringField()
    offers_remaining = db.IntField(default=10)
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))
    web_page = db.StringField()

    def deactivate(self):
        self.update(state=State.objects.get(name='inactive'))
        for member_user in self.member_users:
            member_user.deactivate()
