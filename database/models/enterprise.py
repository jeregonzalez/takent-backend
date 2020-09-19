from database.db import db
from database.models.common import Address, State
from database.models.user import EnterpriseUser


class Enterprise(db.Document):
    fantasy_name = db.StringField(required=True)
    business_name = db.StringField(required=True)
    address = db.EmbeddedDocumentField(Address)
    phone = db.IntField()
    email = db.EmailField()
    location = db.DictField()
    profile_photo = db.ImageField()
    photos = db.ListField(db.ImageField())
    description = db.StringField()
    admin_user = db.ReferenceField(EnterpriseUser, required=True)
    member_users = db.ListField(db.ReferenceField(EnterpriseUser))
    enterprise_type = db.StringField()
    sector = db.StringField()
    state = db.ReferenceField(State, default=lambda: State.objects.get(name='active'))

    def deactivate(self):
        self.update(state=State.objects.get(name='inactive'))
        for member_user in self.member_users:
            member_user.deactivate()
