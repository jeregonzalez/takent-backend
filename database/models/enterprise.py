from database.db import db
from database.models.common import Address, State
from database.models.users import EnterpriseUser


class Enterprise(db.Document):
    fantasy_name = db.StringField(unique=True, required=True)
    business_name = db.StringField()
    address = db.EmbeddedDocumentField(Address)
    phone = db.IntField()
    email = db.EmailField()
    location = db.StringField()
    # profile_photo = db.ImageField()
    # photos = db.ListField(db.ImageField())
    description = db.StringField()
    admin_user = db.ReferenceField(EnterpriseUser)
    member_users = db.ListField(db.ReferenceField(EnterpriseUser))
    state = db.ReferenceField(State)
